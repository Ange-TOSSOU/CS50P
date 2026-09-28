from numb3rs import validate

# pip install pytest
import pytest


def test_validate_with_localhost():
    assert validate("127.0.0.1") == True


def test_validate_with_broadcast():
    assert validate("255.255.255.255") == True


def test_validate_with_wildcard():
    assert validate("0.0.0.0") == True


def test_validate_with_invalid_ip():
    assert validate("275.3.6.28") == False


def test_validate_with_letters():
    assert validate("cat.0.0.1") == False


def test_validate_with_leading_zero():
    assert validate("127.0.0.001") == False


def test_validate_with_more_than_four_bytes():
    assert validate("127.0.0.1.1") == False


def test_validate_with_less_than_four_bytes():
    assert validate("127.0.0") == False


def test_validate_with_omission():
    assert validate("127..0.1") == False
