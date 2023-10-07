import sys
import typing
from io import BytesIO, StringIO
from pathlib import Path, PurePath

import distlib.metadata

from .destination import DestinationBackend
from .patcher import PatchedDependency, TransformsConfig, patchRunRequires
from .util import PathsPair

# pylint:disable=too-few-public-methods

from warnings import warn

warn("We have moved from M$ GitHub to https://codeberg.org/KOLANICH-tools/unpin.py , read why on https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo .")


class ParsedAST:
	__slots__ = ("ast", "pp")

	def __init__(self, pp: PathsPair) -> None:
		self.pp = pp
		self.ast = None

	def load(self, destinationBackend: DestinationBackend) -> None:
		source = destinationBackend.getFileText(self.pp)
		self.ast = self.parse(source)

	def dump(self, destinationBackend: DestinationBackend) -> None:
		res = self.serialize(self.ast)
		destinationBackend.writeBack(self.pp, res)

	def parse(self, source: str) -> distlib.metadata.Metadata:
		raise NotImplementedError

	def serialize(self, ast: distlib.metadata.Metadata, desiredSize: typing.Optional[int] = None) -> str:
		raise NotImplementedError


class ParsedMetadataAST(ParsedAST):
	def parse(self, source: str) -> distlib.metadata.Metadata:
		with StringIO(source) as ff:
			return distlib.metadata.Metadata(fileobj=ff)

	def serialize(self, ast: distlib.metadata.Metadata, desiredSize: typing.Optional[int] = None) -> str:
		# pylint:disable=protected-access
		d = ast._legacy["Description"].encode("utf-8")
		del ast._legacy["Description"]
		descrLen = len(d) + 1  # 1 for "\n"

		with StringIO() as f:
			ast.write(fileobj=f, legacy=True)
			firstPart = f.getvalue().encode("utf-8")

		mdl = len(firstPart)
		predictedLength = descrLen + mdl

		if desiredSize is None:
			desiredSize = predictedLength

		res = bytearray(desiredSize)
		res[0:mdl] = firstPart

		paddingLength = desiredSize - predictedLength

		if paddingLength < 0:
			res[mdl + 1] = b"\n"
			raise ValueError("The result has greater length, will not be able to replace in place", predictedLength, res[: mdl + 1] + d)

		res[mdl : mdl + paddingLength + 1] = b"\n" * (paddingLength + 1)
		res[mdl + paddingLength + 1 :] = d
		return res.decode("utf-8")


specialDirSuffixes = {".dist-info"}


class PatchingPipeline:
	__slots__ = ("patchee", "cfg", "destinationBackend", "metadata")

	def __init__(self, patchee: Path, cfg: TransformsConfig, destinationBackend: typing.Optional[DestinationBackend] = None) -> None:
		self.patchee = patchee
		self.cfg = cfg
		if destinationBackend is None:
			destinationBackend = DestinationBackend.make(patchee)
		self.destinationBackend = destinationBackend
		self.metadata = None

	def __call__(self) -> typing.List[PatchedDependency]:
		self.load()
		report = self.patch()
		if report:
			self.dump()
		return report

	def load(self) -> None:
		for p in self.destinationBackend.iterPaths(self.patchee):
			if p.parent.suffix in specialDirSuffixes:
				if p.name == "METADATA":
					self.metadata = ParsedMetadataAST(PathsPair(self.patchee, p))
					break

		self.metadata.load(self.destinationBackend)

	def patch(self) -> typing.List[PatchedDependency]:
		return patchRunRequires(self.metadata.ast, self.cfg)

	def dump(self) -> None:
		self.metadata.dump(self.destinationBackend)
