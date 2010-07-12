# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import pyfits
import sys
import os
import re
import lsst.afw.image as afwImage

maskFormat = re.compile('^\[(\d+):(\d+),(\d+):(\d+)\]$')

# It looks like these masks include the biassec on the LHS.
# It also includes the secs on the top and RHS
# I need to do some trimming here.
leftBox = afwImage.BBox(afwImage.PointI(0, 0),
                        afwImage.PointI(31, 4643))

# we actually need the bottom row of this top box
topBox0  = afwImage.BBox(afwImage.PointI(0, 4611),
                         afwImage.PointI(2111, 4643))
topBox1  = afwImage.BBox(afwImage.PointI(0, 4611),
                         afwImage.PointI(2111, 4611))

rightBox = afwImage.BBox(afwImage.PointI(2080, 0),
                         afwImage.PointI(2111, 4643))


inmask  = sys.argv[1] # mask definition
inimage = sys.argv[2] # need serial numbers
ptrM    = pyfits.open(inmask)
ptrI    = pyfits.open(inimage)

outfile = sys.argv[3]
buff    = open(outfile, 'w')
buff.write('Defects: { \n')
buff.write('    Raft: { \n')
buff.write('        name: "R:0,0" \n')
 

for ccd in range(1, 37):
    imHeader   = ptrI[ccd].header
    serial     = imHeader['CCDNAME']
    
    maskHeader = ptrM[ccd].header
    nColMask   = maskHeader['NAXIS1']
    nRowMask   = maskHeader['NAXIS2']

    buff.write('        Ccd: { \n')
    buff.write('            name: "CFHT %d" \n' % (ccd - 1))
    buff.write('            serial: %s \n' % (re.sub('-', '', serial)))

    for card in maskHeader.ascardlist().keys():
        if card.startswith('MASK_'):
            datasec = maskHeader[card]

            # Unfortunately, the format of the masks is wrong.  Its
            # x0,y0  x1,y1
            # e.g.
            # MASK_000= '[1:1,2112:1]'       / Bad pixels area definition
            #
            # Datasecs normally have
            # x0,x1  y0,y1
            # e.g.
            # CCDSIZE = '[1:2048,1:4612]'    / Detector imaging area size
            # bbox    = ipIsr.BboxFromDatasec(datasec)

            match = maskFormat.match(datasec)

            if match == None:
                # unable to match mask area!
                print '# WARNING: Extn', nExt, 'unable to parse', maskArea
                continue
            group = map(int, match.groups())

            

            bbox  = afwImage.BBox(afwImage.PointI(group[0]-1, group[1]-1),
                                  afwImage.PointI(group[2]-1, group[3]-1))

            if bbox == leftBox or bbox == rightBox:
                continue
            if bbox == topBox0:
                bbox = topBox1

            buff.write('            Defect: { \n')

            # The first full row is bad; this makes it start at -32.
            # Fix this one case manually.
            if (bbox.getX0() - 32) < 0:
                buff.write('                x0: %d \n' % (bbox.getX0()))
            else:
                buff.write('                x0: %d \n' % (bbox.getX0() - 32))

            # only coordinate that seems OK
            #
            # not anymore, we are getting rid of the first (and last) row
            buff.write('                y0: %d \n' % (bbox.getY0() - 1))

            # don't extend off the right
            if (bbox.getX1() - 32) > 2047:
                buff.write('                x1: %d \n' % (2047))
            else:
                buff.write('                x1: %d \n' % (bbox.getX1() - 32))

            # don't extend off the top
            # ymax = 4611  # took off top row (and bottom!  n-2)
            ymax = 4609
            if bbox.getY1() > ymax:
                buff.write('                y1: %d \n' % (ymax))
            else:
                buff.write('                y1: %d \n' % (bbox.getY1()))
                
            buff.write('            } \n')

    buff.write('        } \n')
buff.write('    } \n')
buff.write('} \n')                                   
buff.close()

# cd /lsst/home/becker/lsst_devel/obs_cfht/megacam/description/defects
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/2003B.mask.0.36.00.n.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits 2003B.mask.0.36.00.n.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/2003B.mask.0.36.01.n.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits 2003B.mask.0.36.01.n.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/2003B.mask.0.36.02.n.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits 2003B.mask.0.36.02.n.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/2004B.mask.0.36.00.n.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits 2004B.mask.0.36.00.n.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/2004B.mask.0.36.01.n.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits 2004B.mask.0.36.01.n.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/static.mask.0.36.00.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits static.mask.0.36.00.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/static.mask.0.36.01.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits static.mask.0.36.01.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/static.mask.0.36.02.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits static.mask.0.36.02.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/static.mask.0.36.03.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits static.mask.0.36.03.paf
#python ~/lsst_devel/prepdc3b/python/makeCfhtMaskDc3b.py /home/becker/repositoryDc3b/CFHTCalib/static.mask.0.36.04.fits /home/becker/repositoryDc3b/CFHTWide/704382o.fits static.mask.0.36.04.paf
