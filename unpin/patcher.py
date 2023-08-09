import typing

from distlib.metadata import Metadata
from packaging.specifiers import Specifier, SpecifierSet

# pylint:disable=too-many-arguments,too-few-public-methods

__all__ = ("TransformsConfig", "patchRunRequires", "PatchedDependency")


class TransformsConfig:
	__slots__ = ("lt", "neq", "eq", "ge", "aeq")

	def __init__(self, lt: bool = True, neq: bool = True, eq: bool = True, aeq: bool = True, ge: bool = False) -> None:
		self.lt = lt
		self.neq = neq
		self.eq = eq
		self.aeq = aeq
		self.ge = ge


def constrMatches(s: Specifier, cfg: TransformsConfig) -> bool:
	e = s.operator
	if cfg.lt and e.startswith("<"):
		return True
	if e[1] == "=":
		if cfg.neq and e[0] == "=":
			return True
		if cfg.eq and e[0] == "!":
			return True
		if cfg.aeq and e[0] == "~":
			return True
		if cfg.ge and e[0] == ">":
			return True
	return False


def constrFilter(e: Specifier, cfg: TransformsConfig) -> typing.Optional[Specifier]:
	if constrMatches(e, cfg):
		return None
	return e


class PatchedDependency:
	__slots__ = ("dep", "conds")

	def __init__(self, dep: "Dependency") -> None:
		self.dep = dep
		self.conds = []  # type: typing.List[PatchedCondition]

	def __iter__(self):
		yield self.dep
		yield self.conds

	def __bool__(self) -> bool:
		return bool(self.conds)

	def __str__(self) -> str:
		return str(self.dep) + "\n\t" + "\n\t".join(str(el) for el in self.conds)

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(el) for el in self) + ")"


class PatchedCondition:
	__slots__ = ("was", "become")

	def __init__(self, was: typing.Optional[Specifier], become: typing.Optional[Specifier]) -> None:
		self.was = was
		self.become = become

	def __iter__(self):
		yield self.was
		yield self.become

	def __str__(self) -> str:
		if self.become is None:
			return "- " + str(self.was)
		if self.was is None:
			return "- " + str(self.become)
		return str(self.was) + " -> " + str(self.become)

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(el) for el in self) + ")"


def parseVersionConstrs(versionConstrs: str) -> SpecifierSet:
	if versionConstrs and versionConstrs[0] == "(" and versionConstrs[-1] == ")":
		versionConstrs = versionConstrs[1:-1].strip()
	if versionConstrs:
		return SpecifierSet(versionConstrs, prereleases=True)

	return SpecifierSet("")


class Dependency:
	__slots__ = ("name", "specifiers", "rest", "envMarkers")

	def __init__(self, name: str, specifiers: SpecifierSet, rest: typing.List[typing.Any], envMarkers) -> None:
		self.name = name
		self.specifiers = specifiers
		self.rest = rest
		self.envMarkers = envMarkers

	def __iter__(self):
		for k in __class__.__slots__:
			yield getattr(self, k)

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(el) for el in self) + ")"

	def __str__(self) -> str:
		res = [self.name, " "]
		if self.specifiers:
			res.extend((serializeVersionConstraints(self.specifiers), " "))

		if self.envMarkers is not None:
			res.extend((";", self.envMarkers, " "))

		if self.rest:
			res.append(" ".join(self.rest))

		return "".join(res)

	@classmethod
	def parse(cls, dep: str) -> typing.Optional["Dependency"]:
		depSplit = [c.strip() for c in dep.split(" ")]
		if len(depSplit) > 1:
			constr = depSplit[1].split(";", 1)  # env marker
			specifiers = parseVersionConstrs(constr[0].strip())
			if len(constr) > 1:
				envMarkers = constr[1]
			else:
				envMarkers = None

			parsedDep = cls(name=depSplit[0].strip(), specifiers=specifiers, rest=depSplit[2:], envMarkers=envMarkers)
			return parsedDep

		return None


def filterSpecifiers(specifiers: SpecifierSet, cfg: TransformsConfig) -> typing.List[PatchedCondition]:
	conds = []
	res = []
	for c in specifiers._specs:
		newC = constrFilter(c, cfg)
		if newC:
			res.append(newC)
		if newC != c:
			conds.append(PatchedCondition(c, newC))

	specifiers._specs = specifiers._specs.__class__(res)
	return conds


def filterVersionsConstrs(dep: Dependency, cfg: TransformsConfig) -> PatchedDependency:
	currDepRep = PatchedDependency(dep)
	currDepRep.conds.extend(filterSpecifiers(dep.specifiers, cfg))
	return currDepRep


def serializeVersionConstraints(parsedVersionConstrs: SpecifierSet) -> str:
	return "(" + str(parsedVersionConstrs) + ")"


def patchRunRequires(m: Metadata, cfg: TransformsConfig) -> typing.List[PatchedDependency]:
	report = []
	rr = m.run_requires  # emits a copy
	for i, dep in enumerate(rr):
		pd = Dependency.parse(dep)
		if pd is not None:
			if pd.specifiers:
				currDepRep = filterVersionsConstrs(pd, cfg)
				if currDepRep:
					rr[i] = str(pd)
					m.run_requires = rr
					report.append(currDepRep)
	return report
