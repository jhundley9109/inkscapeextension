#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2012 Jabiertxo Arraiza, jabier.arraiza@marker.es
# Copyright (C) 2016 su_v, <suv-sf@users.sf.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import sys
sys.path.append('/usr/share/inkscape/extensions')

import re
import math
import inkex
from inkex import Use, TextElement
from lxml import etree


# import inkex
from inkex.base import TempDirMixin
from inkex.command import inkscape_command
from inkex import load_svg



from units import discover_unit, convert_unit, render_unit, parse_unit


GRAPHICS_ELEMENTS = [
    'circle',
    'ellipse',
    'image',
    'line',
    'path',
    'polygon',
    'polyline',
    'rect',
    'text',
    'use',
]

CONTAINER_ELEMENTS = [
    'a',
    'g',
    'switch',
]

class DPISwitcher(inkex.EffectExtension):
    multi_inx = True
    factor_a = 90.0 / 96.0
    factor_b = 96.0 / 90.0
    units = "px"
    # sys.stderr.write("hello from the other size")

    def add_arguments(self, pars):
        # sys.stderr.write("Did we ever make it in here?\n")
        pars.add_argument("--size_select", type=str, default="adult",
                          help="Select the target board size")

    # dictionaries of unit to user unit conversion factors
    __uuconvLegacy = {
        'in': 90.0,
        'pt': 1.25,
        'px': 1.0,
        'mm': 3.5433070866,
        'cm': 35.433070866,
        'm': 3543.3070866,
        'km': 3543307.0866,
        'pc': 15.0,
        'yd': 3240.0,
        'ft': 1080.0,
    }
    __uuconv = {
        'in': 96.0,
        'pt': 1.33333333333,
        'px': 1.0,
        'mm': 3.77952755913,
        'cm': 37.7952755913,
        'm': 3779.52755913,
        'km': 3779527.55913,
        'pc': 16.0,
        'yd': 3456.0,
        'ft': 1152.0,
    }

    def convert_length(self, originalVal, unit):
        """Convert length to self.units if unit differs."""
        """This method takes the units and converts them to the I don't know the use of this acutally"""
        doc_unit = self.units or 'px'
        if unit != doc_unit:
            val_px = originalVal * self.__uuconv[unit]
            val = val_px / (self.__uuconv[doc_unit] / self.__uuconv['px'])

            # print(f'{originalVal} (target unit:{unit}) (current doc unit:{doc_unit}) (number pix:{val_px}) (new val:{val})')
            unit = doc_unit
            return val
        return originalVal

    def convert_to_length_in_px(self, val, unit):
        """Convert from one unit type to another. If the doc is in cm and you want it to inches, it will do the conversion"""
        # doc_unit = self.units or 'px'
        # if unit != doc_unit:

        #     # 2pt -> px -> inches
        #     # 2pt = 1.3333 * 2px = 2.666px
        #     # 2pt = (uuconv[pt] * val) = px
        #     # 2.666px = 2.666 / uuconv[in]

        #     # 72pt -> inches
        #     # 72 * 1.33333333333 = 95.9976px
        #     # valInInches = 95.9976px / 96
            
        #     val_px = val * self.__uuconv["px"]
        #     val = val_px / self.__uuconv[unit]

        # return val

        return val * self.__uuconv[unit]

    def parse_length(self, length, percent=False):
        """Parse SVG length."""
        known_units = list(self.__uuconv)

        if percent:
            unitmatch = re.compile('(%s)$' % '|'.join(known_units + ['%']))
        else:
            unitmatch = re.compile('(%s)$' % '|'.join(known_units))
        param = re.compile(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)')
        p = param.match(length)
        u = unitmatch.search(length)
        val = 100  # fallback: assume default length of 100
        unit = 'px'  # fallback: assume 'px' unit
        if p:
            val = float(p.string[p.start():p.end()])
        if u:
            unit = u.string[u.start():u.end()]
        return val, unit

    def effect(self):
        svg = self.svg

        # inkscape_command(
        #     self.svg,
        #     verbs=['ObjectToPath'],
        # )

        # return
        widthInfo = self.parse_length(svg.get('width'))
        origWidth = widthInfo[0]
        heightInfo = self.parse_length(svg.get('height'))
        origHeight = heightInfo[0]

        self.units = widthInfo[1]

        # widthInInches = self.convert_length(origWidth, 'in')
        # heightInInches = self.convert_length(origHeight, 'in')

        # widthInPx = self.convert_length(origWidth, 'px')
        # heightInPx = self.convert_length(origHeight, 'px')
        widthInPx = convert_unit(svg.get('width'), 'px')
        heightInPx = convert_unit(svg.get('height'), 'px')

        # widthInInches = svg.uutounit(origWidth, 'in')
        # heightInInches = svg.uutounit(origHeight, 'in')

        widthInInches = convert_unit(svg.get('width'), 'in')
        heightInInches = convert_unit(svg.get('height'), 'in')

        # print(f'{widthInInches} {heightInInches}')
        # exit()
        # self.units = 'in'
        # newWidthInPx = self.convert_length(14, 'px')


        # print(f'{svg.unit} {self.units} {widthInInches} {heightInInches} ' + str(svg.unittouu('14in')) + ' ' + str(svg.uutounit('14', 'in')) + ' ' + str(self.convert_length(1400, 'px')) + ' ' + str(self.convert_length(origWidth, 'in')))
        # print(f'{self.units} {14} {newWidthInPx} {newWidthInPx2}')
        # exit()

        if self.options.size_select == "youth":
            targetWidthInches = 10
            targetHeightInches = 12
        elif self.options.size_select == "adult":
            targetWidthInches = 14
            targetHeightInches = 16

        viewbox = svg.get_viewbox()
        thing2 = discover_unit(svg.get('width'), viewbox[2], default='px')

        sys.stderr.write("we in here " + str(origWidth) + " " + str(widthInInches) + " " + svg.get('width') + " " + thing2 + " \n")
        # print(svg.unit + "\n" + str(parse_unit(svg.get('width'))))
        # exit()
        if svg.get('viewBox') == None:
            svg.set('viewBox', "0 0 " + str(origWidth) + " " + str(origHeight))

        # origViewbox = svg.get('viewBox').split(' ')
        origViewbox = svg.get_viewbox()

        # origWidth = float(re.findall(r'\d+', svg.get('width'))[0])
        # origHeight = float(re.findall(r'\d+', svg.get('height'))[0])

        # sys.stderr.write(str(origViewbox) + " " + str(widthInInches) + " " + str(heightInInches) + " " + str(targetWidthInches) + " " + str(targetHeightInches) + "\n")
        # exit()

        svg.set('viewBox', '{} {} {} {}'.format(origViewbox[0], origViewbox[1], (targetWidthInches / widthInInches) * float(origViewbox[2]), (targetHeightInches / heightInInches) * float(origViewbox[3])))

        svg.namedview.set('units', "in")
        svg.namedview.set('inkscape:document-units', "in")
        svg.set('width', str(targetWidthInches) + "in")
        svg.set('height', str(targetHeightInches) + "in")

        # svg.unit = 'in'

        # inkscape:pagecheckerboard="false" />
        svg.namedview.set('inkscape:pagecheckerboard', "true")
        svg.namedview.set('inkscape:window-maximized', "1")

        # self.units = 'in'



        # # sys.stderr.write("Did we ever make it in here?\n" + str(inkex))

        # # inkex.command(svg, 'All', 'AlignHorizontalCenter')
        # centre = svg.view_center   #Put in in the centre of the current view
        # grp_transform = 'translate' + str( centre )
        

        # grp_name = 'Group Name'
        # grp_attribs = {inkex.addNS('label','inkscape'):grp_name,
        #                            'transform':grp_transform }
        
        # sys.stderr.write(str(grp_transform) + " " + str(self) + "\n\n")
        # origWidthInPx = svg.uutounit(origWidth, 'px')
        # origHeightInPx = svg.uutounit(origHeight, 'px')




        # newWidthInPx = self.convert_length(targetWidthInches, 'px')
        newWidthInPx = self.convert_to_length_in_px(targetWidthInches, 'in')
        # newWidthInPx = targetWidthInches * self.__uuconv['in']
        # newHeightInPx = svg.uutounit(origHeight, 'px')

        # diff = newWidthInPx - origWidth
        # translateCalc = diff / 2


        # Old
        # newWidthInPx = svg.uutounit(targetWidthInches, 'px')
        # newWidthInPx = targetWidthInches * self.__uuconv['in']
        # newHeightInPx = svg.uutounit(origHeight, 'px')

        diff = newWidthInPx - widthInPx
        translateCalc = diff / 2

        sys.stderr.write("Did we ever make it in here?\n" + str(origWidth) + " " + str(svg.uutounit(origHeight, 'px')) + " " + str(newWidthInPx) + " diff is : " + str(diff) + " " + str(translateCalc) + "\n " + str(targetWidthInches) + " " + str(newWidthInPx))

        if diff != 0:
            for element in svg:
                tag = element.TAG

                if tag in GRAPHICS_ELEMENTS or tag in CONTAINER_ELEMENTS:
                    element.set('transform', 'translate(' + str(translateCalc) + ')')

        #     sys.stderr.write(str(element.TAG) + " and then " + str(element.attrib) + "\n\n\n")

        # exit()



        # Save this it works
        # Lets try to replace this by just parsing the svg tree and doing the same thing manually
        # self.document = load_svg(inkscape_command(
        #     self.svg,
        #     # verbs=['EditSelectAll', 'EditUnlinkClone', 'ObjectToPath'],
        #     verbs=['EditSelectAll', 'SelectionGroup', 'AlignHorizontalCenter', 'SelectionUnGroup'],
        # ))

        # self.svg = self.document.getroot()
        # svg = self.svg

        # thing = svg.get_selected_bbox()

        # # thing.transform = inkex.Transform("translate(100,100)")

        # # thing = svg.Element('root')
        # # svg.set_selected('layer1')
        # sys.stderr.write(str(self.svg) + "\n")
        # # exit()


        # grp = etree.SubElement(svg, 'g', grp_attribs)#the group to put everything in

    # def affect(self):
    #     sys.stderr.write("poop\n\n")
    #     sys.stderr.write("poop\n\n")
    #     sys.stderr.write("poop\n\n")


if __name__ == '__main__':
    DPISwitcher().run()



# import inkex
# from inkex.base import TempDirMixin
# from inkex.command import inkscape_command
# from inkex import load_svg

# class PreProcess(TempDirMixin, inkex.EffectExtension):
#     def effect(self):
#         self.document = load_svg(inkscape_command(
#             self.svg,
#             verbs=['EditSelectAllInAllLayers', 'EditUnlinkClone', 'ObjectToPath'],
#         ))

# if __name__ == '__main__':
#     PreProcess().run()
