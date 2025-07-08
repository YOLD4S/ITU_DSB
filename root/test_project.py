from datetime import datetime, timedelta
from root.project import time_resolver, wait_until, course_names_by_crns


def test_time_resolver():
    assert time_resolver("31/12/2005 12.59.59") == datetime(2005, 12, 31, 12, 59, 59)
    assert time_resolver("31/12/2005    12.59.59") == datetime(2005, 12, 31, 12, 59, 59)
    try:
        assert time_resolver("31.12.2005 12.59.59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass
    try:
        assert time_resolver("31/12/2005 12:59:59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass
    try:
        assert time_resolver("32/12/2005 12.59.59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass
    try:
        assert time_resolver("31/25/2005 12.59.59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass
    try:
        assert time_resolver("10/12/20054 12.59.59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass
    try:
        assert time_resolver("15/05/2013 12.60.59") == datetime(2005, 12, 30, 12, 59, 59)
        assert False
    except:
        pass


def test_wait_until():
    now = datetime.now()
    wait_until(datetime.now() + timedelta(seconds=5))
    assert (datetime.now() - (now + timedelta(seconds=5))).seconds == 0


def test_course_names_by_crns():
    data = course_names_by_crns()
    assert len(data) > 0
    assert type(data) == dict
    assert type(data[list(data.keys())[0]]) == str
    assert data['30310'] == "BLG 223E Data Structures"
    try:
        s = data['12345']
        assert False
    except KeyError:
        pass