from libs.geoloc import *
from libs.planes import *

import numpy as np
import argparse
import json
import matplotlib as plt
import os

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument("-daydir", type=str)
    args  = parser.parse_args()
    path = []
    list_of_planes = []
    list_of_files = sorted(os.listdir(args.daydir))
    for filename in list_of_files:
        os.system('clear')
        print('loading planes from file ' + filename)
        with open(args.daydir + '/' + filename, encoding='utf-8') as f:
            try:
                j = json.load(f)
                aviatos_list = j['acList']
                leng = len(aviatos_list)
                for i, aviato in enumerate(aviatos_list):
                    os.sys.stdout.write('\r' + str(i) + '/' + str(leng))
                    webi = aviato.get('Reg')
                    numb = aviato.get('Reg')
                    callsign = aviato.get('Call')
                    latitude = aviato.get('Lat')
                    longitude = aviato.get('Long')

                    if any(plane.numb == numb for plane in list_of_planes):
                        #print('Plane already in list ! Append position to the path')
                        plane.path.append(Coordinates(latitude, longitude))
                    elif numb is not None and latitude is not None:
                        plane = Plane(webi, numb, callsign, latitude, longitude)
                        list_of_planes.append(plane)
                print("")
            except ValueError as e:
                pass


    print('Enter interesting plane to check path')
    plane_numb = input()
    if any(plane.numb == plane_numb for plane in list_of_planes):
        plot.plot(plane.path)
        plt.savefig(plane.numb+'.png')

def printpath_and_classify(array):
    plt.plot(array)
    plt.show()



if __name__ == "__main__":
    main()
