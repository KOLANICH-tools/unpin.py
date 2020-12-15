import argparse
import sys
from pathlib import Path

from . import PatchingPipeline
from .patcher import TransformsConfig


def main() -> None:
	p = argparse.ArgumentParser(prog=None, usage=None, description="A patcher for python wheel files that removes harmful constraints from them.", exit_on_error=False)
	p.add_argument(dest="path", metavar="<pathTo.whl>", type=Path, help="The path to a wheel or an unpacked dir")
	args = p.parse_args()

	cfg = TransformsConfig()
	pl = PatchingPipeline(args.path, cfg)
	report = pl()

	if report:
		for el in report:
			print(el)
	else:
		print("Nothing has been patched, everything is OK", file=sys.stderr)


if __name__ == "__main__":
	main()
