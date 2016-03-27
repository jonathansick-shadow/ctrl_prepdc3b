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

import sys
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDetection


if __name__ == "__main__":
    rix = int(sys.argv[1])
    riy = int(sys.argv[2])
    print "    Raft:{"
    print "        name: \"R:%i,%i\""%(rix, riy)
    for six in range(0, 3):
        for siy in range(0, 3):
            file = "afwdata/ImSim/qe/QE_R%i%i_S%i%i.fits.gz"%(rix, riy, six, siy)
            im = afwImage.ImageF(file)
            thresh = afwDetection.Threshold(1.5)
            ds = afwDetection.FootprintSetF(im, thresh)
            fpList = ds.getFootprints()
            print "        Ccd: {"
            print "            serial: %i%i%i%i"%(rix, riy, six, siy)
            print "            name: \"R:%i,%i S:%i,%i\""%(rix, riy, six, siy)
            for fp in fpList:
                print "            Defect: {"
                print "                x0:", fp.getBBox().getY0()
                print "                y0:", fp.getBBox().getX0()
                print "                x1:", fp.getBBox().getY1()
                print "                y1:", fp.getBBox().getX1()
                print "            }"

            thresh = afwDetection.Threshold(-0.1)
            im *= -1.
            ds = afwDetection.FootprintSetF(im, thresh)
            fpList = ds.getFootprints()
            for fp in fpList:
                print "            Defect: {"
                print "                x0:", fp.getBBox().getY0()
                print "                y0:", fp.getBBox().getX0()
                print "                x1:", fp.getBBox().getY1()
                print "                y1:", fp.getBBox().getX1()
                print "            }"
            print "        }"
    print "    }"

