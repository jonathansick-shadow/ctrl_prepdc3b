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

topBox  = afwImage.BBox(afwImage.PointI(0, 4611),
                        afwImage.PointI(2111, 4643))

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

            if bbox == leftBox or bbox == topBox or bbox == rightBox:
                continue

            buff.write('            Defect: { \n')

            # The first full row is bad; this makes it start at -32.
            # Fix this one case manually.
            if (bbox.getX0() - 32) < 0:
                buff.write('                x0: %d \n' % (bbox.getX0()))
            else:
                buff.write('                x0: %d \n' % (bbox.getX0() - 32))
                
            buff.write('                y0: %d \n' % (bbox.getY0()))
            buff.write('                x1: %d \n' % (bbox.getX1() - 32))
            buff.write('                y1: %d \n' % (bbox.getY1()))
            buff.write('            } \n')

    buff.write('        } \n')
buff.write('    } \n')
buff.write('} \n')                                   
buff.close()
