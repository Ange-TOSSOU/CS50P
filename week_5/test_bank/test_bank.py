# pip install pytest
import pytest
from bank import value


def test_with_just_hello():
    assert value("Hello") == 0


def test_with_hello_at_start():
    assert value("Hello, Newman") == 0


def test_with_h_at_start():
    assert value("How you doing?") == 20


def test_with_no_hello_nor_h_at_start():
    assert value("What's happening?") == 100
