#
# 
#

from pathlib import Path

from spsc_player import ISpscPlayer
from widgets.spsc_win import SpscWin


_APP_DIR = Path(__file__).resolve().parent
"""The directory of the program."""


def EnumPlayerTypes() -> list[type[ISpscPlayer]]:
	# Declaring variables ---------------------------------
	from importlib import import_module
	from inspect import isabstract, isclass
	global _APP_DIR
	# Enumerating -----------------------------------------
	modsDir = _APP_DIR / 'spsc_player'
	modNames = list(modsDir.glob('*.py'))
	modNames = [modName.relative_to(modsDir) for modName in modNames]
	try:
		modNames.remove(Path('__init__.py'))
	except ValueError:
		pass
	spscPlayerTypes: list[type[ISpscPlayer]] = []
	for modName in modNames:
		try:
			modObj = import_module(f'spsc_player.{modName.stem}')
		except Exception:
			continue
		for item in dir(modObj):
			item = getattr(modObj, item)
			if isclass(item) and issubclass(item, ISpscPlayer) and \
					not isabstract(item):
				spscPlayerTypes.append(item)
	return spscPlayerTypes


def main() -> None:
	spscPlayerTypes = EnumPlayerTypes()
	spscWin = SpscWin(spscPlayerTypes)
	spscWin.mainloop()


if __name__ == '__main__':
    main()
