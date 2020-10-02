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
# from inkex import Use, TextElement
from lxml import etree


# import inkex
# from inkex.base import TempDirMixin
# from inkex.command import inkscape_command
# from inkex import load_svg


# from units import discover_unit, convert_unit, render_unit, parse_unit
from inkex.units import discover_unit, convert_unit, render_unit, parse_unit

import inkex
from inkex import Group

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

class ArtboardAdjuster(inkex.EffectExtension):

    def add_arguments(self, pars):
        # sys.stderr.write("Did we ever make it in here?\n")
        pars.add_argument("--size_select", type=str, default='',
                          help="Select the target board size")

        pars.add_argument("--toggle_unit_to_inches", type=bool, default=False,
                          help="Switch between inches and pixels as the document units")

    # dictionaries of unit to user unit conversion factors
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

    def remove_all_existing_guides(self):
        for guide in self.svg.namedview.get_guides():
            guide.delete()

    def set_guide_at_position(self, guideLocation, isHorizontal=False):
        svg = self.svg
        newViewbox = svg.get_viewbox()

        if isHorizontal:
            targetDimension = self.parse_length(svg.get('height'))[0]
            viewBoxDimension = newViewbox[3]
        else:
            targetDimension = self.parse_length(svg.get('width'))[0]
            viewBoxDimension = newViewbox[2]

        factor = (1 / targetDimension) * (targetDimension - guideLocation)
        guidePosition = viewBoxDimension * factor

        svg.namedview.new_guide(guidePosition, isHorizontal)

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

        if svg.get('width') == None:
            viewbox = svg.get_viewbox()
            svg.set('width', str(viewbox[2]))
            svg.set('height', str(viewbox[3]))

        widthInfo = self.parse_length(svg.get('width'))
        origWidth = widthInfo[0]
        heightInfo = self.parse_length(svg.get('height'))
        origHeight = heightInfo[0]

        # unittouu == desired units to document units. This calculates in the DPI for the document
        # uutounit == user units to desired units with regards to DPI. Inkscape and pretty much everything else uses 96 DPI but illustrator does everything in 72 DPI because adobe is dumb.
        originalWidthInPx = svg.unittouu(svg.get('width'))

        widthInInches = svg.uutounit(svg.get('width'), 'in')
        heightInInches = svg.uutounit(svg.get('height'), 'in')

        documentDPI = svg.unittouu("1in")

        if self.options.toggle_unit_to_inches or self.options.size_select == '':
            targetWidthInches = widthInInches
            targetHeightInches = heightInInches
        else:
            if self.options.size_select == "youth":
                targetWidthInches = 10
                targetHeightInches = 12
            elif self.options.size_select == "adult":
                targetWidthInches = 14
                targetHeightInches = 16
            elif self.options.size_select == "infant":
                targetWidthInches = 7
                targetHeightInches = 8
            elif self.options.size_select == "exlarge":
                targetWidthInches = 16
                targetHeightInches = 18

        # viewbox = svg.get_viewbox()
        # thing2 = discover_unit(svg.get('width'), viewbox[2], default='px')

        if svg.get('viewBox') == None:
            svg.set('viewBox', "0 0 " + str(origWidth) + " " + str(origHeight))

        origViewbox = svg.get_viewbox()

        svg.set('viewBox', '{} {} {} {}'.format(origViewbox[0], origViewbox[1], (targetWidthInches / widthInInches) * float(origViewbox[2]), (targetHeightInches / heightInInches) * float(origViewbox[3])))

        svg.namedview.set('units', "in")
        svg.namedview.set('inkscape:document-units', "in")
        svg.set('width', str(targetWidthInches) + "in")
        svg.set('height', str(targetHeightInches) + "in")

        # svg.namedview.set('inkscape:cx', '218.85925')
        # svg.namedview.set('inkscape:cy', '114.95549')
        # svg.namedview.set('inkscape:zoom', '0.5')

        if self.options.toggle_unit_to_inches or self.options.size_select == '':
            return None

        svg.namedview.set('pagecolor', "#abd7de")
        svg.namedview.set('inkscape:pagecheckerboard', "true")
        svg.namedview.set('inkscape:window-maximized', "1")

        # Set the guides at 1, 2, 3 inches and half board horizontally, and half board vertically
        self.remove_all_existing_guides()
        self.set_guide_at_position(1, True)
        self.set_guide_at_position(2, True)
        self.set_guide_at_position(3, True)
        self.set_guide_at_position(targetHeightInches / 2, True)
        self.set_guide_at_position(targetWidthInches / 2, False)

        newWidthInPx = svg.unittouu(str(targetWidthInches) + "in")

        diff = newWidthInPx - originalWidthInPx
        translateCalc = diff / 2

        # sys.stderr.write("Did we ever make it in here?\nDocument DPI is: " + str(documentDPI) + " " + str(widthInInches) + " " + str(origWidth) + " " + str(targetWidthInches) + " " + str(originalWidthInPx) + " New width in px: " + str(newWidthInPx) + " " + str(translateCalc));

        elementsToGroup = []

        for element in svg:
            tag = element.TAG

            if tag in GRAPHICS_ELEMENTS or tag in CONTAINER_ELEMENTS:
                # sys.stderr.write(str(element.get('transform')) + " " + str(translateCalc))
                # existtingTransform = element.get('transform')

                # This is a bit of a workaround because I don't know how to do a translate operation on an element that already.
                # So what I do is I take any element that already has transform matrix, remove it from the svg, push it onto a group, and add all those elements back onto the svg
                # if existtingTransform != None and re.search("matrix", existtingTransform):
                    # sys.stderr.write(str(existtingTransform))

                elementsToGroup.append(element)
                svg.remove(element)

        if len(elementsToGroup) > 0:
            group = Group()

            for element in elementsToGroup:
                group.append(element)

            self.svg.append(group)


        for element in svg:
            tag = element.TAG

            if tag in GRAPHICS_ELEMENTS or tag in CONTAINER_ELEMENTS:

                element.transform.add_translate(translateCalc)


if __name__ == '__main__':
    ArtboardAdjuster().run()



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
