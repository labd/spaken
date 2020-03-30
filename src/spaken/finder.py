import operator
import os.path
import re
from collections import defaultdict

from packaging.utils import canonicalize_name
from packaging.version import parse as parse_version


class WheelError(ValueError):
    pass


class WheelFile:

    # Regular expression from wheel/wheelfile.py
    _wheel_info_re = re.compile(
        r"""^(?P<namever>(?P<name>.+?)-(?P<ver>.+?))(-(?P<build>\d[^-]*))?
        -(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)\.whl$""",
        re.VERBOSE)

    def __init__(self, filename):
        basename = os.path.basename(filename)
        self.filename = filename
        self._info = self._wheel_info_re.match(basename)

        if self._info is None:
            raise WheelError("Bad wheel filename {!r}".format(basename))


    @property
    def name(self):
        return canonicalize_name(self._info['name'])

    @property
    def version(self):
        return parse_version(self._info['ver'])


class WheelSet:
    def __init__(self):
        self._wheels = defaultdict(list)

    def add(self, filename):
        try:
            whl = WheelFile(filename)
        except WheelError:
            return False
        else:
            self._wheels[whl.name].append(whl)
        return True

    def find(self, requirement):
        name = canonicalize_name(requirement.name)

        candidates = self._wheels[name]
        if not candidates:
            return

        candidates.sort(key=operator.attrgetter('version'), reverse=True)
        for candidate in candidates:
            if requirement.specifier.contains(candidate.version):
                return candidate


def collect_filenames(filenames, requirements):
    wheelset = WheelSet()
    for filename in filenames:
        wheelset.add(filename)

    result = []
    missing = []
    for requirement in requirements:
        package = wheelset.find(requirement)
        if package:
            result.append(package.filename)
        else:
            missing.append(requirement)
    return result, missing
