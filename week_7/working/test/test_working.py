from working import convert

# pip install pytest
import pytest


def test_convert_with_base_case():
    assert convert("9:00 AM to 5:00 PM") == "09:00 to 17:00"


def test_convert_with_one_omitted_minute():
    assert convert("9 AM to 5 PM") == "09:00 to 17:00"


def test_convert_with_two_omitted_minutes():
    assert convert("9 AM to 5:30 PM") == "09:00 to 17:30"


def test_convert_with_late_working_times():
    assert convert("10:00 AM to 8:50 PM") == "10:00 to 20:50"


def test_convert_with_late_starting_work_time():
    assert convert("10:30 PM to 8 AM") == "22:30 to 08:00"


def test_convert_with_invalid_time_range():
    with pytest.raises(ValueError):
        convert("9:60 AM to 5:60 PM")


def test_convert_with_invalid_time_format():
    with pytest.raises(ValueError):
        convert("9 AM - 5 PM")


def test_convert_with_edge_cases():
    assert convert("12 AM to 12 PM") == "00:00 to 12:00"
