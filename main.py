import calendar
import datetime
import ephem
import math

MOON_DIAMETER = 40
LIGHT_COLOUR  = '#f7f7c0'
SHADOW_COLOUR = '#274982'

class Page:
    def __init__(self):
        self.template = open('template.html').read()

    def _replace_in_template(self, key, value):
        self.template = self.template.replace('<!-- {} -->'.format(key), value)

    def _moon_key(self, m, d):
        return 'MOON_{:02d}_{:02d}'.format(m, d)

    def _write_table(self):
        content = []
        for m in range(1, 13):
            row = '<tr>'
            for d in range(1,32):
                row += '<td>{}</td>'.format(self._moon_key(m, d))
            row += '</tr>'
            content.append(row)

    def _calc_terminator_radius(self, l, r):
        right = None
        illum = None
        L = None

        if l <= 0.25:
            L = l
            right = True
            illum = False
        elif l <= 0.5:
            L = 0.5 - l
            right = False
            illum = False
        elif l <= 0.75:
            L = l - 0.5
            right = True
            illum = True
        else:
            L = 1 - l
            right = False
            illum = True

        x = r * (1 - math.cos(2*math.pi*L))
        n = r - x
        return (r * r + n * n) / (2 * n), right, illum

    def _make_path(self, lunation):
        terminator_radius, right, illum = self._calc_terminator_radius(lunation, MOON_DIAMETER/2)
        colour1 = LIGHT_COLOUR if illum else SHADOW_COLOUR
        colour2 = SHADOW_COLOUR if illum else LIGHT_COLOUR

        move_to_top = 'M{0},0'.format(MOON_DIAMETER/2)
        terminator_arc = 'A {0} {0} 0 0 {1} {2} {3}'.format(terminator_radius, 1 if right else 0, MOON_DIAMETER/2, MOON_DIAMETER)
        left_side_arc = 'A {0} {0} 0 0 1 {0} 0'.format(MOON_DIAMETER/2)
        right_side_arc = 'A {0} {0} 0 0 0 {0} 0'.format(MOON_DIAMETER/2)

        path1 = '<path d="{0} {1} {2}" fill="{3}"/>'.format(move_to_top, terminator_arc, left_side_arc, colour1)

        path2 = '<path d="{0} {1} {2}" fill="{3}"/>'.format(move_to_top, terminator_arc, right_side_arc, colour2)

        return  path1 + path2

    def _generate_moon(self, y, m, d):
        date=ephem.Date(datetime.date(y,m,d))

        nnm = ephem.next_new_moon    (date)
        pnm = ephem.previous_new_moon(date)

        lunation = (date-pnm)/(nnm-pnm)

        return '<svg width="{0}" height="{0}">{1}</svg>'.format(MOON_DIAMETER, self._make_path(lunation))

    def populate(self, year):
        self._replace_in_template('YEAR', str(year))
        for month in range(1,13):
            _, days = calendar.monthrange(year, month)
            for day in range(1, days+1):
                key = self._moon_key(month, day)
                moon = self._generate_moon(year, month, day)
                self._replace_in_template(key, moon)


    def save(self, path):
        open(path, 'w').write(self.template)

YEAR = 2018
page = Page()
page.populate(YEAR)
page.save('lunar_calendar.html'.format(YEAR))

