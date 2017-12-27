import os
import sys
import time

class Display:
    header = "Interactive interface for AVOSINT"
    titles = "Tail #\t Position\t Heading\t Owner\t Is_hovering\t "
    last_res = []
    def __init__(self):
        self.selected_index = 0
        self.i = 0

        os.system('clear')
        print(Display.header)
        print('Initializing display')
        # TODO: start a thread for interaction and non blocking inputs
        return

    def loading(self):
        os.system('clear')
        print(Display.header + '\t loading planes from area...')
        print(Display.titles)
        for ind, plane in enumerate(Display.last_res):
            selector = ''
            if ind == self.selected_index:
                selector = '<--'
            print(plane)

    def update(self, plane_list):
        upd_chr = ''
        net_chr = ''
        os.system('clear')
        print(Display.header)
        print(Display.titles)
        for ind, plane in enumerate(plane_list):
            selector = ''
            if ind == self.selected_index:
                selector = '<--'
            print(plane)
        Display.last_res = plane_list
        time.sleep(1)
