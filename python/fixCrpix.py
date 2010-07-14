import os, sys
import lsst.afw.image as afwImage

BASEDIR = '/usr/data/mysql1/CFHT/CFHTDeep/'
dirs = ['D1', 'D2', 'D3', 'D4']
for dir1 in dirs:
    raw = os.path.join(BASEDIR, dir1, 'raw')
    for dir2 in os.listdir(raw):
        s00 = os.path.join(raw, dir2, 's00')
        for file in os.listdir(s00):
            # print s00, file
            if not file.endswith('a1.fits'):
                continue
            fullfile = os.path.join(s00, file)
            dim   = afwImage.DecoratedImageF(fullfile)
            md    = dim.getMetadata()
            if md.exists('CRPIX1acb'):
                continue
            crpix = md.get('CRPIX1')
            md.set('CRPIX1acb', crpix)
            md.set('CRPIX1', crpix - 2048)

            # outfile = '/tmp/acb.fits'
            # print fullfile, outfile
            dim.writeFits(fullfile)
