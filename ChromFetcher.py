import numpy as np
from os import listdir
from os.path import isdir, isfile
from xml.etree.ElementTree import parse
from json import dumps, loads
import svg_builder as sb


class Bezier(object):
    def __init__(self, x, y):
        self.dx = 1000
        self.dy = 1000

        self.pts = np.array([[x[i], y[i]] for i in range(len(x))])

        self.xmin, self.ymin = self.pts.min(0, initial=500000000000)
        self.xmax, self.ymax = self.pts.max(0, initial=0)

        self.pts = np.append(self.pts, [[self.xmax, self.ymin]], axis=0)

        self.curves = self.get_cubics()

    def get_bezier_coef(self):
        # since the formulas work given that we have n+1 points
        # then n must be this:
        n = len(self.pts) - 1

        # build coefficients matrix
        c = 4 * np.identity(n)
        np.fill_diagonal(c[1:], 1)
        np.fill_diagonal(c[:, 1:], 1)
        c[0, 0] = 2
        c[n - 1, n - 1] = 7
        c[n - 1, n - 2] = 2

        # build points vector
        pnts = [2 * (2 * self.pts[i] + self.pts[i + 1]) for i in range(n)]
        pnts[0] = self.pts[0] + 2 * self.pts[1]
        pnts[n - 1] = 8 * self.pts[n - 1] + self.pts[n]

        # solve system, find a & b
        a = np.linalg.solve(c, pnts)
        b = [0] * n
        for i in range(n - 1):
            b[i] = 2 * self.pts[i + 1] - a[i + 1]
        b[n - 1] = (a[n - 1] + self.pts[n]) / 2

        return a, b

    # returns the general Bezier cubic formula given 4 control points
    # noinspection PyTypeChecker
    def get_cubics(self):
        funs = []
        ctrl1, ctrl2 = self.get_bezier_coef()

        pts = self.pts
        for i in range(len(self.pts) - 1):
            b = list(ctrl1[i])
            c = list(ctrl2[i])
            d = list(pts[i + 1])
            svg = [b, c, d]

            funs = funs + svg
        return funs

    def get_coords(self):
        return dumps(self.curves)


class Chromatogram(object):
    def __init__(self, sample_file):
        self.path = sample_file
        self.dtype = self.msscan()
        self.data = self.binary2numpy()
        self.ymax = max([i[3] for i in self.data])

    def binary2numpy(self):
        magic_number = 257
        header_size = 68
        agilent_dtype = self.msscan()

        with open(self.path, 'rb') as fp:
            if int.from_bytes(fp.read(4), "little") != magic_number:
                raise IOError("Invalid header for MSScan.")
            fp.seek(header_size + 20)
            offset = int.from_bytes(fp.read(4), "little")
            fp.seek(offset)
            buffer = fp.read()
            return np.frombuffer(buffer, dtype=agilent_dtype)

    def msscan(self):
        msscan_dtype = np.dtype(
            [("ScanID", np.int32),
             ("ScanMethodID", np.int32),
             ("TimeSegmentID", np.int32),
             ("ScanTime", np.float64),
             ("MSLevel", np.int16),
             ("ScanType", np.int32),
             ("TIC", np.float64),
             ("BasePeakMZ", np.float64),
             ("BasePeakValue", np.float64),
             ("CycleNumber", np.int32),
             ("Status", np.int32),
             ("IonMode", np.int32),
             ("IonPolarity", np.int16),
             ("CompensationField", np.float32),
             ("DispersionField", np.float32),
             ("Fragmentor", np.float32),
             ("CollisionEnergy", np.float32),
             ("MzOfInterest", np.float64),
             ("SamplingPeriod", np.float64),
             ("DwellTime", np.int32),
             ("MeasuredMassRangeMin", np.float64),
             ("MeasuredMassRangeMax", np.float64),
             ("Threshold", np.float64),
             ("IsFragmentorDynamic", np.int16),
             ("IsCollisionEnergyDynamic", np.int16),
             ("DataDependentScanParamType", np.dtype([("DDScanID", np.int32),
                                                      ("DDScanID2", np.int32)]),),
             ("SpectrumParamValues", np.dtype([("SpectrumFormatID", np.int16),
                                               ("SpectrumOffset", np.int64),
                                               ("ByteCount", np.int32),
                                               ("PointCount", np.int32),
                                               ("MinX", np.float64),
                                               ("MaxX", np.float64),
                                               ("MinY", np.float64),
                                               ("MaxY", np.float64), ]),)])
        return msscan_dtype

    def get_xy(self, parent, fragment, fragmentor, ce):
        b = None
        filt = [(i[3], i[6], i[7], i[15], i[16]) for i in self.data if parent - .01 <= float(i[17]) <= parent + .01]

        filt = [(i[0], i[1], i[3], i[4]) for i in filt if fragment - .01 <= float(i[2]) <= fragment + .01]

        filt = [(i[0], i[1], i[3]) for i in filt if float(fragmentor) == float(i[2])]

        filt = [(float(i[0]), float(i[1])) for i in filt if ce == i[2]]

        if filt:
            x, y = zip(*filt)
            b = Bezier(x, y)

        return b


