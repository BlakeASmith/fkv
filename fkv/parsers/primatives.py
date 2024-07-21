
from typing import BinaryIO, override 
from collections.abc import Iterator
from collections import deque


class ByteStream(Iterator[str]):
    def __init__(self, io: BinaryIO, chunk_size: int = 1024, max_lookbehind: int = 10) -> None:
        self._io = io
        self._chunk_size = chunk_size
        self._chunk = b""
        self._chunk_iter = iter(self._chunk)
        self._offset = 0
        self.__stop = False
        self.__ahead = deque[int]()
        self.__behind: list[int] = []
        self.__max_lookbehind = max_lookbehind


    def __read_chunk(self):
        self._chunk = self._io.read(self._chunk_size)
        self._chunk_iter = iter(self._chunk)
        self._offset = self._io.tell() #TODO: allow setting the intial offset
        if not self._chunk:
            self.__stop = True

    @override
    def __iter__(self):
        return self


    def lookahead(self, n: int = 1) -> str:
        _peek = [self.__next() for _ in range(n)]
        for _c in _peek:
            self.__ahead.appendleft(_c)
        return ''.join(chr(_c) for _c in _peek)

    def lookbehind(self, n: int = 1) -> str:
        if n > self.__max_lookbehind:
            raise ValueError("Cannot look behind passed buffer size")
        v = ''.join(chr(_c) for _c in self.__behind[-n:])
        return v

    @override
    def __next__(self) -> str:
        self._offset += 1
        return chr(self.__next())

    def __next(self) -> int:
        if self.__ahead:
            return self.__ahead.pop()

        try:
            _next = next(self._chunk_iter)
            self.__behind.append(_next)
            if len(self.__behind) > self.__max_lookbehind:
                _ = self.__behind.pop()
            return _next
        except StopIteration as ex:
            self.__read_chunk()
            if self.__stop:
                raise ex
            return self.__next()
