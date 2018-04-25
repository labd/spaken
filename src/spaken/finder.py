import operator
from collections import defaultdict

from packaging.utils import canonicalize_name
from packaging.version import parse as parse_version
from wheel.install import WheelFile as _WheelFile
from wheel.install import BadWheelFile


class WheelFile:

    def __init__(self, filename):
        self.filename = filename

        whl = _WheelFile(self.filename)
        self._info = whl.parsed_filename.groupdict()

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
        except BadWheelFile:
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
