"""
decmsh.py - decoding *.msh file
Research on Visualization of Unstructed mesh nuetron transportaion program
Name: Zikang Li
ID: 518020910095
Date: 2021
"""

import os
import gmsh
import time
import colorama
from colorama import Fore, Style

class transmsh():

    def __init__(self, mshpath):
        self.fpath, self.msh = os.path.split(mshpath)
        self.xy = r'./xy.dat'
        self.ii = r'./ii.dat'
        self.encoding = 'utf-8'
        os.chdir(self.fpath)
        colorama.init()
        
        self.nodes = []
        self.elements = [] 
        self.elem_typ = []       
        try:
            with open(self.msh, 'r', encoding=self.encoding) as file:
                self.file = file.readlines()
            self._readmsh()
            print(f"File {Fore.GREEN}{self.msh}{Style.RESET_ALL} read succesfully.\n")
            time.sleep(3)
            self._xy()
            print(f"File {Fore.GREEN}{self.xy}{Style.RESET_ALL} written succesfully.\n")
            time.sleep(3)
            self._ii()
            print(f"File {Fore.GREEN}{self.ii}{Style.RESET_ALL} written succesfully.\n")
        except IOError as ioe:
            print(f"{Fore.RED}IOError: {ioe}{Style.RESET_ALL}\n")
        finally:
            print(f"Transmsh Done.\n")
    
    def _readmsh(self):
        # Locker represents the attribution ($Nodes or $Elements) of reading line.
        locker = None
        mshLocker = 0
        for line in self.file:
            # '$' means possible change of control right
            if line[0] == '$':
                if line[0:3] == '$End':
                    locker = None
                elif line == '$Nodes\n':
                    locker = 'nodes'
                elif line == '$Elements\n':
                    locker = 'elements'
            # In $Nodes, only lines with 3 elements represent nodes
            elif locker == 'nodes':
                line = line.split(' ')
                if len(line) == 3:
                    line[2] = line[2].replace('\n', '')
                    node = list(map(float, line))
                    self.nodes.append(node)
            # In $Elements, lines with 4 elements but without mshLocker may give infomation about an entity
            elif locker == 'elements':
                line = line.rstrip().split(' ')
                if mshLocker > 0:
                    line[3] = line[3].replace('\n', '')
                    line.pop(0)
                    elem = list(map(int, line))
                    self.elements.append(elem)
                    self.elem_typ.append(typ)
                    mshLocker -= 1
                elif len(line) == 4:
                    if line[0] == '2':
                        mshLocker = int(line[3].replace('\n', ''))
                        typ = int(line[2])

    def _xy(self):
        # Ansys Format
        title = "\n LIST ALL SELECTED NODES.   DSYS=      0\n SORT TABLE ON  NODE  NODE  NODE\n"
        axis = "\n   NODE        X                   Y                   Z\n"

        with open(self.xy, 'w', encoding=self.encoding) as xy:
            xy.write(title)
            for tag, node in enumerate(self.nodes):
                # Write axis every 20 lines - Ansys Format
                if (tag + 1) % 20 == 1:
                    xy.write(axis)
                
                # nums = [x_coefficient, x_exponent, y_coefficient, y_exponent, z_coefficient, z_exponent]
                nums = []
                for num in node:
                    e = 0
                    if num > 1e-52:
                        while num < 0.1:
                            num *= 10.0
                            e += 1
                    nums.append(num)
                    nums.append('E-{:0>3d}'.format(e) if e > 0 else '')
                # Write nodes - Ansys Format
                xy.writelines("{:>9d}{:>#17.12G}{:<5s}{:>#17.12G}{:<5s}{:>#17.12G}{:<5s}\n".format(tag+1, *nums))

    def _ii(self):
        title = "\n LIST ALL SELECTED ELEMENTS.  (LIST NODES)\n"
        axis = "\n    ELEM MAT TYP REL ESY SEC        NODES\n\n"

        with open(self.ii, 'w', encoding=self.encoding) as ii:
            ii.write(title)
            for tag, elem in enumerate(self.elements):
                # Write axis every 20 lines - Ansys Format
                if (tag + 1) % 20 == 1:
                    ii.write(axis)
                ii.write("{:>8d}{:>4d}{:>4d}{:>4d}{:>4d}{:>4d} {:>6d}{:>6d}{:>6d}{:>6d}\n".format(tag+1, 1, 0, 1, 0, 1, *elem, elem[-1]))

def main():
    mshpath = r"C:\SJTUCoursesDocuments\Nuclear\Research & Innovation\coding\part1_gmsh/t1.msh"
    transmsh(mshpath)

if __name__ == '__main__':
    main()
