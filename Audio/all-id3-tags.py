"""Enumerating all tags out of an ID3 metadata container of an MP3 audio
file.
"""

import re
from mutagen.id3 import ID3


def main() -> None:
    REGEX_TAG_VALUE = r'^(?P<tag>\w+):(?P<value>.+)$'
    tagValuePat = re.compile(REGEX_TAG_VALUE)

    mp3File = input('Enter an MP3 file: ')
    id3 = ID3(mp3File)
    # Enumerating all available tags...
    for tag in id3:
        print(tag)
        try:
            # Enumerating values of a multi-valued tag...
            num = 1
            for value in id3[tag]:
                print(f'\t{num}. {value}')
                num += 1
        except TypeError:
            # Parsing single-valued tags...
            match = tagValuePat.match(tag)
            if match:
                print(match['tag'])
                print(match['value'])
            else:
                # Reporting an error...
                pass

if __name__ == '__main__':
    main()