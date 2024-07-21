
from io import BytesIO, IOBase, TextIOBase
from typing import override, Any
from collections.abc import Iterator
from collections import deque


class LookaheadIterator[T](Iterator[T]):
    def __init__(self, _iter: Iterator[T], max_lookbehind: int = 10):
        self._offset = 0
        self._iter = _iter
        self.__ahead = deque[T]()
        self.__behind: list[T] = []
        self.__max_lookbehind = max_lookbehind

    @property
    def offset(self):
        return self._offset

    @override
    def __next__(self) -> T:
        self._offset += 1
        return self.__next()


    def __next(self) -> T:
        if self.__ahead:
            return self.__ahead.pop()
        _next = next(self._iter)
        self.__behind.append(_next)
        if len(self.__behind) > self.__max_lookbehind:
            _ = self.__behind.pop()
        return _next

    def lookahead(self, n: int = 1) -> list[T]:
        _peek: list[T] = []
        for _ in range(n):
            try:
                _peek.append(self.__next())
            except StopIteration:
                break
        for _c in _peek:
            self.__ahead.appendleft(_c)
        return _peek

    def lookbehind(self, n: int = 1) -> list[T]:
        if n > self.__max_lookbehind:
            raise ValueError("Cannot look behind passed buffer size")
        v = self.__behind[-n:]
        return v


class ChunkedIOIterator[T](Iterator[T]):
    def __init__(self, io: IOBase, chunk_size: int = 1024):
        self._io = io
        self._chunk_size = chunk_size
        self._chunk: Iterator[Any] = self._io.read(self._chunk_size)
        self._iter: Iterator[T] = iter(self._chunk)

    @override
    def __next__(self) -> T:
        try:
            return next(self._iter)
        except StopIteration as ex:
            self._chunk = self._io.read(self._chunk_size)
            self._iter = iter(self._chunk)

            if not self._chunk:
                raise ex

            return next(self)


def textstream(text: TextIOBase, chunk_size: int = 1024) -> LookaheadIterator[str]:
    io_iterator = ChunkedIOIterator[str](text, chunk_size) 
    return LookaheadIterator(io_iterator)

def bytestream(binary: BytesIO, chunk_size: int = 1024) -> LookaheadIterator[str]:
    io_iterator = ChunkedIOIterator[int](binary, chunk_size) 
    return LookaheadIterator[str](chr(_c) for _c in io_iterator)
