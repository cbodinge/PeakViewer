# Chromatogram Dimensions
chrom_x = 1000
chrom_y = 500

# Calibration Curve Dimensions
cal_x = 3000
cal_y = 800

# Page Size
page_w = 850
page_h = 1100

# QC Chart Size
qc_w = 750
qc_h = 300
qc_maxdev = 1.5
qc_maxruns = 10

# PDF Size
pdf_w = 637.5
pdf_h = 825

# Color Palette
color = {0: (0, 0, 0),
         1: (70, 225, 170),
         2: (70, 70, 225),
         3: (255, 255, 255),
         4: (180, 225, 70)}

# Path to Data Folder
data_path = 'C:\\PinPoint\\MassHunter\\Data\\Report Testing'

# Multiplier for y max (reduces the graph height)
mult = 1.35


def minmax(mtype, mlist):
    m = None
    if mtype == 'max':
        m = None
        for el in mlist:
            if m is None:
                m = el
            if el is not None and m is not None and el > m:
                m = el

    if mtype == 'min':
        m = None
        for el in mlist:
            if m is None:
                m = el
            if el is not None and m is not None and el < m:
                m = el

    return m
