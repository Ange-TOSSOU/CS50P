# pip install pytest
import pytest
from twttr import shorten


def test_shorten_with_vowels():
    assert shorten("Twitter") == "Twttr"


def test_shorten_with_vowels_capitalized():
    assert shorten("Ate") == "t"


def test_shorten_with_special_characters():
    assert shorten("What's your name?") == "Wht's yr nm?"


def test_shorten_with_no_vowel():
    assert shorten("CS50") == "CS50"
