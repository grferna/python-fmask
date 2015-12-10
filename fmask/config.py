"""
Configuration classes that define the inputs and parameters
for the fmask function.
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

import abc
import numpy
import scipy.constants

from osgeo import gdal
from rios import applier
from . import fmaskerrors

"Landsat 4 to 7"
FMASK_LANDSAT47 = 0
"Landsat 8"
FMASK_LANDSAT8 = 1
"Sentinel 2"
FMASK_SENTINEL2 = 2

"""
Some constants for the various reflective bands used in fmask.
~45um
"""
BAND_BLUE = 0
"~52um"
BAND_GREEN = 1
"~63um"
BAND_RED = 2
"~76um"
BAND_NIR = 3
"~136um"
BAND_CIRRUS = 4 # Sentinel2 + Landsat8 only
"~155um"
BAND_SWIR1 = 5
"~208um"
BAND_SWIR2 = 6

class FmaskConfig(object):
    """
    Class that contains the configuration parameters of the fmask
    run.
    """
    def __init__(self, sensor):
        """
        Pass in the sensor (one of: FMASK_LANDSAT47, FMASK_LANDSAT8 or
        FMASK_SENTINEL2) and default of parameters will be set. These 
        can be overridden using the functions on this object.
        """
        self.sensor = sensor
        
        # Some standard file configurations for different sensors.
        # Assumed that panchromatic + thermal bands stored in separate files.
        if sensor == FMASK_LANDSAT47:
            self.bands = {BAND_BLUE:0, BAND_GREEN:1, BAND_RED:2, BAND_NIR:3,
                        BAND_SWIR1:4, BAND_SWIR2:5}
        elif sensor == FMASK_LANDSAT8:
            self.bands = {BAND_BLUE:1, BAND_GREEN:2, BAND_RED:3, BAND_NIR:4,
                BAND_SWIR1:5, BAND_SWIR2:6, BAND_CIRRUS:7}
        elif sensor == FMASK_SENTINEL2:
            self.bands = {BAND_BLUE:1, BAND_GREEN:2, BAND_RED:3, BAND_NIR:6,
                    BAND_SWIR1:10, BAND_SWIR2:11, BAND_CIRRUS:9}
        else:
            msg = 'unrecognised sensor'
            raise fmaskerrors.FmaskParameterError(msg)

        # we can't do anything with the thermal yet since
        # we need a .mtl file or equivalent to get the gains etc
        self.thermalInfo = None
        
        # same with angles
        self.anglesInfo = None
        
        # obtain the usual extension for the GDAL driver used by RIOS
        # so we can create temporary files with this extension.
        driver = gdal.GetDriverByName(applier.DEFAULTDRIVERNAME)
        if driver is None:
            msg = 'Cannot find GDAL driver %s used by RIOS' 
            msg = msg % applier.DEFAULTDRIVERNAME
            raise fmaskerrors.FmaskParameterError(msg)

        ext = driver.GetMetadataItem('DMD_EXTENSION')
        if ext is None:
            self.defaultExtension = '.tmp'
        else:
            self.defaultExtension = '.' + ext
        
        # some parameters for fmask operation
        self.keepIntermediates = False
        self.cloudBufferSize = 5
        self.shadowBufferSize = 10
        self.verbose = False
        self.strictFmask = False
        self.tempDir = '.'
    
    def setReflectiveBand(self, band, index):
        """
        Tell fmask which band is in which index in the reflectance
        data stack file. band should be one of the BAND_* constants.
        index is zero based (ie 0 is first band in the file).
        
        These are set to default values for each sensor which are
        normally correct, but this function can be used to update.
        
        """
        self.bands[band] = index
        
    def setThermalInfo(self, info):
        """
        Set an instance of ThermalFileInfo. By default this is
        None and fmask assumes there is no thermal data available.
        
        The :func:`fmask.config.readThermalInfoFromLandsatMTL`
        function can be used to obtain this from a Landsat .mtl file.
        
        """
        self.thermalInfo = info
        
    def setAnglesInfo(self, info):
        """
        Set an instance of AnglesInfo. By default this is 
        None and will need to be set before fmask will run.
        
        The :func:`fmask.config.readAnglesFromLandsatMTL` 
        function can be used to obtain this from a Landsat .mtl file.

        """
        self.anglesInfo = info

    def setKeepIntermediates(self, keepIntermediates):
        """
        Set to True to keep the intermediate files created in
        processed. This is False by default.
        
        """
        self.keepIntermediates = keepIntermediates
    
    def setCloudBufferSize(self, bufferSize):
        """
        Extra buffer of this many pixels on cloud layer. Defaults to 5.
        
        """
        self.cloudBufferSize = bufferSize

    def setShadowBufferSize(self, bufferSize):
        """
        Extra buffer of this many pixels on cloud layer. Defaults to 10.
        
        """
        self.shadowBufferSize = bufferSize
        
    def setVerbose(self, verbose):
        """
        Print informative messages. Defaults to False.
        
        """
        self.verbose = verbose
        
    def setStrictFmask(self, strictFmask):
        """
        Set whatever options are necessary to run strictly as per Fmask paper 
        (Zhu & Woodcock). Setting this will override the settings of other
        parameters on this object.
    
        """
        self.strictFmask = strictFmask
        
    def setTempDir(self, tempDir):
        """
        Temporary directory to use. Defaults to '.' (the current directory).
        
        """
        self.tempDir = tempDir
        
    def setDefaultExtension(self, extension):
        """
        Sets the default extension used by temporary files created by
        fmask. Defaults to the extension of the driver that RIOS
        is configured to use.
        
        Note that this should include the '.' - ie '.img'.
        
        """
        self.defaultExtension = extension

class FmaskFilenames(object):
    """
    Class that contains the filenames used in the fmask run.
    """
    def __init__(self, toaRefFile=None, thermalFile=None, outputMask=None,
                saturationMask=None):
        self.toaRef = toaRefFile
        self.thermal = thermalFile
        self.saturationMask = saturationMask
        self.outputMask = outputMask
    
    def setThermalFile(self, thermalFile):
        """
        Set the path of the input thermal file. To make use
        of this, the :func:`fmask.config.FmaskConfig.setThermalInfo`
        function must also be called so that fmask knows how
        to use the file.
        
        This file should be in any GDAL readable format.
        
        """
        self.thermal = thermalFile
    
    def setTOAReflectanceFile(self, toaRefFile):
        """
        Set the path of the input top of atmosphere (TOA) file. It pays
        to check that the default set of bands match what fmask expects in 
        the :class:`fmask.config.FmaskConfig` class and update if necessary.
        
        This should have numbers which are reflectance * 1000
        
        Use the :func:`fmask.landsatTOA.makeTOAReflectance` function to create
        this file from raw Landsat radiance (or the fmask_usgsLandsatTOA.py
        command line program supplied with fmask).
        
        It is assumed that any values that are nulls in the original radiance
        image are set to the ignore values in the toaRefFile.

        This file should be in any GDAL readable format.
        
        """
        self.toaRef = toaRefFile
    
    def setSaturationMask(self, mask):
        """
        Set the mask to use for ignoring saturated pixels. By default
        no mask is used and all pixels are assumed to be unsaturated.
        This will cause problems for the whiteness test if some pixels
        are in fact saturated, but not masked out.
        
        Use the :func:`fmask.saturation.makeSaturationMask` function to
        create this from input radiance data.
        
        This mask should be 1 for pixels that are saturated, 0 otherwise.
        
        Note that this is not in the original paper so cannot be considered
        'strict', but if provided is used no matter the strict setting in 
        :class:`fmask.config.FmaskConfig`.

        This file should be in any GDAL readable format.
        
        """
        self.saturationMask = mask
    
    def setOutputCloudMaskFile(self, cloudMask):
        """
        Set the output cloud mask path. 
        
        Note that this file will be written in the format
        that RIOS is currently configured to use. See the 
        `RIOS documentation <http://rioshome.org/rios_imagewriter.html#rios.imagewriter.setDefaultDriver>`_
        for more details. Note that the default is HFA (.img) and can
        be overridden using environment variables.
        
        """
        self.outputMask = cloudMask


class ThermalFileInfo(object):
    """
    Contains parameters for interpreting thermal file.
    See :func:`fmask.config.readThermalInfoFromLandsatMTL`.
    
    """
    thermalBand1040um = None
    thermalGain1040um = None
    thermalOffset1040um = None
    thermalK1_1040um = None
    thermalK2_1040um = None
    
    def __init__(self, thermalBand1040um, thermalGain1040um,
            thermalOffset1040um, thermalK1_1040um, thermalK2_1040um):
        self.thermalBand1040um = thermalBand1040um
        self.thermalGain1040um = thermalGain1040um
        self.thermalOffset1040um = thermalOffset1040um
        self.thermalK1_1040um = thermalK1_1040um
        self.thermalK2_1040um = thermalK2_1040um

    def scaleThermalDNtoC(self, scaledBT):
        """
        Use the given params to unscale the thermal, and then 
        convert it from K to C. Return a single 2-d array of the 
        temperature in deg C. 
        """
        KELVIN_ZERO_DEGC = scipy.constants.zero_Celsius
        rad = (scaledBT[self.thermalBand1040um].astype(float) * 
                    self.thermalGain1040um + self.thermalOffset1040um)
        # see http://www.yale.edu/ceo/Documentation/Landsat_DN_to_Kelvin.pdf
        # and https://landsat.usgs.gov/Landsat8_Using_Product.php
        rad[rad <= 0] = 0.00001 # to stop errors below
        temp = self.thermalK2_1040um / numpy.log(self.thermalK1_1040um / rad + 1.0)
        bt = temp - KELVIN_ZERO_DEGC
        return bt

"Keys within a .mtl file for each band"
LANDSAT_RADIANCE_MULT = 'RADIANCE_MULT_BAND_%s'
LANDSAT_RADIANCE_ADD = 'RADIANCE_ADD_BAND_%s'
LANDSAT_K1_CONST = 'K1_CONSTANT_BAND_%s'
LANDSAT_K2_CONST = 'K2_CONSTANT_BAND_%s'

"band numbers in mtl file for gain and offset for thermal"
LANDSAT_TH_BAND_NUM_DICT = {'LANDSAT_4' : '6', 
        'LANDSAT_5' : '6',
        'LANDSAT_7' : '6_VCID_1',
        'LANDSAT_8' : '10'}
                        
"""
for some reason L4, 5, and 7 don't
have these numbers in the mtl file, but L8 does
from http://www.yale.edu/ceo/Documentation/Landsat_DN_to_Kelvin.pdf
"""
LANDSAT_K1_DICT = {'TM' : 607.76, 'ETM' : 666.09}
LANDSAT_K2_DICT = {'TM' : 1260.56, 'ETM' : 1282.71}
        
def readThermalInfoFromLandsatMTL(mtlfile, thermalBand1040um=0):
    """
    Returns an instance of ThermalFileInfo given a path to the mtl
    file and the index of the thermal band.
    
    """
    mtlData = readMTLFile(mtlfile)
    gain = None
    offset = None
    k1 = None
    k2 = None
    if 'SPACECRAFT_ID' in mtlData:
        # we can now grab the gain and offset
        spaceCraft = mtlData['SPACECRAFT_ID']
        band = LANDSAT_TH_BAND_NUM_DICT[spaceCraft]
        
        s = LANDSAT_RADIANCE_MULT % band
        gain = float(mtlData[s])
            
        s = LANDSAT_RADIANCE_ADD % band
        offset = float(mtlData[s])
        
    if 'SENSOR_ID' in mtlData:
        # look for k1 and k2
        sensor = mtlData['SENSOR_ID']
        s = LANDSAT_K1_CONST % band
        if s in mtlData:
            k1 = float(mtlData[s])
        else:
            # drop back to our own values if not in file
            k1 = LANDSAT_K1_DICT[sensor]
                                    
        s = LANDSAT_K2_CONST % band
        if s in mtlData:
            k2 = float(mtlData[s])
        else:
            # drop back to our own values if not in file
            k2 = LANDSAT_K1_DICT[sensor]
            
    if gain is not None and offset is not None and k1 is not None and k2 is not None:
        thermalInfo = ThermalFileInfo(thermalBand1040um, gain, 
                        offset, k1, k2)
    else:
        msg = 'Cannot find SPACECRAFT_ID/SENSOR_ID in MTL file'
        raise fmaskerrors.FmaskFileError(msg)
        
    return thermalInfo
            
class AnglesInfo(object):
    """
    Abstract base class that Contains view and solar angle 
    information for file (in radians).
    
    """
    __metaclass__ = abc.ABCMeta
    
    def prepareForQuerying(self):
        """
        Called when fmask is about to query this object for angles.
        Derived class should do any reading of files into memory required here.
        """
        
    def releaseMemory(self):
        """
        Called when fmask has finished querying this object.
        Can release any allocated memory.
        """
    
    @abc.abstractmethod
    def getSolarZenithAngle(self, indices):
        """
        Return the average solar zenith angle for the given indices
        """

    @abc.abstractmethod
    def getSolarAzimuthAngle(self, indices):
        """
        Return the average solar azimuth angle for the given indices
        """
    
    @abc.abstractmethod
    def getViewZenithAngle(self, indices):
        """
        Return the average view zenith angle for the given indices
        """

    @abc.abstractmethod
    def getViewAzimuthAngle(self, indices):
        """
        Return the average view azimuth angle for the given indices
        """
    
class AnglesFileInfo(AnglesInfo):
    """
    An implementation of AnglesInfo that reads the information from
    GDAL supported files.
    """
    def __init__(self, solarZenithFilename, solarZenithBand, solarAzimuthFilename,
            solarAzimuthBand, viewZenithFilename, viewZenithBand, 
            viewAzimuthFilename, viewAzimuthBand):
        """
        Initialises the object with the names and band numbers of the angles.
        band numbers should be 0 based - ie first band is 0.
        """
        self.solarZenithFilename = solarZenithFilename
        self.solarZenithBand = solarZenithBand
        self.solarAzimuthFilename = solarAzimuthFilename
        self.solarAzimuthBand = solarAzimuthBand
        self.viewZenithFilename = viewZenithFilename
        self.viewZenithBand = viewZenithBand
        self.viewAzimuthFilename = viewAzimuthFilename
        self.viewAzimuthBand = viewAzimuthBand
        # these will contain the actual image data once read
        # by prepareForQuerying()
        self.solarZenithData = None
        self.solarAzimuthData = None
        self.viewZenithData = None
        self.viewAzimuthData = None
    
    @staticmethod
    def readData(filename, bandNum):
        ds = gdal.Open(filename)
        band = ds.GetRasterBand(bandNum + 1)
        data = band.ReadAsArray()
        del ds
        return data
    
    def prepareForQuerying(self):
        """
        Called when fmask is about to query this object for angles.
        """
        self.solarZenithData = self.readData(self.solarZenithFilename, 
                                self.solarZenithFilename)
        self.solarAzimuthData = self.readData(self.solarAzimuthFilename, 
                                self.solarAzimuthFilename)
        self.viewZenithData = self.readData(self.viewZenithFilename, 
                                self.viewZenithFilename)
        self.viewAzimuthData = self.readData(self.viewAzimuthFilename, 
                                self.viewAzimuthFilename)
        
    def releaseMemory(self):
        """
        Called when fmask has finished querying this object.
        """
        del self.solarZenithData
        del self.solarAzimuthData
        del self.viewZenithData
        del self.viewAzimuthData
    
    def getSolarZenithAngle(self, indices):
        """
        Return the average solar zenith angle for the given indices
        """
        return self.solarZenithData[indices].mean()

    def getSolarAzimuthAngle(self, indices):
        """
        Return the average solar azimuth angle for the given indices
        """
        return self.solarAzimuthData[indices].mean()
    
    def getViewZenithAngle(self, indices):
        """
        Return the average view zenith angle for the given indices
        """
        return self.viewZenithData[indices].mean()

    def getViewAzimuthAngle(self, indices):
        """
        Return the average view azimuth angle for the given indices
        """
        return self.viewAzimuthData[indices].mean()

class AngleConstantInfo(AnglesInfo):
    """
    An implementation of AnglesInfo that uses constant
    angles accross the scene. 
    """
    def __init__(self, solarZenithAngle, solarAzimuthAngle, viewZenithAngle,
                    viewAzimuthAngle):
        self.solarZenithAngle = solarZenithAngle
        self.solarAzimuthAngle = solarAzimuthAngle
        self.viewZenithAngle = viewZenithAngle
        self.viewAzimuthAngle = viewAzimuthAngle

    def getSolarZenithAngle(self, indices):
        """
        Return the solar zenith angle
        """
        return self.solarZenithAngle

    def getSolarAzimuthAngle(self, indices):
        """
        Return the solar azimuth angle
        """
        return self.solarAzimuthAngle
    
    def getViewZenithAngle(self, indices):
        """
        Return the view zenith angle
        """
        return self.viewZenithAngle

    def getViewAzimuthAngle(self, indices):
        """
        Return the view azimuth angle
        """
        return self.viewAzimuthAngle

def readMTLFile(mtl):
    """
    Very simple .mtl file reader that just creates a dictionary
    of key and values and returns it
    """
    dict = {}
    for line in open(mtl):
        arr = line.split('=')
        if len(arr) == 2:
            (key, value) = arr
            dict[key.strip()] = value.replace('"', '').strip()
                                                                
    return dict
                                                                    

def readAnglesFromLandsatMTL(mtlfile):
    """
    Given the path to a Landsat USGS .MTL file, read the angles
    out and return an instance of AngleConstantInfo.
    
    """
    mtlInfo = readMTLFile(mtlfile)
    saa = None
    sza = None
    
    if 'SUN_AZIMUTH' in mtlInfo:
        saa = numpy.radians(float(mtlInfo['SUN_AZIMUTH']))
    if 'SUN_ELEVATION' in mtlInfo:
        sza = numpy.radians(90.0 - float(mtlInfo['SUN_ELEVATION']))

    if saa is None or sza is None:
        msg = 'Cannot find SUN_AZIMUTH/SUN_ELEVATION fields in MTL file'
        raise fmaskerrors.FmaskFileError(msg)
    
    # TODO: do we have better numbers for the Landsat view azimuth?
    angles = AngleConstantInfo(sza, saa, 0.0, 0.0)
    return angles