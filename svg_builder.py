import py_svg as psvg


def num2per(num):
    try:
        per = str(num) + '%'
    except TypeError:
        per = '0%'

    return per


class Chromatogram(list):
    def __init__(self, name, w, h):
        super().__init__()
        self.append('<svg width="%s" height="%s" xmlns="http://www.w3.org/2000/svg">   ' % (str(w), str(h)))
        self.keys = []
        self.col1 = {'fill': (0, 0, 0),
                     'stroke': (0, 0, 0),
                     'fill-opacity': 0,
                     'stroke-width': 7,
                     'stroke-dash-array': None}

        self.col2 = {'fill': (70, 225, 170),
                     'stroke': (70, 225, 170),
                     'fill-opacity': .15,
                     'stroke-width': 2,
                     'stroke-dash-array': None}

        self.col3 = {'fill': (70, 70, 225),
                     'stroke': (70, 70, 225),
                     'fill-opacity': .4,
                     'stroke-width': 2,
                     'stroke-dash-array': None}

        self.col4 = {'fill': (70, 225, 170),
                     'stroke': (70, 225, 170),
                     'fill-opacity': .5,
                     'stroke-width': 2,
                     'stroke-dash-array': None}

        self.blck = {'fill': (0, 0, 0),
                     'stroke': (0, 0, 0),
                     'fill-opacity': 0,
                     'stroke-width': 4,
                     'stroke-dash-array': 10}

        self.margin = 3

        # Add Graph Title
        x = num2per(100 - self.margin)
        y = num2per(1.5 * self.margin)
        self.add_text(name, x, y, 'end')

    def add_cubic(self, x1, y1, body, settings=None):
        if settings is None:
            settings = self.col1

        row = psvg.Cubic(x1, y1, body)
        row.set_fill(settings['fill'])
        row.set_stroke(settings['stroke'])
        row.set_fill_opacity(settings['fill-opacity'])
        row.set_stroke_width(settings['stroke-width'])

        svg = row.construct()
        self.append(svg)

    def add_key(self, label, settings):
        n = len(self.keys)
        dy = (2 * n + 1) * self.margin

        x = num2per(self.margin)
        y = num2per(dy)
        w = num2per(self.margin)
        h = num2per(self.margin)

        # Set Box
        row = psvg.Rect(x, y, w, h)
        row.set_fill(settings['fill'])
        row.set_fill_opacity(settings['fill-opacity'])
        svg = row.construct()
        self.append(svg)

        # Set Line
        x1 = num2per(self.margin)
        x2 = num2per(2 * self.margin)
        if settings['fill-opacity'] == 0:
            y1 = num2per(dy + (self.margin / 2))
        else:
            y1 = y

        row = psvg.Line(x1, y1, x2, y1)
        row.set_stroke(settings['stroke'])
        row.set_stroke_width(settings['stroke-width'])
        row.set_dash_array(settings['stroke-dash-array'])
        svg = row.construct()
        self.append(svg)

        # Set Text
        x = num2per(3 * self.margin)
        y = num2per(dy + (self.margin / 2))
        self.add_text(label, x, y, 'left')

        self.keys.append(label)

    def add_text(self, label, x, y, side):
        row = psvg.Text(label, x, y)
        row.set_font_family('IBM Plex Mono')
        row.set_font_size(40)
        row.set_font_weight(500)
        row.set_dominant_baseline('central')
        row.set_text_anchor(side)
        svg = row.construct()
        self.append(svg)

    def add_line(self, x1, y1, x2, y2):
        row = psvg.Line(x1, y1, x2, y2)
        row.set_stroke(self.blck['stroke'])
        row.set_stroke_width(self.blck['stroke-width'])
        row.set_dash_array(self.blck['stroke-dash-array'])

        svg = row.construct()
        self.append(svg)

    def save(self):
        row = psvg.Rect(0, 0, '100%', '100%')
        row.set_fill_opacity(0)
        row.set_stroke((10, 10, 15))
        row.set_stroke_width(5)
        self.append(row.construct())
        self.append('</svg>')
        ans = '\n'.join(self)

        return ans


class HTML(object):
    def __init__(self):
        super().__init__()

        self.body = []

    def add_section(self, drug, svg):
        div = ['<h1>%s</h1>' % [drug],
               '<div class="myDiv">',
               svg,
               '</div>']

        self.body.append('\n'.join(div))

    def save(self):
        htmlist = ['<!DOCTYPE html>',
                   '<html>',
                   '<head>',
                   '<style>',
                   '.myDiv {border: 1px outset red; background-color: lightblue; text-align: center;}',
                   '</style>',
                   '</head>',
                   '<body>']

        for item in self.body:
            htmlist.append(item)

        htmlist.append('</body>')
        htmlist.append('</html>')

        return '\n'.join(htmlist)
