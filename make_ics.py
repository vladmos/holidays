# coding: utf-8
import requests
import datetime
from xml.etree import ElementTree
from cStringIO import StringIO
from hashlib import md5

COUNTRIES = {
    'ru': 225,
}
CALENDAR_URL = 'http://calendar.yandex.ru/export/holidays.xml?start_date=2014-01-01&end_date=%(year)s-12-31&' +\
               'country_id=%(country)s&out_mode=overrides'


def fetch_feed():
    year = datetime.date.today().year
    url = CALENDAR_URL % {'year': year + 1, 'country': COUNTRIES['ru']}
    xml = requests.get(url).text.encode('utf-8')
    tree = ElementTree.fromstring(xml)
    days = tree.find('get-holidays').find('days').findall('day')
    return days


def make_ics(feed):
    io = StringIO()
    io.write('BEGIN:VCALENDAR\n')
    io.write('CALSCALE:GREGORIAN\n')
    io.write('PRODID:fulc.ru\n')
    io.write('VERSION:2.0\n')
    io.write('X-WR-CALNAME:Праздники России\n')

    for day in feed:
        attributes = day.attrib
        date = attributes['date'].replace('-', '')  # 2015-01-01 -> 20150101
        name = attributes['holiday-name'].encode('utf-8')
        is_holiday = attributes['is-holiday'] == '1'
        if not is_holiday:
            name = 'Рабочий день: ' + name
        uid = md5(name + date).hexdigest()

        io.write('BEGIN:VEVENT\n')
        io.write('CATEGORIES:каникулы\n')
        io.write('DTSTAMP:%sT000000Z\n' % date)
        io.write('DTSTART;VALUE=DATE:%s\n' % date)
        io.write('CLASS:PUBLIC\n')
        io.write('SEQUENCE:0\n')
        io.write('SUMMARY;LANGUAGE=ru:%s\n' % name)
        io.write('TRANSP:TRANSPARENT\n')
        io.write('UID:%s\n' % uid)
        io.write('END:VEVENT\n')

    io.write('END:VCALENDAR')
    return io.getvalue()


def main():
    feed = fetch_feed()
    ics = make_ics(feed)
    with open('ru_holidays.ics', 'w') as f:
        f.write(ics)


if __name__ == '__main__':
    main()
