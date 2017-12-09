
from sortedcontainers import SortedList, SortedListWithKey

"""
sortedcontainers.SortedDict just wasn't working for me
"""


class SortedDict(dict):
    def __init__(self, key=None, default=None):
        if default:
            super().__init__(default)
        else:
            super().__init__()

        self._sort_key = key
        if key:
            self._keys = SortedListWithKey(key=key)
        else:
            self._keys = SortedList()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self._keys:
            self._keys.add(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def copy(self):
        return SortedDict(self)

    """ Because I'm lazy, the following 3 methods return generators rather
    than views. Doesn't matter (for this project). """

    def items(self):
        """ Return items in sorted order. """
        for key in self._keys:
            yield (key, self[key])

    def keys(self):
        """ Return keys in sorted order. """
        return self._keys

    def values(self):
        """ Return values in sorted order. """
        for key in self._keys:
            return self[key]

    def mutate_val(self, key, func):
        """ If you're going to mutate a value in the dict, do the mutation in a function and pass
        it to this method, along with the key to the value it's going to mutate.
        This rule must be followed, else all hell will break loose. """
        """ This function exists as an artifact of strange behaviour of SortedList and SortedListWithKey
        as far as I can tell, their .remove(val) relies on the key(val) being the same as when it
         was inserted. So, mutable values are an issue. """
        self._keys.remove(key)
        func()
        self._keys.add(key)


