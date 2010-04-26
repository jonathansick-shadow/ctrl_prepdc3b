#!/usr/bin/env python

# For reference the file name conventions are at:
#
# http://dev.lsstcorp.org/trac/wiki/DC3bDataOrganization 

# THIS VERSION USES AFW

import sys, os, string
import lsst.daf.base as dafBase
import lsst.afw.image as afwImage

# where do you want the data to end up
if os.environ['HOSTNAME'].endswith('ncsa.uiuc.edu'):
    BASEDIR = '/lsst/DC3/data/obstest/CFHTLS'
else:
    BASEDIR = None


def saveScience(dim, basedir, fieldid, visitid, filterid, snapid, ccdid, ampid):
    # CFHTLS/%(field)/raw/v%(visitid)-f%(filterid)/s%(snapid)/c%(ccdid)-a%(ampid).fits

    outdir  = '%s/%s/raw/v%s-f%s/s%s' % (basedir, fieldid, visitid, filterid, snapid)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        
    outfile = '%s/c%s-a%s.fits' % (outdir, ccdid, ampid)
    print '# writing', outfile

    dim.getMetadata().set('DC3BPATH', outfile)
    dim.writeFits(outfile)

    
def saveCalibration(dim, basedir, dtype, dateid, ccdid, ampid, filterid):
    # CFHTLS/%(dtype)/v%(dateid)/c%(ccdid)-a%(ampid).fits
    # -- or --
    # CFHTLS/%(dtype)/v%(dateid)-f%(filterid)/c%(ccdid)-a%(ampid).fits

    if filterid == None:
        outdir = '%s/%s/v%s' % (basedir, dtype, dateid)
        if dtype == 'dark':
            outdir = '%s/%s/v%s-e%d' % (basedir, dtype, dateid, int(dim.getMetadata().get('DARKTIME')))
            
    else:
        outdir = '%s/%s/v%s-f%s' % (basedir, dtype, dateid, filterid)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    outfile = '%s/c%s-a%s.fits' % (outdir, ccdid, ampid)
    print '# writing', outfile

    # convert to exposure
    exp = afwImage.ExposureF(afwImage.MaskedImageF(dim.getImage()), afwImage.Wcs())
    exp.setMetadata(dim.getMetadata())

    exp.getMetadata().set('DC3BPATH', outfile)
    exp.writeFits(outfile)


if __name__ == '__main__':
    bbox1 = afwImage.BBox(afwImage.PointI(0, 0),
                          1056, 4644)
    bbox2 = afwImage.BBox(afwImage.PointI(1056, 0),
                          1056, 4644)

    #print bbox1.getX0(), bbox1.getX1(), bbox1.getY0(), bbox1.getY1()
    #print bbox2.getX0(), bbox2.getX1(), bbox2.getY0(), bbox2.getY1()
    
    for file in sys.argv[1:]:

        if BASEDIR == None:
            basedir = os.path.dirname(os.path.abspath(file))
        else:
            basedir = BASEDIR

        for ccd in range(2, 38):
            try:
                dim1 = afwImage.DecoratedImageF(file, ccd, bbox1)
                dim2 = afwImage.DecoratedImageF(file, ccd, bbox2)
            except Exception, e:
                print 'FAILED', e
                sys.exit(1)

            md1 = dim1.getMetadata()
            md2 = dim2.getMetadata()

            # Some of the wides have e.g. 'w3' instead of 'W3'
            fieldid  = string.capitalize('%s' % (md1.get('OBJECT')[:2]))
            visitid  = '%d' % (md1.get('OBSID'))

            # Filter
            filter   = md1.get('FILTER').strip()
            if filter.startswith('i') and filter.endswith('2'):
                filterid = '%s%s' % (filter[0], filter[-1]) 
            else:
                filterid = '%s' % (filter[0])               

            # Always snapshot 0; no cosmic ray splits
            snapid   = '%02d' % (0)

            # Type of observation
            if md1.get('OBSTYPE').strip() == 'BIAS' or \
               md1.get('OBSTYPE').strip() == 'FLAT' or \
               md1.get('OBSTYPE').strip() == 'DARK' or \
               md1.get('OBSTYPE').strip() == 'FRINGE':
                isCal = True
                dtype = md1.get('OBSTYPE').strip().lower()
                dateid = md1.get('CRUNID').strip()
                
                # lets send no filter for dark and bias
                if dtype == 'bias' or dtype == 'dark':
                    filterid = None
            else:
                isCal = False

            # Clear out conflicting information from header
            for keyword in ['DETSEC', 'DETSECA', 'DETSECB', 'DATASEC', 
                            'ASECA', 'DSECA', 'TSECA', 'BSECA', 'CSECA', 
                            'ASECB', 'DSECB', 'TSECB', 'BSECB', 'CSECB', 
                            'BIASSEC']:
                md1.remove(keyword)
                md2.remove(keyword)


            # Write 'em
            if isCal:
                saveCalibration(dim1, basedir, dtype, dateid, '%02d' % (ccd-2), 0, filterid)
                saveCalibration(dim2, basedir, dtype, dateid, '%02d' % (ccd-2), 1, filterid)
            else:
                saveScience(dim1, basedir, fieldid, visitid, filterid, snapid, '%02d' % (ccd-2), 0)
                crpix1 = md2.get('CRPIX1')
                md2.set('CRPIX1', crpix1 + 1024)
                saveScience(dim2, basedir, fieldid, visitid, filterid, snapid, '%02d' % (ccd-2), 1)

            
            del dim1, dim2
