#!/usr/bin/env python

"""
Script that takes a stacked Sentinel 2 image and runs
fmask on it.
"""
# This file is part of 'python-fmask' - a cloud masking module
# Copyright (C) 2015  Neil Flood
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from __future__ import print_function, division

import sys
import optparse
from xml.dom import minidom
from fmask import fmask
from fmask import config

class CmdArgs(object):
    """
    Class for processing command line arguments
    """
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option('-a', '--toa', dest='toa',
            help='Input stack of TOA reflectance (as supplied by ESA)')
        self.parser.add_option('-o', '--output', dest='output',
            help='output cloud mask')
        self.parser.add_option('-x', '--xml', dest='xml',
            help='.xml file supplied with the granule')
        self.parser.add_option('-v', '--verbose', dest='verbose', default=False,
            action='store_true', help='verbose output')
        self.parser.add_option('-k', '--keepintermediates', dest='keepintermediates', 
            default=False, action='store_true', help='verbose output')
            
        (options, self.args) = self.parser.parse_args()
        self.__dict__.update(options.__dict__)
        
        if self.output is None or self.toa is None or self.xml is None:
            self.parser.print_help()
            sys.exit(1)
            
def getMeanSunAngles(xmlFile):
    """
    Just gets the mean sun angles for an image from the .xml file.
    Ideally this would do something with the regular grid of such
    values instead.
    
    """
    xmldoc = minidom.parse(xmlFile)
    itemList = xmldoc.getElementsByTagName('Mean_Sun_Angle')
    zenList = itemList[0].getElementsByTagName('ZENITH_ANGLE')
    zenith = float(zenList[0].firstChild.data)
    aziList = itemList[0].getElementsByTagName('AZIMUTH_ANGLE')
    azimuth = float(aziList[0].firstChild.data)
    return config.AngleConstantInfo(zenith, azimuth, 0, 0)
            
def mainRoutine():
    """
    Main routine that calls fmask
    """
    cmdargs = CmdArgs()
    
    anglesInfo = getMeanSunAngles(cmdargs.xml)
    
    fmaskFilenames = config.FmaskFilenames()
    fmaskFilenames.setTOAReflectanceFile(cmdargs.toa)
    fmaskFilenames.setOutputCloudMaskFile(cmdargs.output)
    
    fmaskConfig = config.FmaskConfig(config.FMASK_SENTINEL2)
    fmaskConfig.setAnglesInfo(anglesInfo)
    fmaskConfig.setKeepIntermediates(cmdargs.keepintermediates)
    fmaskConfig.setVerbose(cmdargs.verbose)
    
    fmask.doFmask(fmaskFilenames, fmaskConfig)
    
if __name__ == '__main__':
    mainRoutine()
