class BaseRow(object):
    def __init__(self, table, row):
        self._row = list(row)
        self._table = table

    def __len__(self):
        return len(self._row)

    def __iter__(self):
        return iter(self._row)

    def __next__(self):
        return next(self._row)

    def __repr__(self):
        return "{}<{}>".format(type(self).__name__, ', '.join(str(v) for v in self._row))

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i, j in zip(self, other):
            if i != j:
                return False
        return True

    def _append(self, item):
        self._row.append(item)

    def _insert(self, i, item):
        self._row.insert(i, item)

    def _pop(self, i=-1):
        return self._row.pop(i)

    def _remove(self, item):
        self._row.remove(item)

    def _clear(self):
        self._row.clear()

    def count(self, item):
        return self._row.count(item)

    def index(self, item, *args):
        return self._row.index(item, *args)

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._row[key]
        elif isinstance(key, str):
            index = self._table.get_column_index(key)
            return self._row[index]
        else:
            raise TypeError("row indices must be integers or slices, not {}".format(type(key).__name__))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._row[key] = value
        elif isinstance(key, str):
            index = self._table.get_column_index(key)
            self._row[index] = value
        else:
            raise TypeError("row indices must be integers or slices, not {}".format(type(key).__name__))
