from enum import IntFlag
from typing import Generator


class _LRSpaces(IntFlag):
    NO_SPACE = 0
    L_SPACE = 1
    R_SPACE = 2


def Partition(
        text: str,
        chunckSize: int
        ) -> Generator[str, None, str]:
    '''This function partitions 'text' into chuncks of about 'chunckSize' bytes
    on the boundary of white spaces.'''
    from string import whitespace as WHITE_SPACES

    from megacodist.text import GetFirstIndexLTR, GetFirstIndexRTL

    start = 0
    while True:
        # Stripping leading white spaces from the start of this chunck...
        try:
            while text[start] in WHITE_SPACES:
                start += 1
        except IndexError:
            yield ''
            return

        end = start + chunckSize
        if end >= len(text):
            yield text[start:]
            return
        elif text[end] in WHITE_SPACES:
            yield text[start:end]
            start = end
            continue
        
        spaces = _LRSpaces.NO_SPACE
        # Finding the nearest space on the left...
        try:
            lSpace = GetFirstIndexRTL(
                text,
                WHITE_SPACES,
                start,
                end)
            spaces = spaces | _LRSpaces.L_SPACE
        except ValueError:
            pass
        
        # Finding the nearest space on the right...
        try:
            rSpace = GetFirstIndexLTR(
                text,
                WHITE_SPACES,
                end)
            spaces = spaces | _LRSpaces.R_SPACE
        except ValueError:
            pass

        match spaces:
            case 0:
                # No white space was found around the end of this chunck
                # Returning the rest of text
                yield text[start:]
                return
            case 1:
                # Found a white space only on the left of the end of
                # this chunck
                yield text[start:lSpace]
                start = lSpace
            case 2:
                # Found a white space only on the right of the end of
                # this chunck
                yield text[start:rSpace]
                start = rSpace
            case 3:
                # Found a white space on both the left and the right of
                # the end of this chunck
                if (end - lSpace) > (rSpace - end):
                    yield text[start:rSpace]
                    start = rSpace
                else:
                    yield text[start:lSpace]
                    start = lSpace


def CountWords(text: str) -> dict[str, int]:
    from collections import defaultdict
    from re import compile, IGNORECASE

    wordsCount: dict[str, int] = defaultdict(int)
    pattern = compile(r'\b\w+\b', IGNORECASE)
    for match in pattern.finditer(text):
        wordsCount[match[0].lower()] += 1
    return wordsCount


def MergeResults(
        a: dict[str, int],
        b: dict[str, int]
        ) -> dict[str, int]:
    merge = {**a}
    for word, count in b.items():
        try:
            merge[word] += count
        except KeyError:
            merge[word] = count
    return merge
