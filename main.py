import calendar
import datetime
import ephem # see http://rhodesmill.org/pyephem/
import math
import sys

'''
Lunar Calendar Generator

This utility will generate an HTML Lunar Calendar for the year that you specify.
To run the utility, pass the year as a command-line argument - for example:

    python main.py 2018

When running the utility, the file 'template.html' must be present in the current
working directory.

Latest version of source code available from:
    https://github.com/codebox/lunar-calendar

Project home page:
   https://codebox.net/pages/lunar-calendar

This source code is released under the MIT Open Source License

© 2018 Rob Dawson
'''

class Calendar:
    def __init__(self):
        self.html = open('template.html').read()

    def _replace_in_html(self, key, value):
        self.html = self.html.replace('<!-- {} -->'.format(key), value)

    def _calc_terminator_arc(self, lunation, disc_radius):
        right_of_centre = None
        lit_from_left = None
        L = None

        if lunation <= 0.25:
            L = lunation
            right_of_centre = True
            lit_from_left = False

        elif lunation <= 0.5:
            L = 0.5 - lunation
            right_of_centre = False
            lit_from_left = False

        elif lunation <= 0.75:
            L = lunation - 0.5
            right_of_centre = True
            lit_from_left = True

        else:
            L = 1 - lunation
            right_of_centre = False
            lit_from_left = True

        x = disc_radius * (1 - math.cos(2 * math.pi * L))
        n = disc_radius - x
        terminator_arc_radius = (disc_radius * disc_radius + n * n) / (2 * n)

        return terminator_arc_radius, right_of_centre, lit_from_left

    def _make_path(self, lunation, view_box_size):
        terminator_arc_radius, right_of_centre, lit_from_left = self._calc_terminator_arc(lunation, view_box_size/2)

        LIGHT_CSS_CLASS   = 'light'
        SHADOW_CSS_CLASS  = 'shadow'

        colour_left  = LIGHT_CSS_CLASS if lit_from_left else SHADOW_CSS_CLASS
        colour_right = SHADOW_CSS_CLASS if lit_from_left else LIGHT_CSS_CLASS

        move_to_top    = 'M{0},0'.format(view_box_size/2)
        disc_left_arc  = 'A {0} {0} 0 0 1 {0} 0'.format(view_box_size/2)
        disc_right_arc = 'A {0} {0} 0 0 0 {0} 0'.format(view_box_size/2)
        terminator_arc = 'A {0} {0} 0 0 {1} {2} {3}'.format(
            terminator_arc_radius, 1 if right_of_centre else 0, view_box_size/2, view_box_size)

        path_left  = '<path d="{0} {1} {2}" class="{3}"/>'.format(move_to_top, terminator_arc, disc_left_arc, colour_left)
        path_right = '<path d="{0} {1} {2}" class="{3}"/>'.format(move_to_top, terminator_arc, disc_right_arc, colour_right)

        return path_left + path_right

    def _generate_moon(self, year, month, day):
        date = ephem.Date(datetime.date(year, month, day))

        preceding_new_moon = ephem.previous_new_moon(date)
        following_new_moon = ephem.next_new_moon(date)

        lunation = (date - preceding_new_moon) / (following_new_moon - preceding_new_moon)

        VIEW_BOX_SIZE = 100
        return '<svg width="100%" viewBox="0 0 {0} {0}">{1}</svg>'.format(VIEW_BOX_SIZE, self._make_path(lunation, VIEW_BOX_SIZE))

    def _get_moon_dates(self, year, next_fn):
        start_of_year = ephem.Date(datetime.date(year, 1, 1))
        end_of_year   = ephem.Date(datetime.date(year + 1, 1, 1))

        moon_dates = []

        date = start_of_year
        previous_month = None
        while date < end_of_year:
            date = next_fn(date)
            date_and_time = date.datetime()

            formatted_date = date_and_time.strftime('%d %b %H:%M')
            second_in_month = date_and_time.month == previous_month

            moon_dates.append((formatted_date, second_in_month))
            previous_month = date_and_time.month

        return moon_dates[:-1]

    def _moon_key(self, m, d):
        return 'MOON_{:02d}_{:02d}'.format(m, d)

    def populate(self, year):
        for month in range(1, 13):
            _, days_in_month = calendar.monthrange(year, month)
            for day in range(1, days_in_month + 1):
                key = self._moon_key(month, day)
                moon = self._generate_moon(year, month, day)
                self._replace_in_html(key, moon)

        new_moon_dates  = self._get_moon_dates(year, ephem.next_new_moon)
        full_moon_dates = self._get_moon_dates(year, ephem.next_full_moon)

        def build_markup(moon_dates, second_in_month_class):
            markup = []
            for moon_date in moon_dates:
                date, second_in_month = moon_date
                markup.append('<span class="{}">{}</span>'.format(second_in_month_class if second_in_month else '', date))

            return markup

        self._replace_in_html('YEAR', str(year))

        new_moon_markup  = build_markup(new_moon_dates,  'blackMoon')
        full_moon_markup = build_markup(full_moon_dates, 'blueMoon')

        self._replace_in_html('NEW_MOONS',  ''.join(new_moon_markup))
        self._replace_in_html('FULL_MOONS', ''.join(full_moon_markup))


    def save(self, path):
        open(path, 'w').write(self.html)

if __name__ == '__main__':
    year = None
    try:
        year = int(sys.argv[1])
    except:
        print('Error, please specify a year: python {} <year>'.format(sys.argv[0]))
        sys.exit(1)
    
    cal = Calendar()
    cal.populate(year)
    output_file = 'lunar_calendar_{}.html'.format(year)
    cal.save(output_file)
    
    print('Success! Calendar saved to file {}'.format(output_file))
