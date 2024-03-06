#
# This code snippet dynamically loads a module. The module must reside
# inside the folder of the application.
#
from msvcrt import getwche


def main() -> None:
    # Declaring variables -----------------------------
    from importlib import import_module
    from types import ModuleType
    mp3Mod: ModuleType
    # Functioning -------------------------------------
    mp3Mod = import_module('foo')
    print(mp3Mod)
    print('Items inside the module:')
    for item in dir(mp3Mod):
        print(item)


if __name__ == '__main__':
    main()
    print('Press any key to quit:', end='', flush=True)
    getwche()