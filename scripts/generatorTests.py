import unittest
from volumes import mincException, mincVolume, NoDataException, IncorrectDimsException
from factory import volumeFromFile, volumeFromInstance
import numpy as N
import os


inputFilename = "/Users/jason/workspace/pyminc-eclipse/test.mnc"
outputFilename = "/Users/jason/workspace/pyminc-eclipse/test-out.mnc"

class TestFromFile(unittest.TestCase):
    """test the volumeFromFile generator"""
    def testFromFileError(self):
        """attempting to load a garbage file should raise exception"""
        self.assertRaises(mincException, volumeFromFile, "garbage.mnc")
    def testFromFileDataType(self):
        """ensure that default datatype is float"""
        v = volumeFromFile(inputFilename)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float32')
    def testFromFileData(self):
        """ensure data read from file is correct"""
        v = volumeFromFile(inputFilename)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 1)
        
class TestCopyConstructor(unittest.TestCase):
    def testCopyConstructorDimensions(self):
        """dimensions should be the same in copied volume"""
        v = volumeFromFile(inputFilename)
        n = volumeFromInstance(v, outputFilename)
        ns = n.sizes[0:3]
        vs = v.sizes[0:3]
        n.closeVolume()
        v.closeVolume()
        self.assertEqual(ns, vs)
    def testCopyWithoutData(self):
        """copying without data=True flag should result in array of zeros"""
        v = volumeFromFile(inputFilename)
        n = volumeFromInstance(v, outputFilename)
        m = n.data.max()
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(m, 0)
    def testCopyWithData(self):
        """copying with data=True flag should result in a copy of the data"""
        v = volumeFromFile(inputFilename)
        n = volumeFromInstance(v, outputFilename, data=True)
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(va, na)
    def testCopyWithData2(self):
        """ensure that data is copied and not referenced"""
        v = volumeFromFile(inputFilename)
        n = volumeFromInstance(v, outputFilename, data=True)
        # set data to some random value
        n.data[:,:,:] = 10
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertNotEqual(va, na)
        
class TestEmptyConstructor(unittest.TestCase):
    """tests for when no generator was used"""
    def testErrorOnDataAccess(self):
        """ensure error is raised on data access"""
        v = mincVolume(inputFilename)
        self.assertRaises(NoDataException, v.getdata)
    def testLoadData(self):
        """data should be accessible once openFile is called"""
        v = mincVolume(inputFilename)
        v.openFile()
        self.assertEqual(v.data.dtype, 'float32')
        v.closeVolume()
if __name__ == "__main__":
    unittest.main()
        
        