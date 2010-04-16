#!/usr/bin/env python

# For reference the file name conventions are at:
#
# http://dev.lsstcorp.org/trac/wiki/DC3bDataOrganization 

import string
import sys
import os
import pyfits
import numpy
import lsst.afw.image as afwImage
import lsst.afw.image.testUtils as testUtils

# where do you want the data to end up
BASEDIR = None


def saveScience(data, header, basedir, fieldid, visitid, filterid, snapid, ccdid, ampid):
    # CFHTLS/%(field)/raw/v%(visitid)-f%(filterid)/s%(snapid)/c%(ccdid)-a%(ampid).fits

    # I think CFHTLS is redundant here, we can move this dir structure en masse into CFHTLS
    # outdir  = '%s/CFHTLS/%s/raw/v%s-f%s/s%s' % (basedir, fieldid, visitid, filterid, snapid)
    outdir  = '%s/%s/raw/v%s-f%s/s%s' % (basedir, fieldid, visitid, filterid, snapid)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        
    outfile = '%s/c%s-a%s.fits' % (outdir, ccdid, ampid)
    print '# writing', outfile
    header.update('DC3BPATH', outfile)

    hdu = pyfits.PrimaryHDU(data, header)
    hdu.scale('int16', '', bscale = 1.0, bzero = 32768.0)
    hdu.writeto(outfile, output_verify='silentfix', clobber=True)
    
def saveCalibration(data, header, basedir, dtype, dateid, ccdid, ampid, filterid):
    # CFHTLS/%(dtype)/v%(dateid)/c%(ccdid)-a%(ampid).fits
    # -- or --
    # CFHTLS/%(dtype)/v%(dateid)-f%(filterid)/c%(ccdid)-a%(ampid).fits

    if filterid == None:
        #outdir = '%s/CFHTLS/%s/v%s' % (basedir, dtype, dateid)
        outdir = '%s/%s/v%s' % (basedir, dtype, dateid)
    else:
        #outdir = '%s/CFHTLS/%s/v%s-f%s' % (basedir, dtype, dateid, filterid)
        outdir = '%s/%s/v%s-f%s' % (basedir, dtype, dateid, filterid)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    outfile = '%s/c%s-a%s.fits' % (outdir, ccdid, ampid)

    # we need to be a bit more tricky with the cals, since they should
    # be masked images.  since pyfits has a problem with MEFs with
    # different types, just use the build system for making the cals.
    # we don't need (I don't think?) the header information as much as
    # we need it for the science images
    if dtype == 'bias':
        retType = afwImage.MaskedImageI
    else:
        retType = afwImage.MaskedImageF
    mi = testUtils.maskedImageFromArrays( [data.T, 0 * data.T, 0 * data.T],
                                          retType=retType)
    print '# writing', outfile
    mi.writeFits(outfile)

    # note : potential issue, is that the cals have the overscan
    # borders, and I am *not* setting their associated mask and
    # variance equal to 0x1 and NaN, respectively.



if __name__ == '__main__':
    for file in sys.argv[1:]:

        if BASEDIR == None:
            basedir = os.path.dirname(os.path.abspath(file))
        else:
            basedir = BASEDIR
        ptr     = pyfits.open(file)
        head    = ptr[0].header

        if head['OBSTYPE'] == 'BIAS' or head['OBSTYPE'] == 'FLAT' or head['OBSTYPE'] == 'FRINGE':
            isCal = True
            dtype = head['OBSTYPE'].lower()
            dateid = head['CRUNID']
        else:
            isCal = False


        # Some of the wides have e.g. 'w3' instead of 'W3'
        fieldid  = string.capitalize('%s' % (head['OBJECT'][:2]))
        visitid  = '%d' % (head['OBSID'])

        filter   = head['FILTER']
        if filter.startswith('i') and filter.endswith('2'):
            filterid = '%s%s' % (filter[0], filter[-1])   # only 1 character
        else:
            filterid = '%s' % (head['FILTER'][0])   # only 1 character
        snapid   = '%02d' % (0)                 # always, no cosmic ray splits

        # lets send no filter for dark and bias
        if dtype == 'bias' or dtype == 'dark':
            filterid = None
        
        for ccd in range(1, len(ptr)):
            # Details:
            #
            # The images have already been spliced from their natural readout.
            # The CameraGeom should therefore reflect this spliced configuration.
            #
            # http://cfht.hawaii.edu/Instruments/Imaging/MegaPrime/rawdata.html

            data   = ptr[ccd].data
            header = ptr[ccd].header

            # If you want to avoid any and all confusion with fits headers & data section
            if 1:
                for keyword in ['DETSEC', 'DETSECA', 'DETSECB', 'DATASEC', 
                                'ASECA', 'DSECA', 'TSECA', 'BSECA', 'CSECA', 
                                'ASECB', 'DSECB', 'TSECB', 'BSECB', 'CSECB', 
                                'BIASSEC']:
                    header.update(keyword, '')

            cfhtAmpA  = data[0:4644, 0:1056]
            cfhtAmpB  = data[0:4644, 1056:2112]

            headerA = header.copy()
            if isCal:
                saveCalibration(cfhtAmpA, headerA, basedir,
                                dtype, dateid, '%02d' % (ccd-1), 0, filterid)
            else:
                saveScience(cfhtAmpA, headerA, basedir,
                            fieldid, visitid, filterid, snapid, '%02d' % (ccd-1), 0)
            
            headerB = header.copy()
            if isCal:
                saveCalibration(cfhtAmpB, headerB, basedir,
                                 dtype, dateid, '%02d' % (ccd-1), 1, filterid)
            else:
                crpix1 = headerB['CRPIX1']
                headerB.update('CRPIX1', crpix1 + 1024)
                saveScience(cfhtAmpB, headerB, basedir,
                            fieldid, visitid, filterid, snapid, '%02d' % (ccd-1), 1)
                        
            #print data.shape, cfhtAmpA.shape, cfhtAmpB.shape
