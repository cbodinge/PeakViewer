from pathlib import Path
import struct


def open_injection(scanpath: str) -> bytes:
    path = Path(scanpath)
    scanfile = path / 'AcqData\\MSScan.bin'
    with open(scanfile, 'rb') as file:
        scanbytes = file.read()

    return scanbytes


def get_injection_data(scanbytes: bytes) -> list[dict]:
    magic_number = 186
    offset = struct.unpack('I', scanbytes[88:92])[0]
    n = len(scanbytes)
    data = []

    if (n - offset) % magic_number == 0:
        nrows = (n - offset) // 186
        for i in range(nrows):
            start = offset + 186 * i
            data.append(entry(scanbytes[start:start + 186]))

    return data


def entry(blist: bytes) -> dict:
    d = {'time': struct.unpack('d', blist[12:20]),
         'tic': struct.unpack('d', blist[26:34]),
         'fragment': struct.unpack('d', blist[34:42]),
         'fragmentor': struct.unpack('f', blist[72:76]),
         'collision energy': struct.unpack('f', blist[76:80]),
         'parent': struct.unpack('d', blist[80:88])}

    return d


sb = open_injection('C:\\PinPoint\\MassHunter\\Data\\PAR\\Test Injections\\-\\Butalbital.d')
DATA = get_injection_data(sb)