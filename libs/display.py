import os
import sys

class Display:
    def __init__(self):
        self.selected_index = 0
        self.i = 0
        return
    def update(self, plane_list):
        upd_chr = ''
        net_chr = ''
        os.system('clear')
        inp = '' # TODO: non blocking input
        if inp == '\x1b[A':
            self.selected_index = self.selected_index-1
        if inp == '\x1b[B':
            self.selected_index = self.selected_index+1

        print('Interactive interface for plane owners')
        print('▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀')
        print('Flight #\t Position\t Heading\t Owner\t Is_hovering\t ')
        for ind, plane in enumerate(plane_list):
            selector = ''
            if ind == self.selected_index:
                selector = '<--'
            print(str(plane) + selector)
