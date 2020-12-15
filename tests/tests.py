#!/usr/bin/env python3
import itertools
import re
import sys
import unittest
from pathlib import Path

from packaging.specifiers import SpecifierSet

sys.path.insert(0, str(Path(__file__).parent.parent))

from collections import OrderedDict

dict = OrderedDict


import unpin
from unpin import *
from unpin.patcher import TransformsConfig, filterSpecifiers


class Tests(unittest.TestCase):
	def testUnpinningSingleSpecifierSet(self):
		tcfg = TransformsConfig()
		sset = SpecifierSet(">=3, < 10")
		filterSpecifiers(sset, tcfg)
		str(sset) == ">=3"


if __name__ == "__main__":
	unittest.main()
