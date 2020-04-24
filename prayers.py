#!/usr/bin/env python3

import sys
import os
import argparse
import requests
from datetime import datetime
import json

city = 'NewYork'
country = 'US'
prayers_url = 'http://api.aladhan.com/v1/timingsByCity?method=2&city={}&country={}'.format(city, country)
prayers_file = os.path.expanduser('~/.config/prayers')
prayers_arabic = {
    'Fajr': 'الفجر',
    'Sunrise': 'الشروق',
    'Dhuhr': 'الظهر',
    'Asr': 'العصر',
    'Maghrib': 'المغرب',
    'Isha': 'العشاء'
}

def update():
    try:
        prayers_info = requests.get(prayers_url).json()
        with open(prayers_file, 'w') as f:
            json.dump(prayers_info, f)
        return prayers_info
    except:
        return None

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--next', action='store_true', help='Show time remaining for next salah')
    parser.add_argument('--update', action='store_true', help='Force update of prayers file')
    args = parser.parse_args(arguments)
    
    if args.update or not os.path.exists(prayers_file):
        prayers_info = update()
    else:
        with open(prayers_file, 'r') as f:
            prayers_info = json.load(f)
    
    if not prayers_info:
        return
    
    prayers_date = datetime.fromtimestamp(int(prayers_info['data']['date']['timestamp'])).date()
    if prayers_date < datetime.today().date():
        prayers_info = update()
        if not prayers_info:
            return
    
    items = filter(lambda item: item[0] in prayers_arabic, prayers_info['data']['timings'].items())
    items = [(prayers_arabic[item[0]], datetime.combine(prayers_date, datetime.strptime(item[1], '%H:%M').time())) for item in items]
    
    if args.next:
        now = datetime.now()
        next_prayers = list(filter(lambda item: item[1] > now, items))
        if not next_prayers:
            next_prayers.append(items[0])
        next_prayer = min(next_prayers, key=lambda item: abs(item[1] - now))
        time_remaining = next_prayer[1] - now
        print(next_prayer[0], next_prayer[1].strftime('%-I:%M%P'), '\n', 'متبقي', ':'.join(str(time_remaining).split(':')[:2]))
    else:
        for item in items:
            print(item[0], item[1].strftime('%I:%M%P'))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
