Release Notes
=============

Version 0.4.4 (2017-04-04)
--------------------------

Enhancements
  * Added commandline options to set cloud probability threshold, and the two reflectance 
    thresholds used for the snow mask. 
  * Call gdal.UseExceptions(), so that when bad things happen, they are more likely
    to be reported accurately by the exception message, and reduce confusion for users. 


Version 0.4.3 (2016-11-26)
--------------------------

Bug Fixes:
  * Fix 32 bit builds
  * Fix help message for fmask_usgsLandsatStacked.py

Enhancements
  * Helper .bat file for Windows to expand wildcards
  * Changes to 'nodata' handling to make processing in parallel possible with RIOS


Version 0.4.2 (2016-09-01)
--------------------------

Bug Fixes
  * Fixed fall-back default values for Landsat brightness temperature equation constants, 
    as required when processing older USGS files which do not have these present in the MTL file. 
  * For Sentinel-2 only, added a work-around for the alarming random null pixels which
    ESA leave in the cirrus band. This avoids leaving corresponding null pixels in the 
    resulting output masks. 


Version 0.4.0 (2016-06-10)
--------------------------

Bug fixes
  * Proper null mask taken from all reflective bands combined, not just the blue band
  * Trap seg-faults in valueindexes C code
  * Use null value of 32767 for Landsat TOA image
  * Cope when Sentinel-2 metadata only has sensor angles for a subset of bands. 

Enhancements
  * Landsat angles code is now in a module, with a main program wrapper, consistent 
    with the rest of the package
  * Added :command:`--cloudbufferdistance`, :command:`--shadowbufferdistance` and 
    :command:`--mincloudsize` options to
    main program wrappers (both Landsat and Sentinel-2) to give user control over these
    parameters


Version 0.3.0 (2016-03-21)
--------------------------

Bug fixes
  * Added code for estimating per-pixel Landsat sun and sensor angles, to allow proper
    shadow tracking, as per original code
  * Full use of Sentinel-2 metadata XML, including per-pixel angles grid

