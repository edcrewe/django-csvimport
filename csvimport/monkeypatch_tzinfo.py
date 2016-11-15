""" Monkeypatch so that dates outside of 1970-2037 can be imported for
    the DB backends that do not handle this
"""
import time


def _isdst(self, dt):
    """ Monkeypatch from https://code.djangoproject.com/ticket/3418
        since sqlite and other backends still have this issue in django 1.6
    """
    year = dt.year
    if int(year) < 1970:
        year = 1970
    if int(year) > 2037:
        year = 2037
    tt = (year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)
    try:
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0
    except OverflowError:
        pass
    raise Exception('Cannot process dates from %s' % year)

try:
    from django.utils.timezone import ReferenceLocalTimezone
    ReferenceLocalTimezone._isdst = _isdst
except:
    # Don't patch it if it isnt there to be patched!
    pass
