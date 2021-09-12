"""
iDNTR.py - Pre-processing & Post-processing of DNTR
Research on Visualization of Unstructrued Mesh Nuetron Transportaion Program
Name: Zikang Li
ID: 518020910095
Date: 2021
"""

import os
from sys import argv
from time import time
import colorama
from colorama import Fore, Style
import meshio
import numpy as np

class solver():

    def __init__(self, mshpath):
        startT = time()
        colorama.init()
        print(f"\nPython scipt {Fore.GREEN}DNTR.py{Style.RESET_ALL} is running.\n")
        self.workpath = os.path.split(mshpath)[0]
        self.msh = mshpath
        self.xy = self.workpath + '\\' + r'xy.dat'
        self.ii = self.workpath + '\\' + r'ii.dat'
        self.dntr = self.workpath + '\\' + r'DNTR.exe'
        self.input = self.workpath + '\\' + r'INPUT.DAT'
        self.output = self.workpath + '\\' + r'OUTPUT.DAT'
        self.vtk = self.workpath + '\\' + r'RESULT.vtk'
        self.encoding = 'utf-8'
        
        self.mesh = None
        self.layer = 0
        self.energy_groups = 0
        self.materials = 0
        self.materials_area = []
        self.nodes = []
        self.cells = []
        self.physical_names = []
        self.physical = []
        self.flux = []
        try:
            # Pre-processing: Gmsh *.msh -> DNTR xy.dat & ii.dat
            print(24 * "=" + f" {Style.BRIGHT}Pre-processing{Style.RESET_ALL} " + 24 * "=")
            self.readmsh()
            print(f"File {Fore.GREEN}{self.msh}{Style.RESET_ALL} read succesfully.\n")
            self._xy()
            print(f"File {Fore.GREEN}{self.xy}{Style.RESET_ALL} written succesfully.\n")
            self._ii()
            print(f"File {Fore.GREEN}{self.ii}{Style.RESET_ALL} written succesfully.\n")
            # DNTR
            print(24 * "=" + f" {Style.BRIGHT}DNTR{Style.RESET_ALL} " + 24 * "=")
            self._readinput()
            print(f"File {Fore.GREEN}{self.input}{Style.RESET_ALL} read succesfully.\n")
            print(f"Programme {Fore.GREEN}{self.dntr}{Style.RESET_ALL} is running.\n")
            self._dntr()
            print(f"Programme {Fore.GREEN}{self.dntr}{Style.RESET_ALL} done.\n")
            # Post-processing: DNTR INPUT.DAT & OUTPUT.DAT -> ParaView postDNTR.vtk
            print(24 * "=" + f" {Style.BRIGHT}Post-processing{Style.RESET_ALL} " + 24 * "=")
            self._readoutput()
            print(f"File {Fore.GREEN}{self.output}{Style.RESET_ALL} read succesfully.\n")
            self._vtk()
            print(f"File {Fore.GREEN}{self.vtk}{Style.RESET_ALL} written succesfully.\n")
        except IOError as ioe:
            print(f"{Fore.RED}IOError: {ioe}{Style.RESET_ALL}\n")
        finally:
            endT = time()
            print(f"{Fore.GREEN}iDNTR.py{Style.RESET_ALL} Done.\nTime: {endT-startT} sec\n")

    
    def readmsh(self):
        # Read mesh from mesh.msh by Meshio
        self.mesh = meshio.read(self.msh)

        # Get nodes from Meshio.Mesh.nodes in numpy.ndarray format
        # Meshio.Mesh.nodes = [node1[x1, y1, z1], node2[x2, y2, z2], ...]
        self.nodes = self.mesh.points

        # Get cells from Meshio.Mesh.CellBlock in collections.namedtuple format, see meshio -> _mesh.py -> Class CellBlock
        #   Meshio.Mesh.cells = [cell1(type1, data1), cell2(type2, data3), ...], e.g. [('vertex', [1]), ('triangle', [1 2 3])]
        #   Only cells in type triangle are concerned
        # Get cell_data of each physical groups from Mehsio.Mesh.cell_data['gmsh:physical']
        #   Meshio.Mesh.cell_data = {physical1: [name_cell1, name_cell2, ...], physcial2: [...]}, e.g. {'gmsh:physical': [1 1 2 2 3 3]}
        #   Meshio.Mesh.cell_sets.keys() = [name1, name2, ...], e.g. ['material1', 'material2']
        #   Onlu cell_data in type gmsh:physical are concenrned
        #   cell_data = [cell for cells in self.mesh.cell_data['gmsh:physical'] for cell in cells]
        self.physical_names = list(self.mesh.cell_sets.keys())

        for cell, cell_data in zip(self.mesh.cells, self.mesh.cell_data['gmsh:physical']):
            if cell[0] == 'triangle':
                for triangle, physical in zip(cell[1], cell_data):
                    self.cells.append([num + 1 for num in triangle])
                    self.physical.append(int(self.physical_names[physical-1]))
        print(self.mesh)
    
    
    def readdat(self):
        # Read mesh file from xy.dat & ii.dat.
        # Just for testing, no use in formal release.
        cmap = ['', 'r', 'g', 'b', 'y', 'c', 'm', 'k']
        
        tag = []
        x = []
        y = []
        z = []
        connection = []

        # xy.dat
        with open(self.xy, 'r', encoding='utf-8') as xy:
            for count in range(4):
                xy.readline()
            count = 0
            for line in xy.readlines():
                if count > 0 and count < 21:
                    node = list(map(float, line.split()))
                    tag.append(node[0])
                    x.append(node[1])
                    y.append(node[2])
                    z.append(node[3])
                if count < 21:
                    count += 1
                else:
                    count = 0
        
        with open(self.ii, 'r', encoding='utf-8') as ii:
            for count in range(2):
                ii.readline()
            count = 0
            for line in ii.readlines():
                if count > 2:
                    line = line.split()
                    conn = line[6:9].copy()
                    conn.append(line[2])
                    connection.append(list(map(int, conn)))
                if count < 22:
                    count += 1
                else:
                    count = 0
        
        print(f"nodes:{len(x)} triangles:{len(connection)}")

        # pyplot plot
        try:
            import matplotlib.pyplot as plt
            plt.scatter(x, y)
            for conn in connection:
                plt.plot([x[conn[0]-1], x[conn[1]-1]], [y[conn[0]-1], y[conn[1]-1]], cmap[conn[3]])
                plt.plot([x[conn[0]-1], x[conn[2]-1]], [y[conn[0]-1], y[conn[2]-1]], cmap[conn[3]])
                plt.plot([x[conn[1]-1], x[conn[2]-1]], [y[conn[1]-1], y[conn[2]-1]], cmap[conn[3]])
            plt.show()
        except ImportError:
            print("Can't import matplotlib.pyplot")

    
    def _xy(self):
        # Write nodes in xy.dat in Ansys format.
        title = "\n LIST ALL SELECTED NODES.   DSYS=      0\n SORT TABLE ON  NODE  NODE  NODE\n"
        axis = "\n   NODE        X                   Y                   Z\n"

        with open(self.xy, 'w', encoding=self.encoding) as xy:
            xy.write(title)
            for tag, node in enumerate(self.nodes):
                # Write axis every 20 lines - Ansys Format
                if (tag + 1) % 20 == 1:
                    xy.write(axis)
                
                # Seperate the mantissa and exponent
                # nums = [x_mantissa, x_exponent, y_mantissa, y_exponent, z_mantissa, z_exponent]
                nums = []
                for num in node:
                    e = 0
                    if abs(num) > 1e-52:
                        while abs(num) < 0.1:
                            num *= 10.0
                            e += 1
                    nums.append(num)
                    nums.append('E-{:0>3d}'.format(e) if e > 0 else '')
                # Write nodes - Ansys Format
                xy.writelines("{:>8d}   {:>#15.12G}{:<5s}{:>#15.12G}{:<5s}{:>#15.12G}{:<5s}\n".format(tag+1, *nums))

    
    def _ii(self):
        # Write elements in ii.dat in Ansys format.
        title = "\n LIST ALL SELECTED ELEMENTS.  (LIST NODES)\n"
        axis = "\n    ELEM MAT TYP REL ESY SEC        NODES\n\n"

        with open(self.ii, 'w', encoding=self.encoding) as ii:
            ii.write(title)
            for tag, elem in enumerate(self.cells):
                # Write axis every 20 lines - Ansys Format
                if (tag + 1) % 20 == 1:
                    ii.write(axis)
                ii.write("{:>8d}{:>4d}{:>4d}{:>4d}{:>4d}{:>4d} {:>6d}{:>6d}{:>6d}{:>6d}\n".format(tag+1, 1, self.physical[tag], 1, 0, 1, *elem, elem[-1]))

    
    def _readinput(self):
        # Read infomation from INPUT.dat, but some confuse me a lot.
        with open(self.input, 'r', encoding='utf-8') as input_file:
            # Line 1: File Name
            filename = input_file.readline().rstrip('\n')

            # Line 2: Discretization Conditions
            line = input_file.readline().rstrip('\n').split(',')
            energy_groups = int(line[0])
            self.energy_groups = energy_groups
            layer_num = int(line[3])
            self.layer = layer_num
            materials_num = int(line[4])
            self.materials = materials_num
            segment_num = int(line[-5])

            # Line 3: Convergence criteria
            input_file.readline()
            count = 0
            materials_layer = []
            for line in input_file.readlines():
                line = list(map(eval, line.rstrip('\n').split()))

                # Line 4 -> 3+NA: Materials in every layer
                if count < layer_num:
                    materials_layer.append(line)
                
                # Line 4+NA -> 3+NSP+NA: Index
                elif count < layer_num + segment_num:
                    pass
                
                # Line 4+NSP+NA: Axiel Height
                elif count == layer_num + segment_num:
                    axiel_height = line
                
                # Line 5+NSP+NA: Friction Neutron Shares
                elif count == layer_num + segment_num + 1:
                    friction_shares = line
                count += 1
                # Line Left: Cross Sections of different Materials in different Energy Groups
        
        # Print Information
        print("INPUT.DAT\n File Name: {}\n Energy Groups: {}\n Number of Materials: {}\n Axiel Segment Height: {}\n Friction Neutron Shares: {}\n".format(\
            filename, energy_groups, materials_num, axiel_height, friction_shares))

    
    def _dntr(self):
        # Call the core computation programme DNTR.exe
        # But there is bug to be fixed.
        os.chdir(self.workpath)
        os.system("DNTR.exe")

    
    def _readoutput(self):
        # Read flux distribution from OUTPUT.dat
        # Variable energyLocker counts the 
        dataset = 0
        energyLocker = True
        energyCounter = 0
        materialsLocker = 0

        with open(self.output, 'r', encoding=self.encoding) as fluxfile:
            # Line 1: Eigenvalue and Outer Iteration Times
            line = fluxfile.readline().rstrip('\n').split()
            self.eigenvalue = line[0]
            self.outIteration = line[1]

            # Line 2: Normalization Factor
            self.norm = fluxfile.readline().rstrip('\n').split()[0]

            # Line 3: Normalized Flux in Different Material Area
            for line in fluxfile.readlines(): # readlines() will continue from last-read line to the last line(EOF), it does work:)
                line = line.rstrip('\n').split()
                
                if dataset == 0:
                    if energyLocker:
                        self.flux.append([])
                        line.pop(0)
                        materialsLocker = 0
                        energyLocker = False
                        energyCounter += 1
                    if not energyLocker and materialsLocker < self.materials:
                        line = list(map(float, line))
                        for flux in line:
                            self.flux[energyCounter-1].append(flux)
                        materialsLocker += len(line)
                    if materialsLocker == self.materials:
                        energyLocker = True
                        if energyCounter == self.energy_groups:
                            materialsLocker = 0
                            dataset += 1
                
                elif dataset == 1:
                    line = list(map(float, line))
                    for area in line:
                        self.materials_area.append(area)
                    materialsLocker += len(line)
                    if materialsLocker == self.materials:
                        dataset += 1
                
                elif dataset == 2:
                    print("OUTPUT.DAT\n DNTR CPU Time: {}\n Netron Flux Distribution:".format(line[-1]))
                    for ng in range(self.energy_groups):
                        print("  NG {}: {}".format(ng+1, self.flux[ng]))

    
    def _vtk(self):
        # Write mesh and flux distribution (in cell_data form) into vtk file
        self.mesh = meshio.read(self.msh)
        cell_data = self.mesh.cell_data.copy()

        # Iterate energy groups
        for ng in range(self.energy_groups):
            name = 'DNTR:Flux_group_' + str(ng + 1)
            # Add flux in all materials' zone in every energy group
            flux_ng = []
            
            for cell, physical in zip(self.mesh.cells, self.mesh.cell_data['gmsh:physical']):
                if cell[0] == 'triangle':
                    material_zone = int(self.physical_names[physical[0]-1])
                    flux = self.flux[ng][material_zone]
                    flux_ng.append(np.array([np.array([0, 0, flux]) for i in range(len(physical))], dtype=np.float))
                else:
                    flux_ng.append(np.array([np.array([0, 0, 0]) for i in range(len(physical))], dtype=np.float))
            
            cell_data[name] = flux_ng

        meshio.write_points_cells(self.vtk, self.mesh.points, self.mesh.cells, cell_data=cell_data, file_format="vtk", binary=False)


def main():
    # Command in cmd.exe: "python iDNTR.py -i C:\yourPath\yourMesh.msh"
    # Then this script will run in C:\yourPath.
    # Otherwise, default mshpath will be used.
    args = argv
    mshpath = r"C:\your_Path\mesh.msh"
    if len(args) > 1 and args[1] == '-i':
        mshpath = args[2]
    solver(mshpath)

if __name__ == '__main__':
    main()
