from um import count

# pip install pytest
import pytest


def test_count_with_um_at_the_beginning():
    assert count("um, hello dude !") == 1


def test_count_with_um_at_the_end():
    assert count("hello dude, um") == 1


def test_count_with_multiple_um():
    assert count("um, hello ... um dude, um") == 3


def test_count_um_with_dots():
    assert count("um...") == 1


def test_count_with_um_only():
    assert count("um") == 1


def test_count_with_um_as_substring():
    assert count("yum") == 0


def test_count_with_um_as_part():
    assert count("yummy") == 0


def test_count_with_no_um():
    assert count("hello") == 0


def test_count_case_insensitive():
    assert count("Um, thanks for the album.") == 1


def test_count_case_insensitive_with_edge_case():
    assert count("Um, thanks, um...") == 2


def test_count_um_with_question_mark():
    assert count("Um?") == 1
