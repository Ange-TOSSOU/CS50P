from seasons import get_age_in_words

# pip install pytest
import pytest


def test_get_age_in_words_with_invalid_date_format():
    with pytest.raises(ValueError):
        get_age_in_words("January 1, 1999")


def test_get_age_in_words_with_invalid_date_ranges():
    with pytest.raises(ValueError):
        get_age_in_words("1999-15-21")


def test_get_age_in_words_with_one_year_age():
    assert (
        get_age_in_words("1999-01-01", "2000-01-01")
        == "Five hundred twenty-five thousand, six hundred minutes"
    )


def test_get_age_in_words_with_one_leap_year_age():
    assert (
        get_age_in_words("2000-01-01", "2001-01-01")
        == "Five hundred twenty-seven thousand forty minutes"
    )


def test_get_age_in_words_with_one_day_age():
    assert (
        get_age_in_words("1999-12-31", "2000-01-01")
        == "One thousand, four hundred forty minutes"
    )


def test_get_age_in_words_with_thirty_year_age():
    assert (
        get_age_in_words("1970-01-01", "2000-01-01")
        == "Fifteen million, seven hundred seventy-eight thousand eighty minutes"
    )
