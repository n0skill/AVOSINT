#!/usr/bin/python3
#n
# ToTest regarding live HLS
#	-> akamai failures might be due to dns load balancing. try resolving using .ch DNS servers? "Service Unavailable - DNS failure"
#   -> akamai gives 403 forbidden on playlists when not proxified. maybe it does also with .ts
#	-> akamai doesn't seem to allow proxifying the .ts files!? "An error occurred while processing your request."
#	-> another explaination could be rapid pruning of the files... that remains to be checked ^^ 
#	https://developer.akamai.com/api/luna/config-media-security/task.html#ct
#   pay attention to country and referer, and possibly hosters IPs are b8nd too...
#   la version flash utilise la verification de player... et 403 on fail

import json, os, subprocess, sys, urllib.request, urllib.parse

from xml.dom import minidom

from bs4 import BeautifulSoup

from tkinter import *
import tkinter.messagebox

	

class GUI(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()
		#self.resizable(TRUE,TRUE)

	def empty(self, b):
		self.id.set("")
	def paste(self, b):
		self.id.set("")
		
	def act(self, b):
		x = fetchId(self.id.get())
		if x == -1:
			tkinter.messagebox.showerror("No match", "No match found. Are you sure it's the page with the player?");
		else:
			step2(x, self)
	def createWidgets(self):
		self.id = StringVar()	

		self.tb = Entry()
		self.tb["textvariable"] = self.id
		self.tb.pack(fill='both',expand = 1)
		self.tb.focus_set()
		self.id.set("Collez l\'adresse d\'une page de video et appuyez sur Enter")
		self.tb.bind('<Key-Return>', self.act)
		self.tb.bind('<Button-1>', self.empty)
		self.tb.bind('<Control-v>', self.paste)
		self.lb = Listbox();
		self.lb.pack(fill='both',expand = 1)
		self.lb.insert(END, 'Les resultats apparaitront ici')





def fetchId(webpage):
	# choper l'id <video data-id=""
	try:
		webpageData = urllib.request.urlopen(webpage).read().decode("utf-8")
		soup = BeautifulSoup(webpageData)
		#print(soup.prettify())
		v = soup.select('video');
		if len(v) < 1:
			return -1
		if len(v) > 1:
			print("Warning, more than a data id on the page. Only the first one will be processed")
		for it in v:
			print(it['data-id'])
		return v[0]['data-id']
	except:
		pass
	try:
		n = int(webpage)
		if n > 0:
			return n
	except:
		pass
	return -1

		
def begingui():
	# demander un copier coller de la page
	# chercher le <video data-id
	_gui = 1
	app = GUI(master=root)
	app.mainloop()
#google: https://www.google.com/?q=intitle:phproxy+site:.ch&gws_rd=cr
def proxify(url):
	return url
	proxyURL = "http://46-127-211-250.dynamic.hispeed.ch/PHProxy/"#dead"http://via.sawd.ch/index.php?q="
	return proxyURL+urllib.parse.quote_plus(url)+"&hl=e1"

def abort(error):
	print(error, file=sys.stderr)
	exit(1)

def fetchMedias(videoId):
	jsonURL = "http://www.tsr.ch/?format=json/video&id=%s" % videoId
	jsonData = urllib.request.urlopen(jsonURL).read().decode("utf-8")
	result = json.loads(jsonData)
	try:
		ptitle = result["video"]["JSONinfo"]["xobix_program_name"]
		print(ptitle)
		vtitle = result["video"]["rawTitle"]
		print(vtitle)
		descr = result["video"]["JSONinfo"]["intro"]
		media = result["video"]["JSONinfo"]["media"]
		media = map(lambda m: m["url"].split("?")[0], media)
		baseURL = result["video"]["JSONinfo"].get("download") # was previously "http://media.tsr.ch/xobix_media/"
	except:
		abort("Media not found")
	
	try:
		tv = result["video"]["JSONinfo"]["streams"]["tv"]
		if tv.startswith(baseURL):
			tv = tv[len(baseURL):]
		media.append(tv)
	except:
		pass 
	
	return (list(media), baseURL, ptitle, vtitle, descr)

def fetchCommand(media, baseURL):
	akastreamingPrefix = "http://akastreaming.tsr.ch/ch/"
	if media.startswith(akastreamingPrefix):
		mediaPath = media[len(akastreamingPrefix):]
		fileName = os.path.splitext(os.path.split(mediaPath)[1])[0] + ".flv"
		tokenURL = proxify("http://www.rts.ch/token/ch-vod.xml?stream=media")
		print(tokenURL)
		try:
			x = (urllib.request.urlopen(tokenURL));
			dom = minidom.parse(urllib.request.urlopen(tokenURL))
			print(x.read(1000))
			print(dom.toprettyxml())
		except:
			abort("Could not get token")
		
		
		hostname = dom.getElementsByTagName("hostname")[0].firstChild.data
		appName = dom.getElementsByTagName("appName")[0].firstChild.data
		authParams = ""
		try:
			authParams = dom.getElementsByTagName("authParams")[0].firstChild.data
		except:
			pass
		return ["rtmpdump", "--protocol", "rtmp", "--host", hostname, "--port", "443", "--app", "%s?ovpfv=2.1.7&%s" % (appName, authParams), "--playpath", "mp4:media/" + mediaPath, "--flashVer", "MAC 10,1,102,64", "--swfUrl", "http://www.tsr.ch/swf/player.swf", "--pageUrl", "http://www.tsr.ch/video/", "--flv", fileName]
	else:
		return ["wget", "--verbose", "-c", "--tries=10", baseURL + media]

def onsel(e):
	i = int(e.widget.curselection()[0])+1 #index must start at 1
	step3(i)

	
def step3(n):
	global media, medias, _gui, app
	try:
		n = int(n)
	except:
		n = len(medias)
		
	media = medias[n - 1]

	print(media)
	print(baseURL)
	command = fetchCommand(media, baseURL)
	#print(command)
	subprocess.call(command)
	fileName = os.path.split(command[-1])[-1]
	#if os.path.splitext(fileName)[1] == ".flv":
	#	subprocess.call(["ffmpeg", "-i", fileName, "-analyzeduration", "2000", "-probesize", "2000", "-vcodec", "copy", "-acodec", "copy", os.path.splitext(fileName)[0] + ".mp4"])
	if _gui == 1:
		tkinter.messagebox.showinfo("Telechargement termine");
	else:
		exit(0)


def step2(id, app):
		global media, medias, _gui, baseURL, pt, vt, intro
		medias, baseURL, pt, vt, intro = fetchMedias(id)
		print(_gui)
		if len(medias) > 1:
			if _gui == 0:
				print(pt, " - ", vt, "\n----\n", intro)
				print("Which media do you want to download?")
			if _gui == 1:
				app.id.set("Quelle version voulez-vous telecharger?")
				app.tb.unbind('<Key-Return>')
			i = 1
			if _gui == 1:
				app.lb.delete(0, END)
				app.lb.bind('<<ListboxSelect>>', onsel)
			for m in medias:
				if _gui == 0:
					print("%u. %s" % (i, os.path.basename(m)))
				else:
					app.lb.insert(END, os.path.basename(m))
				i = i + 1
			if _gui == 0:
				n = input()
				step3(n)
		else:
			media = media[0]		
		
		
		#http://via.sawd.ch/index.php?q=https%3A%2F%2Fsrgssr_uni_9_ch-lh.akamaihd.net%2Fi%2Fenc9uni_ch%40112904%2Findex_100_av-p.m3u8%3Fsd%3D%26rebase%3Don%26id%3DAgBS3CIE1PPSvPZ6X1L8AY27xSJadM2gRV%252fGKeQ%252fgGTChVclQ0RJ%2Bhs%252fJi%252f3zm4nogXoNQs8FqKu6g%253d%253d&hl=e1
def main():
#http://via.sawd.ch/index.php?q=https%3A%2F%2Fsrgssr_uni_9_ch-lh.akamaihd.net%2Fi%2Fenc9uni_ch%40112904%2Fmaster.m3u8&hl=e1
	#print(proxify("https://srgssr_uni_9_ch-lh.akamaihd.net/i/enc9uni_ch@112904/index_100_av-p.m3u8?sd=&rebase=on&id=AgBS3CIE1PPSvPZ6X1L8AY27xSJadM2gRV%2fGKeQ%2fgGTChVclQ0RJ+hs%2fJi%2f3zm4nogXoNQs8FqKu6g%3d%3d"))
	global app, _gui, root
	_gui = (len(sys.argv) != 2)

	if _gui == 1:		
		root = Tk().geometry("640x150+300+300")
		app = GUI(master=root)
		app.mainloop()
	else:
		app = FALSE
		step2(sys.argv[1], 0)

if __name__=='__main__':
	main()
