# Copyright 2017, 2018 CA Technologies. All Rights Reserved.

import time
import calendar
import re

ISO_FORMAT       = '%Y-%m-%dT%H:%M:%SZ'
LOCAL_FORMAT     = '%Y-%m-%dT%H:%M:%S'

ISO_FRAC_FORMAT  = '%Y-%m-%dT%H:%M:%S.%fZ'
READABLE_FORMAT  = '%Y-%m-%d %H:%M:%S Z'
TIMEFILE_FORMAT  = READABLE_FORMAT
LOCALTIME_FORMAT = "%Y-%m-%d %I:%M:%S %p %Z"
BITBUCKET_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

class TimeStamp:

    @staticmethod
    def fromEpochSeconds(epoch_seconds):
        return TimeStamp(epoch_seconds=epoch_seconds)

    @staticmethod
    def fromEpochMilliSeconds(epoch_milleseconds):
        epoch_seconds = epoch_milleseconds/1000
        return TimeStamp(epoch_seconds=epoch_seconds)

    @staticmethod
    def fromFormattedString(value_string, format=TIMEFILE_FORMAT):
        bitbucket_cloud_time_format   = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d\d:\d\d:\d\d)\.\d{6}\+00:00$')
        bitbucket_server_time_format  = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d\d:\d\d:\d\d)\.\d{6}\+|-\d{2}:\d{2}$')
        mo = bitbucket_cloud_time_format.match(value_string)
        if mo:
            value_string, format = TimeStamp.normalizeBitbucketCloudTimestamp(value_string)
        else:
            mo = bitbucket_server_time_format.match(value_string)
            if mo:
                value_string, format = TimeStamp.normalizeBitbucketServerTimestamp(value_string)

        tz_offset_with_colon = re.compile(r'.\d(\+|-)\d\d:\d\d$')
        colon_found = tz_offset_with_colon.search(value_string)
        if colon_found:
            value_string = TimeStamp.normalizedBambooTimestamp(value_string)
        struct = TimeStamp.parseTimeStringToStruct(value_string, format=format)
        if format.endswith('Z') and not colon_found:
            epoch_seconds = calendar.timegm(struct)  # calendar.timegm assumes the struct is in UTC / GMT / Z / Zulu time
        else:
            epoch_seconds = int(time.mktime(struct)) # time.mktime assumes the struct is in local time!
        return TimeStamp(epoch_seconds=epoch_seconds)

    fromBambooTimestampString = fromFormattedString

    @staticmethod
    def now():
        return TimeStamp.fromEpochSeconds(time.time())

    @staticmethod
    def _popLastColon(time_str):
        # example of string returned by Bamboo: '2017-06-12T13:55:39.712-06:00'
        # squish the last appearing colon (in the middle of the timezone offset value)
        last_colon_idx = time_str.rfind(':')
        li = list(time_str)
        li.pop(last_colon_idx)
        return ''.join(li)

    normalizedBambooTimestamp = _popLastColon

    @staticmethod
    def fromTimeStruct(time_struct):
        return TimeStamp(epoch_seconds=calendar.timegm(time_struct))

    @staticmethod
    def getOffset():
        utc = time.gmtime()
        local = time.localtime()
        return local.tm_hour - utc.tm_hour

    @staticmethod
    def getLocalTimeZone():
        daylight = time.localtime()[8]
        tuple_idx = 0
        if daylight == 1:
            tuple_idx = 1
        return time.tzname[tuple_idx]

    @staticmethod
    def parseTimeStringToStruct(time_str, format=None):

        if format:
            try:
                return time.strptime(time_str, format)
            except Exception as exc:
                pass

        other_common_formats = ['%Y-%m-%d %H:%M:%S Z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ']
        for time_format in other_common_formats:
            try:
                return time.strptime(time_str, time_format)
            except ValueError:
                pass

        return False

    @staticmethod
    def normalizeBitbucketCloudTimestamp(value):
        value = value[:-13] + 'Z'
        return value, ISO_FORMAT

    @staticmethod
    def normalizeBitbucketServerTimestamp(value):
        pass
        # value = value[:-13] + 'Z'
        # return value, ISO_FORMAT

    def __init__(self, epoch_seconds=None):
        self.epoch_seconds = epoch_seconds
        self.readable      = self.asISOString()

    def __lt__(self, other):
        return self.epoch_seconds < other.epoch_seconds

    def __gt__(self, other):
        return self.epoch_seconds > other.epoch_seconds

    def asEpochSeconds(self):
        return self.epoch_seconds

    def asTimeStruct(self):
        return time.gmtime(self.epoch_seconds)

    def asFormattedString(self, format):
        struct = self.asTimeStruct()
        return time.strftime(format, struct)

    def asISOString(self):
        return self.asFormattedString(ISO_FORMAT)

    def asLogStamp(self):
        return self.asFormattedString(READABLE_FORMAT)

    def asLocalTime(self, format=LOCALTIME_FORMAT):
        lt_struct = time.localtime(self.epoch_seconds)
        return time.strftime(format, lt_struct)

    def minus(self, value, units='seconds'):
        value = int(value)
        delta = 0
        # legal units --> days, hours, minutes, seconds
        if units == 'seconds':
            delta = value
        elif units == 'minutes':
            delta = value * 60
        elif units == 'hours':
            delta = value * 3600
        elif 'days' in units:
            delta = value * 86400
        return TimeStamp(self.epoch_seconds - delta)

    def plus(self, value, units='seconds'):
        return self.minus(-1 * value, units=units)

