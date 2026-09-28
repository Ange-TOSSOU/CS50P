from watch import parse

# pip install pytest
import pytest


def test_parse_iframe_with_one_attribute():
    html_element = '<iframe src="http://www.youtube.com/embed/xvFZjo5PgG0"></iframe>'
    assert parse(html_element) == "https://youtu.be/xvFZjo5PgG0"


def test_parse_iframe_with_multiple_attributes():
    html_element = '<iframe width="560" height="315" src="https://www.youtube.com/embed/xvFZjo5PgG0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    assert parse(html_element) == "https://youtu.be/xvFZjo5PgG0"


def test_parse_iframe_with_src_not_pointing_to_youtube():
    html_element = '<iframe width="560" height="315" src="https://cs50.harvard.edu/python"></iframe>'
    assert parse(html_element) == None
