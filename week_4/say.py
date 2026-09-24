# pip install cowsay
import cowsay
import sys

from sayings import hello

if len(sys.argv) == 2:
    hello(sys.argv[1])
    cowsay.trex("hello, " + sys.argv[1])