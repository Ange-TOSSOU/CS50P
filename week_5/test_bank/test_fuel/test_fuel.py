# pip install pytest
import pytest
from fuel import *


def test_gauge_when_value_is_one():
    assert gauge(1) == "E"


def test_gauge_when_value_is_less_than_one():
    assert gauge(0) == "E"


def test_gauge_when_value_is_99():
    assert gauge(99) == "F"


def test_gauge_when_value_is_more_than_99():
    assert gauge(100) == "F"


def test_gauge_when_value_is_between_1_and_99():
    assert gauge(13) == "13%"


def test_convert_when_x_is_negative():
    with pytest.raises(ValueError):
        convert("-1/3")


def test_convert_when_x_is_0():
    assert convert("0/3") == 0


def test_convert_when_y_is_negative():
    with pytest.raises(ValueError):
        convert("1/-3")


def test_convert_when_y_is_0():
    with pytest.raises(ZeroDivisionError):
        convert("1/0")


def test_convert_when_x_is_not_integer():
    with pytest.raises(ValueError):
        convert("a/3")


def test_convert_when_y_is_not_integer():
    with pytest.raises(ValueError):
        convert("1/b")


def test_convert_when_x_is_greater_than_y():
    with pytest.raises(ValueError):
        convert("3/2")


def test_convert():
    assert convert("1/4") == 25
