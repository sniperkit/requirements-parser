import os
import json
from nose.tools import raises, assert_equal
import warnings

from requirements import parse

REQFILE_DIR = os.path.join(os.path.dirname(__file__), 'reqfiles')


def listify(iterable):
    out = []
    for item in iterable:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(item[key], (tuple, list)):
                    if key in ('extras', 'specs'):
                        # enforce predictability
                        item[key] = sorted(listify(value))
                    else:
                        item[key] = listify(value)
        elif isinstance(item, (tuple, list)):
            item = listify(item)
        out.append(item)
    return out


def test_requirement_files():
    for fn in os.listdir(REQFILE_DIR):
        def fancy(f):
            f.description = "%s.%s: %s" % (f.__module__, f.__name__, fn)
            return f

        @fancy
        @raises(ValueError)
        def check_fail(s):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                list([dict(r) for r in parse(s)])

        @fancy
        def check(s, expected):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                assert_equal(listify(dict(r) for r in parse(s)), expected)

        fp = os.path.join(REQFILE_DIR, fn)

        # skip ".expected" files
        if not os.path.isfile(fp) or not fp.endswith('.txt'):
            continue

        if 'fail' in fn:
            yield check_fail, open(fp)
        else:
            with open(fp[:-4] + '.expected', 'r') as f2:
                expected = json.loads(f2.read())
                yield check, open(fp), expected
