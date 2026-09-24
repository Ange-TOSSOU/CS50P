# pip install pytest
import pytest
from plates import is_valid


def test_basic_example():
    assert is_valid("CS50") == True


def test_first_number_used_cannot_be_zeo():
    assert is_valid("CS05") == False


def test_numbers_cannot_be_used_in_middle():
    assert is_valid("CS50P") == False


def test_dot_is_not_allowed():
    assert is_valid("PI3.14") == False


def test_less_than_two_characters_is_not_allowed():
    assert is_valid("H") == False


def test_more_than_six_characters_is_not_allowed():
    assert is_valid("OUTATIME") == False


def test_starting_with_other_than_letters_is_not_allowed():
    assert is_valid("50") == False
