import os
import sys
import time

class Display:
    def __init__(self):
        self.selected_index = 0
        self.i = 0
        # TODO: start a thread for interaction and non blocking inputs
        return
    def update(self, plane_list):
        upd_chr = ''
        net_chr = ''
        os.system('clear')


        print('Interactive interface for plane owners')
        print('Flight #\t Position\t Heading\t Owner\t Is_hovering\t ')
        for ind, plane in enumerate(plane_list):
            selector = ''
            if ind == self.selected_index:
                selector = '<--'
            print(str(plane))
        time.sleep(1)
