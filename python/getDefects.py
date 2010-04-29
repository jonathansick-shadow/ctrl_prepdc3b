import sys
import lsst.afw.image as afwImage
import lsst.afw.detection as afwDetection


if __name__ == "__main__":
    rix = int(sys.argv[1])
    riy = int(sys.argv[2])
    print "    Raft:{"
    print "        name: \"R:%i,%i\""%(rix,riy)
    for six in range(0,3):
        for siy in range(0,3):
            file = "afwdata/ImSim/qe/QE_R%i%i_S%i%i.fits.gz"%(rix,riy,six,siy)
            im = afwImage.ImageF(file)
            thresh = afwDetection.Threshold(1.5)
            ds = afwDetection.FootprintSetF(im, thresh)
            fpList = ds.getFootprints()
            print "        Ccd: {"
            print "            serial: %i%i%i%i"%(rix,riy,six,siy)
            print "            name: \"R:%i,%i S:%i,%i\""%(rix,riy,six,siy)
            for fp in fpList:
                print "            Defect: {"
                print "                x0:",fp.getBBox().getY0()
                print "                y0:",fp.getBBox().getX0()
                print "                x1:",fp.getBBox().getY1()
                print "                y1:",fp.getBBox().getX1()
                print "            }"

            thresh = afwDetection.Threshold(-0.1)
            im *= -1.
            ds = afwDetection.FootprintSetF(im, thresh)
            fpList = ds.getFootprints()
            for fp in fpList:
                print "            Defect: {"
                print "                x0:",fp.getBBox().getY0()
                print "                y0:",fp.getBBox().getX0()
                print "                x1:",fp.getBBox().getY1()
                print "                y1:",fp.getBBox().getX1()
                print "            }"
            print "        }"
    print "    }"

