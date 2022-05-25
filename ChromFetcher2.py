from pathlib import Path
import struct
from xml.etree.ElementTree import parse


class Injection:
    def __init__(self, path):
        self.path = Path(path)
        self.acqmethod = self._get_acq_method()
        self.chromatograms = self._get_chromatograms()
        self._set_data()

    def _set_data(self):
        for drug, transitions in self.acqmethod.items():
            for trsn in transitions:
                filt = self._filter(float(trsn['parent']),
                                    float(trsn['fragment']),
                                    float(trsn['fragmentor']),
                                    float(trsn['collision energy']))

                xy = [[i['time'], i['tic']] for i in filt]
                trsn['points'] = xy

    def _get_chromatograms(self) -> list[dict]:
        scanbytes = self._open_injection()
        magic_number = 186
        offset = struct.unpack('I', scanbytes[88:92])[0]
        n = len(scanbytes)
        data = []

        if (n - offset) % magic_number == 0:
            nrows = (n - offset) // magic_number
            for i in range(nrows):
                start = offset + magic_number * i
                data.append(self._entry(scanbytes[start:start + magic_number]))

        return data

    def _filter(self, parent, fragment, fragmentor, ce) -> list[dict]:
        filt = [i for i in self.chromatograms if parent - .01 <= float(i['parent']) <= parent + .01]
        filt = [i for i in filt if fragment - .01 <= float(i['fragment']) <= fragment + .01]
        filt = [i for i in filt if float(fragmentor) == float(i['fragmentor'])]
        filt = [i for i in filt if ce == i['collision energy']]

        return filt

    def _entry(self, blist: bytes) -> dict:
        d = {'time': struct.unpack('d', blist[12:20])[0],
             'tic': struct.unpack('d', blist[26:34])[0],
             'fragment': struct.unpack('d', blist[34:42])[0],
             'fragmentor': struct.unpack('f', blist[72:76])[0],
             'collision energy': struct.unpack('f', blist[76:80])[0],
             'parent': struct.unpack('d', blist[80:88])[0]}

        return d

    def _open_injection(self) -> bytes:
        with open(self.path / 'AcqData\\MSScan.bin', 'rb') as file:
            scanbytes = file.read()

        return scanbytes

    def _get_acq_method(self):
        vals = {}
        path = None
        # Find XML Method file
        method_files = self.path / 'AcqData'
        for method_file in method_files.iterdir():
            xpath = self.path / method_file / '192_1.xml'
            if xpath.is_file():
                path = xpath

        # Parse xml data to dictionary 'vals'
        if path:
            x = parse(path)
            root = x.getroot()
            for child in root[10][0][5]:
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

                        val = [{'parent': parent,
                                'fragment': fragment,
                                'fragmentor': fragmentor,
                                'collision energy': ce,
                                'points': []}]

                        if drug in vals.keys():
                            vals[drug] = vals[drug] + val
                        else:
                            vals[drug] = val
        return vals


sb = Injection('C:\\PinPoint\\MassHunter\\Data\\PAR\\Test Injections\\-\\Butalbital.d')
a=1
