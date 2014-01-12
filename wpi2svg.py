#!/usr/bin/python

from struct import unpack
from copy import deepcopy
import sys
import argparse
import os.path

def wpi_convert(indata,thick):
    ''' Converts Inkling data to SVG '''
    headertext = ""
    datatext = ""
    endtext = ""
    SVG = ""
    
    add_m = False
    first_run = True
    pen_x_max = -100000
    pen_y_max = -100000
    pen_x_min = 100000
    pen_y_min = 100000
        
    for x in range(0, len(indata)-2):
        header = int(unpack('H', indata[x:x+2])[0])

        if header == 1633: 
            pen_x = int(unpack('>h', indata[x+2:x+4])[0])/2
            pen_y = int(unpack('>h', indata[x+4:x+6])[0])
#
#            pen_pressur and pen_tilt is not used, I have no ide how to convert pressuer or tilt to SVG
#            Data not verified, it culd be wrong endian or in need of some transformation
#
#            pen_pressure = int(unpack('>H', indata[x+10:x+12])[0])
#            pen_tilt = int(unpack('>H', indata[x+14:x+16])[0])
            
            if pen_x > pen_x_max : pen_x_max = deepcopy(pen_x)
            if pen_y > pen_y_max : pen_y_max = deepcopy(pen_y)
            if pen_x < pen_x_min : pen_x_min = deepcopy(pen_x)
            if pen_y < pen_y_min : pen_y_min = deepcopy(pen_y)

            if add_m :
                datatext += 'M'+ str(pen_x) + ',' + str(pen_y) + ','
                add_m = False
            else :
                datatext += 'L'+ str(pen_x) + ',' + str(pen_y) + ','

            x =+ 15
            
        elif header == 1009:
            if int(unpack('B', indata[x+2:x+3])[0]) == 1:
                datatext += '<path d="'
                x =+ 2
                add_m = True
            elif int(unpack('B', indata[x+2:x+3])[0]) == 0:
                if first_run :
                    first_run = False
                else:
                    datatext += '" />\n'
                    x =+ 2
            elif int(unpack('B', indata[x+2:x+3])[0]) == 128:
                #New Layer added, have no ide how to convert it to SVG
                datatext += '<desc>New Layer</desc>\n'
                x =+ 2
        else:
            continue
    
    headertext += '<?xml version="1.0" standalone="no"?>\n'
    headertext += '<svg width="' + str(abs(pen_x_max-pen_x_min)) + '" height="' + str(abs(pen_y_max-pen_y_min)) 
    headertext += '" xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
    headertext += '<title>Converted with wpi2svg</title>\n'

    # Draw a white background
    headertext += '<g fill="#ffffff" fill-opacity="1" stroke="none" transform="matrix(1,0,0,1,' + str(pen_x_min * -1) + ',' + str(pen_y_min * -1) + ')">\n'
    headertext += '<path fill-rule="evenodd" d="M'
    headertext += str(pen_x_min) + ',' + str(pen_y_min)
    headertext += ' L' + str(pen_x_max) + ',' + str(pen_y_min)
    headertext += ' L' + str(pen_x_max) + ',' + str(pen_y_max)
    headertext += ' L' + str(pen_x_min) + ',' + str(pen_y_max)
    headertext += ' L' + str(pen_x_min) + ',' + str(pen_y_min)
    headertext += '"/>\n</g>\n'

    # Start the drawings
    headertext += '<g fill="none" stroke="#000000" stroke-opacity="1" stroke-width="' + str(thick) +'"'
    headertext += ' stroke-linecap="round" stroke-linejoin="bevel" transform="matrix(1,0,0,1,' + str(pen_x_min * -1) + ',' + str(pen_y_min * -1) + ')">\n'

    # Closing at the end
    endtext = '</g>\n</svg>\n'

    # Add everything together
    SVG = headertext + datatext + endtext

    return SVG

if __name__ == "__main__":


    def is_valid_file(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!"%arg)
        else:
            return arg
   
    parser = argparse.ArgumentParser(prog='wpi2svg',description='Convert WACOM Inkling files to SVG')
    parser.add_argument('files', metavar='FILE', type=lambda x: is_valid_file(parser,x), nargs='+', help='WACOM Inkling file')
    parser.add_argument('-t', type=float, help='Thickness of lines (default 5.0)', default=5.0)
    parser.add_argument("-v", "--verbose", action="store_true")
    
    args = vars(parser.parse_args())

    if args['verbose'] : print args

    for filename in args['files'] :
        if args['verbose'] : print 'Converting: ' + str(filename)
        wpifile = open(filename,'r')
        svgfiledata = wpi_convert(wpifile.read(),args['t'])
        wpifile.close()
        svgfile = open(os.path.splitext(filename)[0] + '.svg', 'w')
        svgfile.write(svgfiledata)
        svgfile.close()
 