.. _contents:

Python Fmask
========================================================

Introduction
------------

A set of command line utilities and Python modules that implement
the 'fmask' algorithm as published in:
    Zhu, Z. and Woodcock, C.E. (2012). 
    Object-based cloud and cloud shadow detection in Landsat imagery
    Remote Sensing of Environment 118 (2012) 83-94. 
    
    and
    
    Zhu, Z., Wang, S. and Woodcock, C.E. (2015).
    Improvement and expansion of the Fmask algorithm: cloud, cloud
    shadow, and snow detection for Landsats 4-7, 8, and Sentinel 2 images
    Remote Sensing of Environment 159 (2015) 269-277.

Installation requires `Python <http://python.org/>`_, `numpy <http://www.numpy.org/>`_, `scipy <http://www.scipy.org/>`_,
`GDAL <http://gdal.org/>`_ and `RIOS <http://rioshome.org/>`_.
It is licensed under GPL 3.

Command Line Examples
---------------------

Please note that the output format used is defined by RIOS. This defaults to HFA (.img). 
See `RIOS documentation <http://rioshome.org/rios_imagewriter.html#rios.imagewriter.setDefaultDriver>`_
for more information and how to change this using environment variables.

USGS Landsat
^^^^^^^^^^^^

The command line scripts supplied can process an untarred USGS Landsat scene. Here is an 
example of how to to this::

    gdal_merge.py -separate -of HFA -co COMPRESSED=YES -o ref.img L*_B[1,2,3,4,5,7].TIF
    gdal_merge.py -separate -of HFA -co COMPRESSED=YES -o thermal.img L*_B6_VCID_?.TIF
    fmask_usgsLandsatSaturationMask.py -i ref.img -m LE7*_MTL.txt -o saturationmask.img
    fmask_usgsLandsatTOA.py -i ref.img -m LE7*_MTL.txt -o toa.img
    fmask_usgsLandsatStacked.py -t thermal.img -a toa.img -m LE7*_MTL.txt -s saturationmask.img -o cloud.img 


Sentinel2
^^^^^^^^^

The command line scripts supplied can process a Sentinel2 granule from the image directory. 
Here is an example of how to to this::

    gdalbuildvrt -resolution lowest -separate allbands.vrt S2*_B0[1-9].jp2 S2*_B1[0-2].jp2
    fmask_sentinel2Stacked.py -a allbands.vrt -x ../*.xml -o cloud.img

Downloads
---------
From `Sourceforge <http://sourceforge.net/projects/pythonfmask/>`_ or `BitBucket <https://bitbucket.org/chchrsc/python-fmask/downloads>`_.

Python developer documentation
------------------------------

.. toctree::
    :maxdepth: 1

    Running the fmask algorithm  <fmask_fmask>
    Configuring the fmask run <fmask_config>
    Creating Top of Atmosphere rasters for Landsat <fmask_landsatTOA>
    fmask_saturationcheck
    fmask_zerocheck
    fmask_fillminima
    fmask_valueindexes
    fmask_fmaskerrors

* :ref:`modindex`
* :ref:`search`

.. codeauthor:: Neil Flood & Sam Gillingham