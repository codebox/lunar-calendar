# Lunar Calendar

This Python utility will generate an HTML Lunar Calendar for the year that you specify.
To run the utility, pass the year as a command-line argument - for example:

```
python main.py 2018
```

The code uses the PyEphem library, which [you will need to install](https://rhodesmill.org/pyephem/#installation) before running it.

When running the utility, the file `template.html` must be present in the current working directory.

An example calendar is shown below:

<img src="https://codebox.net/assets/images/lunar_calendar.png" width="800px" alt="Lunar Calendar for 2018" /><br>
[link to generated HTML file](https://codebox.net/raw/lunar_calendar_2018.html)

As well as displaying the phase of the moon for each day of the year, the calendar lists the exact dates and times of each full moon
and new moon, highlighting any [blue moons](https://en.wikipedia.org/wiki/Blue_moon) or [black moons](https://en.wikipedia.org/wiki/Black_moon) that occur.
