from sys import stdin
from fkv.parsers.key import keys
from fkv.parsers.primatives import textstream


def main():
    for key, offset in keys(textstream(stdin)):
        print(key, offset)



