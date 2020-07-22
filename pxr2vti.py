'''

pxr2vti.py

Script converts .pxr binary files into .vtk files, to be read e.g.
with paraview. The script should be located in 'picsar/utils/postprocessing
and the .pxr files should be contained in 'picsar/fortran_bin/RESULTS'.
For the command line options run the script with the -h option.
The script runs both with python version 2 and 3.

Developer:
Mike Wilbert 

Date:
July 2020

'''

import numpy as np
from matplotlib import pyplot as plt
from Field import *
import sys
import struct
import glob
import os
from optparse import OptionParser

SIZEOF_INT   = 4
SIZEOF_FLOAT = 4

def conv2vti(filename, data_dir, vti_dir, field_name):
	
	file_path = data_dir + filename
	field_name_pxr = filename[:-4]
	out_filename = vti_dir + "/" + field_name_pxr + ".vti"
	print("\tConverting field " + field_name_pxr)
	
	# read field information
	field_read = Field(file_path)

	field = field_read.f.astype(np.float32)

	nx = field_read.nx
	ny = field_read.ny
	nz = field_read.nz
	n_tot = nx*ny*nz

	# header
	with open(out_filename, 'w') as out_writer:
			
			out_writer.write("<VTKFile type=\"ImageData\" version=\"0.1\" byte_order=\"LittleEndian\">\n")
			out_writer.write('<ImageData WholeExtent="0 %d 0 %d 0 %d" ' %(nx,ny,nz) )
			out_writer.write('Origin="0 0 0" Spacing="1 1 1">\n' )
			out_writer.write('<Piece Extent="0 %d 0 %d 0 %d">\n' %(nx,ny,nz) )
			out_writer.write('<CellData>\n')
			out_writer.write('<DataArray type=\"Float32\" Name="%s" NumberOfComponents="1" format="appended" offset="%d"/>\n' %(field_name, 0))
			out_writer.write('</CellData>\n')
			out_writer.write('<PointData/>\n')
			out_writer.write('</Piece>\n')
			out_writer.write('</ImageData>\n')
			out_writer.write('<AppendedData encoding="raw">\n')
			out_writer.write('_')
			
	# binary data
	with open(out_filename, 'ab') as out_binary:
		N = n_tot*SIZEOF_FLOAT
		
		out_binary.write((N).to_bytes(SIZEOF_INT, byteorder='little', signed=True)) # only python3
		# ~ out_binary.write(bytearray(struct.pack("i", N)))
			
		for ix in range(nx):
			for iy in range(ny):
				for iz in range(nz):
					out_binary.write(bytearray(struct.pack("f", field[ix,iy,iz])))
		
	# footer		
	with open(out_filename, 'a') as out_writer:		
		out_writer.write('</AppendedData>')
		out_writer.write('</VTKFile>')

# read command line options
parser = OptionParser()
help_string = "Options: Name the field ou want to convert (e.g. rho).\n'all': Convert all fields. 'show': show all possible fields to be converted."
parser.add_option("-f", "--field", action="store", dest="field_name", help=help_string)

(options,args) = parser.parse_args()

field_name = options.field_name
if(field_name==None):
	print("\tPlease name the field you'd like to convert!\n")
	print("\t-f FILE_NAME")
	print("\tHelp : -h")
	exit()

# define directory names
main_dir = os.getcwd()
data_dir = "../../fortran_bin/RESULTS/"
vti_dir = "vti_data"

# get all field names
os.chdir(data_dir)
if(field_name == "all" or field_name == "show"):
	field_names = glob.glob("*.pxr")
else:
	field_names = glob.glob("*" + field_name + "*.pxr")
os.chdir(main_dir)

if(field_names == []):
	print("\tGiven field name does not match any .pxr file!")
	exit()
	
if(field_name == "show"):
	print("\tPossible fields to be converted:")
	print("\t" + field_names)
	exit()

print("\tFields to be converted:")
print(field_names)
print("\tTotal number of fields to convert:" , len(field_names))
print("")

# create data directory if not already existing
if(len(glob.glob(vti_dir)) == 0):
	print("\tcreating directory for vti files:", vti_dir)
	os.mkdir(vti_dir)

# convert to vti
for name in field_names:
	conv2vti(name, data_dir, vti_dir, field_name)




