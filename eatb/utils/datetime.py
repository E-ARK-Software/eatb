#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import os
import pytz
from pytz import timezone
import time


DT_ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

DT_ISO_FMT_SEC_PREC = '%Y-%m-%dT%H:%M:%S'

TS_FORMAT = '%Y-%m-%d %H:%M:%S'

EU_UI_FORMAT = '%d.%m.%Y %H:%M:%S'

DATE_DMY = '%d.%m.%Y'

DT_ISO_FORMAT_FILENAME = "%Y%m%d-%H%M%SZ"

TASK_EXEC_TIMES = {}


class LengthBasedDateFormat(object):
    date_str = None

    def __init__(self, date_str):
        self.date_str = date_str

    def reformat(self, target_fmt='%Y-%m-%dT%H:%M:%SZ'):
        if not self.date_str:
            return "1970-01-01T00:00:00Z"
        return self.format(target_fmt, len(self.date_str))

    def format(self, target_fmt, length=10):
        fmt = "%d.%m.%Y" if length == 10 else "%d%m%Y" if length == 6 else "%Y"
        return reformat_date_string(fmt, self.date_str, target_fmt)

def reformat_date_string(origin_fmt, origin_dts, target_fmt):
    return datetime.strptime(origin_dts, origin_fmt).strftime(target_fmt)


def get_date_from_iso_str(origin_fmt, origin_dts):
    return datetime.strptime(origin_fmt, origin_dts)


def get_file_ctime_iso_date_str(file_path, fmt=DT_ISO_FORMAT, wd=None):
    fp = file_path
    path = fp if wd is None else os.path.join(wd, fp)
    dt = timezone('Europe/Vienna').localize(datetime.fromtimestamp(os.path.getctime(path)).replace(microsecond=0))
    return dt.strftime(fmt)


def ts_date(fmt=TS_FORMAT):
    return datetime.fromtimestamp(time.time()).strftime(fmt)


def date_format(date, fmt=DT_ISO_FORMAT):
    return date.strftime(fmt)


def current_timestamp(fmt=DT_ISO_FMT_SEC_PREC, time_zone_id='Europe/Vienna'):
    dt = datetime.now(tz=timezone(time_zone_id))
    return dt.strftime(fmt)


def current_date(time_zone_id='Europe/Vienna'):
    return datetime.now(tz=timezone(time_zone_id))


def get_current_milli_time():
    millis = int(round(time.time() * 1000))
    return millis


def get_local_datetime_now():
    return datetime.now(tz=pytz.timezone('Europe/Vienna'))
