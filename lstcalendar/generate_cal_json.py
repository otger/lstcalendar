#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import io
import json
import datetime
import pytz


class LST1Fields:
    Name = 0
    StartDate = 1
    EndDate = 2


class MagicFields:
    Name = 0
    StartDate = 1
    EndDate = 2


class CalendarSpreadsheet(object):
    def __init__(self, url, fields=LST1Fields):
        self._url = url
        self._req = None
        self.csv = None
        self.lines = None
        self.fields = fields

    def get_csv(self):
        self._req = requests.get(self._url)
        if self._req is None or self._req.status_code != 200:
            return
        print(self._req.encoding)
        self._req.encoding = 'utf-8'
        self.csv = self._req.text

    def process_csv(self):
        x = []
        for el in self.csv.split('\r\n'):
            e = el.split(',')
            x.append(e)
        self.lines = x

    def generate_json(self, path):
        if self._req is None or self._req.status_code != 200:
            return
        events = []
        for line in self.lines[1:-1]:
            start = None
            end = None
            try:
                start = datetime.datetime.strptime(line[self.fields.StartDate], "%d/%m/%Y").date()
                end = datetime.datetime.strptime(line[self.fields.EndDate], "%d/%m/%Y").date()
            except:
                print("Error parsing date of line: {}".format(line))
                tmp = "Failed parsing dates: "
                tmp += "start: {}".format(line[self.fields.StartDate])
                tmp += " - "
                tmp += "end: {}".format(line[self.fields.EndDate])
                print(tmp)

            obj = {'title': line[self.fields.Name]}

            if start is not None:
                obj['start'] = start.strftime("%Y-%m-%d")
                if end is not None:
                    # Full calendar has exclusive end date
                    end += datetime.timedelta(days=1)
                    obj['end'] = end.strftime("%Y-%m-%d")
                events.append(obj)

        # now = datetime.datetime.now(tz=pytz.utc)
        # info = {
        #     'created_on': now.strftime('%H:%M:%S %d/%m/%Y'),
        #     'events': events
        # }
        with io.open(path, 'w', encoding='utf8') as fp:
            json.dump(events, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":

    # url = 'https://docs.google.com/spreadsheets/d/157nYPNsbaGdcIkyZSrPPQiaWV16dMwAF8Aq6o3fndKA/export?format=csv'
    url = 'https://docs.google.com/spreadsheets/d/1Ct7Tm3LeG5LCx_rYS6O-uS9QTShK55mdf1_c2JPBZIw/export?format=csv'
    cs = CalendarSpreadsheet(url=url)
    cs.get_csv()
    cs.process_csv()
    cs.generate_json(path='lst1_events.json')

    # url = 'https://docs.google.com/spreadsheets/d/1ajnZZJnZsC8P3g0WKddNtptiFuuV9HwnNzG_isKzXfs/export?format=csv'
    url = 'https://docs.google.com/spreadsheets/d/1kUVgcLO7oXr4p9e-qFOcWTVJ8B3uja3T2wiS92r7Mm8/export?format=csv'
    cs = CalendarSpreadsheet(url=url, fields=MagicFields)
    cs.get_csv()
    cs.process_csv()
    cs.generate_json(path='magic_events.json')
