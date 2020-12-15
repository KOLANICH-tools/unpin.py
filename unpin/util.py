from pathlib import Path, PurePath


class PathsPair:
	__slots__ = ("root", "internal")

	def __init__(self, root: Path, internal: PurePath) -> None:
		self.root = root
		self.internal = internal