# noinspection PyBroadException
def acq_method(path):
    vals = []
    method_files = listdir(path)
    for method_file in method_files:
        xpath = path + '\\' + method_file + '\\192_1.xml'
        if isfile(xpath):
            chrom = Chromatogram(path + '\\MSScan.bin')

            x = parse(xpath)

            root = x.getroot()
            root = root[10][0][5]
            vals = []
            for child in root:
                for el in child:
                    drug, parent, fragment, fragmentor, ce = None, None, None, None, None
                    if el.tag == 'scanElements':
                        for grandchild in el[0]:
                            if grandchild.tag == 'compoundName':
                                drug = grandchild.text
                            elif grandchild.tag == 'ms1LowMz':
                                parent = grandchild.text
                            elif grandchild.tag == 'ms2LowMz':
                                fragment = grandchild.text
                            elif grandchild.tag == 'fragmentor':
                                fragmentor = grandchild.text
                            elif grandchild.tag == 'collisionEnergy':
                                ce = grandchild.text
                        b = chrom.get_xy(float(parent), float(fragment), float(fragmentor), float(ce))

                        val = {'drug': drug,
                               'parent': parent,
                               'fragment': fragment,
                               'fragmentor': fragmentor,
                               'collision energy': ce,
                               'xmax': b.xmax,
                               'xmin': b.xmin,
                               'ymax': b.ymax,
                               'ymin': b.ymin,
                               'bezier': b.get_coords()}
                        vals.append(val)
    return vals


# noinspection PyBroadException
def search_dir(path):
    ans = []
    method_path = path + '\\AcqData'
    if isdir(method_path):
        try:
            ans = acq_method(method_path)
        except:
            pass

    return ans


def xy(data, parent, fragment):
    parent_filter = [list(i) for i in data if parent - .01 <= float(i[17]) <= parent + .01]
    fragment_filter = [list(i) for i in parent_filter if
                       fragment - .01 <= i[7] <= fragment + .01]

    return fragment_filter


class Chroms(object):
    def __init__(self, chrom):
        if chrom:
            self.bezier = loads(chrom['bezier'])
            self.xmin = chrom['xmin']
            self.xmax = chrom['xmax']
            self.ymin = chrom['ymin']
            self.ymax = chrom['ymax']
            self.drug = chrom['drug']
        else:
            self.bezier = None
            self.xmin = None
            self.xmax = None
            self.ymin = None
            self.ymax = None

    def get_body(self, xmin, ymin, xmax, ymax, divx=1, divy=1):
        # Transform Data
        dx = 1000
        dy = 500
        xmin = xmin / divx
        ymin = ymin / divy
        xmax = xmax / divx
        ymax = 1 * ymax / divy

        body = ''
        if self.bezier is not None:
            jsn = [[dx * (j[0] / divx - xmin) / (xmax - xmin), -dy * (j[1] / divy - ymin) / (ymax - ymin) + dy]
                   for j in self.bezier]
            body = ', '.join([str(i[0]) + ' ' + str(i[1]) for i in jsn])

        return body


if __name__ == '__main__':
    qqq = search_dir('C:\\PinPoint\\MassHunter\\Data\\Test Injections\\Test Injections\\test-A.d')
    f = sb.Chromatogram('test', 1000, 500)
    ff = Chroms(qqq[0])
    f.add_cubic(0, 500, ff.get_body(ff.xmin, ff.ymin, ff.xmax, ff.ymax*1.1), f.col3)
    svg=f.save()
    with open('test.svg','w') as file:
        file.write(svg)
    q = 1
