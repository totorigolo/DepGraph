import os
import random
import re
import typing
from collections import OrderedDict, MutableSet, Callable


class OrderedSet(MutableSet, typing.Set):
    def __init__(self, iterable=None):
        self.data = OrderedDict()
        if iterable is not None:
            for key in iterable:
                self.data[key] = None

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def add(self, key):
        if key not in self.data:
            self.data[key] = None

    def discard(self, key):
        if key in self.data:
            self.data.pop(key)

    def __iter__(self):
        yield from self.data

    def __reversed__(self):
        yield from reversed(self.data)

    def pop(self, last=True):
        if not self:
            raise KeyError('OrderedSet is empty')
        self.data.popitem(last=last)

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class DefaultOrderedDict(OrderedDict):
    # From: https://stackoverflow.com/a/6190500/2209243
    def __init__(self, default_factory=None, *a, **kw):
        # Source: http://stackoverflow.com/a/6190500/562769
        if (default_factory is not None and
                not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


def random_hex_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return '#{}'.format(''.join(map(lambda i: format(i, '02X'), [r, g, b])))


def get_all_files_ending_with(base_path, endings, filter_regex_str=None):
    result = []

    compiled_path_regex = None
    if filter_regex_str:
        compiled_path_regex = re.compile(filter_regex_str)

    for path, _, files in sorted(os.walk(base_path)):
        for f in sorted(files):
            absolute_path = os.path.abspath(path)
            absolute_file_path = "/".join((absolute_path, f))
            if compiled_path_regex and not compiled_path_regex.search(
                    absolute_file_path):
                continue
            if any(f.endswith(ending) for ending in endings):
                result.append(absolute_file_path)
    return result
