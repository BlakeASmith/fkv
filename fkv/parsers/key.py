from itertools import takewhile

from fkv.parsers.primatives import LookaheadIterator


KEY_START = '"\''
KEY_END = '"\''
SEPARATORS = ':='
SEPARATOR_DISTANCE = 4



def keys(stream: LookaheadIterator[str]):
    for c in stream:
        if c in KEY_START:
            key = ''.join(takewhile(lambda x: x not in KEY_END, stream))
            after = stream.lookahead(SEPARATOR_DISTANCE);
            if any(_c in SEPARATORS for _c in after):
                yield key, stream.offset



    

