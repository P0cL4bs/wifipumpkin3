from .base import BaseRow
from .enums import Alignment


class TableMetaData(BaseRow):
    def __init__(self, table, row):
        for i in row:
            self.validate(i)
        super(TableMetaData, self).__init__(table, row)

    def __setitem__(self, key, value):
        self.validate(value)
        super(TableMetaData, self).__setitem__(key, value)

    def validate(self, value):
        pass


class AlignmentMetaData(TableMetaData):
    def validate(self, value):
        if not isinstance(value, Alignment):
            error_msg = ("allowed values for alignment are: "
                         + ', '.join("{}.{}".format(type(self).__name__, i.name) for i in Alignment)
                         + ', was {}'.format(value))
            raise TypeError(error_msg)


class PositiveIntegerMetaData(TableMetaData):
    def validate(self, value):
        if isinstance(value, int) and value >= 0:
            pass
        else:
            raise TypeError("Value must a non-negative integer, was {}".format(value))
