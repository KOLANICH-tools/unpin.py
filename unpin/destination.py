import typing
from pathlib import Path, PurePath

from .util import PathsPair


class DestinationBackend:
	__slots__ = ()

	def getFileText(self, pp: PathsPair) -> str:
		raise NotImplementedError

	def writeBack(self, pp: PathsPair, source: str) -> None:
		raise NotImplementedError

	def iterPaths(self, path: Path) -> typing.Iterator[PurePath]:
		raise NotImplementedError

	@classmethod
	def make(cls, patchee: Path) -> "DestinationBackend":
		if patchee.is_dir():
			return DirDestinationBackend()
		return ArchiveDestinationBackend()


class DirDestinationBackend(DestinationBackend):
	__slots__ = ()

	def _iterPaths(self, path: Path):
		for el in path.iterdir():
			if el.is_dir():
				yield from self._iterPaths(el)
			else:
				yield el

	def iterPaths(self, path: Path) -> typing.Iterator[PurePath]:
		for el in self._iterPaths(path):
			yield el.relative_to(path)

	def getFileText(self, pp: PathsPair) -> str:
		return (pp.root / pp.internal).read_text()

	def writeBack(self, pp: PathsPair, source: str) -> None:
		(pp.root / pp.internal).write_text(source)


class ArchiveDestinationBackend(DestinationBackend):
	__slots__ = ()

	Archive = None
	OpenFlags = None
	Source = None

	def __init__(self):
		if self.__class__.Archive is None:
			from libzip.Archive import Archive
			from libzip.enums import OpenFlags
			from libzip.Source import Source

			self.__class__.Archive = Archive
			self.__class__.OpenFlags = OpenFlags
			self.__class__.Source = Source

	def iterPaths(self, path: Path) -> typing.Iterator[PurePath]:
		with self.__class__.Archive(path, self.__class__.OpenFlags.read_only | self.__class__.OpenFlags.check) as a:
			for el in a:
				yield PurePath(el.pathName)

	def getFileText(self, pp: PathsPair) -> str:
		with self.__class__.Archive(pp.root, self.__class__.OpenFlags.read_only | self.__class__.OpenFlags.check) as a:
			f = a[pp.internal]
			appConstsText = bytes(f.stat.originalSize)
			with f as of:
				of.read(appConstsText)
			return appConstsText.decode("utf-8")

	def writeBack(self, pp: PathsPair, source: str) -> None:
		with self.__class__.Archive(pp.root, self.__class__.OpenFlags.read_write | self.__class__.OpenFlags.check) as a:
			f = a[pp.internal]
			s = self.__class__.Source.make(source.encode("utf-8"))
			f.replace(s)
