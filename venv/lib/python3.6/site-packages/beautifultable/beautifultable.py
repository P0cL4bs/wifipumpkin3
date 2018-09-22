"""This module provides BeautifulTable class intended for printing Tabular data to terminals.

Example
-------
>>> from beautifultable import BeautifulTable
>>> table = BeautifulTable()
>>> table.column_headers = ['1st column', '2nd column']
>>> for i in range(5):
...    table.append_row([i, i*i])
...
>>> print(table)
+------------+------------+
| 1st column | 2nd column |
+------------+------------+
|     0      |     0      |
+------------+------------+
|     1      |     1      |
+------------+------------+
|     2      |     4      |
+------------+------------+
|     3      |     9      |
+------------+------------+
|     4      |     16     |
+------------+------------+
"""
from __future__ import division
import itertools
import copy
import operator
import collections

from .utils import convert_to_numeric, raise_suppressed
from .rows import RowData, HeaderData
from .meta import AlignmentMetaData, PositiveIntegerMetaData
from .enums import WidthExceedPolicy, Alignment, SignMode, Style

__all__ = ['BeautifulTable']


class Column:
    def __init__(self, table, column):
        self._column = column
        self._table = table

    def __getitem__(self, key):
        if isinstance(key, int):
            return next(itertools.islice(self._column, key, None))
        elif isinstance(key, slice):
            return itertools.islice(self._column, key.start, key.stop, key.step)
        else:
            raise TypeError("column indices must be integers or slices, not {}".format(type(key).__name__))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._column[key] = value
        else:
            raise TypeError("column indices must be integers or slices, not {}".format(type(key).__name__))


class BeautifulTable(object):
    """Utility Class to print data in tabular format to terminal.

    The instance attributes can be used to customize the look of the
    table. To disable a behaviour, just set its corresponding attribute
    to an empty string. For example, if Top border should not be drawn,
    set `top_border_char` to ''.

    Parameters
    ----------
    max_width: int, optional
        maximum width of the table in number of characters.

    default_alignment : int, optional
        Default alignment for new columns.

    default_padding : int, optional
        Default width of the left and right padding for new columns.

    Attributes
    ----------
    column_count
    sign_mode
    width_exceed_policy
    default_alignment
    default_padding
    column_widths
    column_headers
    column_alignments
    left_padding_widths
    right_padding_widths

    left_border_char : str
        Character used to draw the left border.

    right_border_char : str
        Character used to draw the right border.

    top_border_char : str
        Character used to draw the top border.

    bottom_border_char : str
        Character used to draw the bottom border.

    header_seperator_char : str
        Character used to draw the line seperating Header from data.

    row_seperator_char : str
        Character used to draw the line seperating two rows.

    column_seperator_char : str
        Character used to draw the line seperating two columns.

    intersection_char : str
        Character used to draw intersection of a vertical and horizontal
        line. Disabling it just draws the horizontal line char in it's place.

    numeric_precision : int
        All float values will have maximum number of digits after the decimal,
        capped by this value(Default 3).

    serialno : bool
        Whether automatically generated serial number should be printed for
        each row(Default False).
    """

    WEP_WRAP = WidthExceedPolicy.WEP_WRAP
    WEP_STRIP = WidthExceedPolicy.WEP_STRIP
    WEP_ELLIPSIS = WidthExceedPolicy.WEP_ELLIPSIS
    SM_PLUS = SignMode.SM_PLUS
    SM_MINUS = SignMode.SM_MINUS
    SM_SPACE = SignMode.SM_SPACE
    ALIGN_LEFT = Alignment.ALIGN_LEFT
    ALIGN_CENTER = Alignment.ALIGN_CENTER
    ALIGN_RIGHT = Alignment.ALIGN_RIGHT
    STYLE_DEFAULT = Style.STYLE_DEFAULT
    STYLE_DOTTED = Style.STYLE_DOTTED
    STYLE_SEPERATED = Style.STYLE_SEPERATED
    STYLE_COMPACT = Style.STYLE_COMPACT
    STYLE_MYSQL = Style.STYLE_MYSQL
    STYLE_MARKDOWN = Style.STYLE_MARKDOWN
    STYLE_RESTRUCTURED_TEXT = Style.STYLE_RESTRUCTURED_TEXT

    def __init__(self, max_width=80, default_alignment=ALIGN_CENTER,
                 default_padding=1):

        self.set_style(BeautifulTable.STYLE_DEFAULT)

        self.numeric_precision = 3
        self.serialno = False

        self._sign_mode = BeautifulTable.SM_MINUS
        self._width_exceed_policy = BeautifulTable.WEP_WRAP
        self._default_alignment = default_alignment
        self._default_padding = default_padding
        self._column_pad = " "
        self._max_table_width = max_width

        self._initialize_table(0)
        self._table = []

    def __setattr__(self, name, value):
        if name in ('left_border_char', 'right_border_char', 'top_border_char',
                    'bottom_border_char', 'header_seperator_char',
                    'column_seperator_char', 'row_seperator_char',
                    'intersection_char') and not isinstance(value, str):
            raise TypeError("Expected {attr} to be of type 'str', got {attr_type}".format(attr=name, attr_type=type(value).__name__))
        super(BeautifulTable, self).__setattr__(name, value)


# ****************************Properties Begin Here*****************************

    @property
    def column_count(self):
        """Get the number of columns in the table(read only)"""
        return self._column_count

    @property
    def sign_mode(self):
        """Attribute to control how signs are displayed for numerical data.

        It can be one of the following:

        ========================  ==============================================
         Option                    Meaning
        ========================  ==============================================
         BeautifulTable.SM_PLUS    A sign should be used for both +ve and -ve
                                   numbers.

         BeautifulTable.SM_MINUS   A sign should only be used for -ve numbers.

         BeautifulTable.SM_SPACE   A leading space should be used for +ve
                                   numbers and a minus sign for -ve numbers.
        ========================  ==============================================
        """
        return self._sign_mode

    @sign_mode.setter
    def sign_mode(self, value):
        if not isinstance(value, SignMode):
            error_msg = ("allowed values for sign_mode are: "
                         + ', '.join("{}.{}".format(type(self).__name__, i.name) for i in SignMode))
            raise ValueError(error_msg)
        self._sign_mode = value

    @property
    def width_exceed_policy(self):
        """Attribute to control the behaviour of table when items exceed the column width.

        It can be one of the following:

        ============================  ==========================================
         Option                        Meaning
        ============================  ==========================================
         BeautifulTable.WEP_WRAP       An item is wrapped so every line fits
                                       within it's column width.

         BeautifulTable.WEP_STRIP      An item is stripped to fit in it's
                                       column.

         BeautifulTable.WEP_ELLIPSIS   An item is stripped to fit in it's
                                       column and appended with ...(Ellipsis).
        ============================  ==========================================
        """
        return self._width_exceed_policy

    @width_exceed_policy.setter
    def width_exceed_policy(self, value):
        if not isinstance(value, WidthExceedPolicy):
            error_msg = ("allowed values for width_exceed_policy are: "
                         + ', '.join("{}.{}".format(type(self).__name__, i.name) for i in WidthExceedPolicy))
            raise ValueError(error_msg)
        self._width_exceed_policy = value

    @property
    def default_alignment(self):
        """Attribute to control the alignment of newly created columns.

        It can be one of the following:

        ============================  ==========================================
         Option                        Meaning
        ============================  ==========================================
         BeautifulTable.ALIGN_LEFT     New columns are left aligned.

         BeautifulTable.ALIGN_CENTER   New columns are center aligned.

         BeautifulTable.ALIGN_RIGHT    New columns are right aligned.
        ============================  ==========================================
        """
        return self._default_alignment

    @default_alignment.setter
    def default_alignment(self, value):
        if not isinstance(value, Alignment):
            error_msg = ("allowed values for default_alignment are: "
                         + ', '.join("{}.{}".format(type(self).__name__, i.name) for i in Alignment))
            raise ValueError(error_msg)
        self._default_alignment = value

    @property
    def default_padding(self):
        """Initial value for Left and Right padding widths for new columns."""
        return self._default_padding

    @default_padding.setter
    def default_padding(self, value):
        if not isinstance(value, int):
            raise TypeError("padding must be an integer")
        elif value <= 0:
            raise ValueError("padding must be more than 0")
        else:
            self._default_padding = value

    @property
    def column_widths(self):
        """get/set width for the columns of the table.

        Width of the column specifies the max number of characters
        a column can contain. Larger characters are handled according to
        the value of `width_exceed_policy`.
        """
        return self._column_widths

    @column_widths.setter
    def column_widths(self, value):
        width = self._validate_row(value)
        self._column_widths = PositiveIntegerMetaData(self, width)

    @property
    def column_headers(self):
        """get/set titles for the columns of the table.

        It can be any iterable having all memebers an instance of `str`.
        """
        return self._column_headers

    @column_headers.setter
    def column_headers(self, value):
        header = self._validate_row(value)
        for i in header:
            if not isinstance(i, str):
                raise TypeError("Headers should be of type 'str'")
        self._column_headers = HeaderData(self, header)

    @property
    def column_alignments(self):
        """get/set alignment of the columns of the table.

        It can be any iterable containing only the following:

        * BeautifulTable.ALIGN_LEFT
        * BeautifulTable.ALIGN_CENTER
        * BeautifulTable.ALIGN_RIGHT
        """
        return self._column_alignments

    @column_alignments.setter
    def column_alignments(self, value):
        alignment = self._validate_row(value)
        self._column_alignments = AlignmentMetaData(self, alignment)

    @property
    def left_padding_widths(self):
        """get/set width for left padding of the columns of the table.

        Left Width of the padding specifies the number of characters
        on the left of a column reserved for padding. By Default It is 1.
        """
        return self._left_padding_widths

    @left_padding_widths.setter
    def left_padding_widths(self, value):
        pad_width = self._validate_row(value)
        self._left_padding_widths = PositiveIntegerMetaData(self, pad_width)

    @property
    def right_padding_widths(self):
        """get/set width for right padding of the columns of the table.

        Right Width of the padding specifies the number of characters
        on the rigth of a column reserved for padding. By default It is 1.
        """
        return self._right_padding_widths

    @right_padding_widths.setter
    def right_padding_widths(self, value):
        pad_width = self._validate_row(value)
        self._right_padding_widths = PositiveIntegerMetaData(self, pad_width)

# *****************************Properties End Here******************************

    def _initialize_table(self, column_count):
        """Sets the column count of the table.

        This method is called to set the number of columns for the first time.

        Parameters
        ----------
        column_count : int
            number of columns in the table
        """
        self._column_count = column_count
        self._column_headers = HeaderData(self, [''] * column_count)
        self._column_alignments = AlignmentMetaData(self, [self.default_alignment] * column_count)
        self._column_widths = PositiveIntegerMetaData(self, [0] * column_count)
        self._left_padding_widths = PositiveIntegerMetaData(self, [self.default_padding] * column_count)
        self._right_padding_widths = PositiveIntegerMetaData(self, [self.default_padding] * column_count)

    def _validate_row(self, value, init_table_if_required=True):
        # TODO: Rename this method
        # str is also an iterable but it is not a valid row, so
        # an extra check is required for str
        if not isinstance(value, collections.Iterable) or isinstance(value, str):
            raise TypeError("parameter must be an iterable")

        row = list(value)
        if init_table_if_required and self._column_count == 0:
            self._initialize_table(len(row))

        if len(row) != self._column_count:
            raise ValueError("'Expected iterable of length {}, got {}".format(self._column_count, len(row)))
        return row

    def __getitem__(self, key):
        """Get a row, or a column, or a new table by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, returns a row.
            If key is an `str`, returns iterator to a column with heading `key`.
            If key is a slice object, returns a new table sliced according to
            rows.

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not found in headers.
        """
        if isinstance(key, slice):
            new_table = copy.copy(self)
            # Every child of BaseRow class needs to be reassigned so that
            # They contain reference of the new table rather than the old
            # This was a cause of a nasty bug once.
            new_table.column_headers = self.column_headers
            new_table.column_alignments = self.column_alignments
            new_table.column_widths = self.column_widths
            new_table.left_padding_widths = self.left_padding_widths
            new_table.right_padding_widths = self.left_padding_widths
            new_table._table = []
            for row in self._table[key]:
                new_table.append_row(row)
            return new_table
        elif isinstance(key, int):
            return self._table[key]
        elif isinstance(key, str):
            return self.get_column(key)
        else:
            raise TypeError("table indices must be integers or slices, not {}".format(type(key).__name__))

    def __delitem__(self, key):
        """Delete a row, or a column, or multiple rows by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, deletes a row.
            If key is a slice object, deletes multiple rows.
            If key is an `str`, delete the first column with heading `key`

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not found in headers.
        """
        if isinstance(key, int) or isinstance(key, slice):
            del self._table[key]
        elif isinstance(key, str):
            return self.pop_column(key)
        else:
            raise TypeError("table indices must be integers or slices, not {}".format(type(key).__name__))

    def __setitem__(self, key, value):
        """Update a row, or a column, or multiple rows by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, updates a row.
            If key is an `str`, appends `column` to the list with header as
            `key`.
            If key is a slice object, updates multiple rows according to slice
            rules.

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        """
        if isinstance(key, (int, slice)):
            self.update_row(key, value)
        elif isinstance(key, str):
            self.update_column(key, value)
        else:
            raise TypeError("table indices must be integers or slices, not {}".format(type(key).__name__))

    def __len__(self):
        return len(self._table)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self._column_headers
        elif isinstance(key, collections.Iterable):
            return key in self._table
        else:
            raise TypeError("'key' must be str or Iterable, not {}".format(type(key).__name__))

    def __iter__(self):
        return iter(self._table)

    def __next__(self):
        return next(self._table)

    def __repr__(self):
        return repr(self._table)

    def __str__(self):
        return self.get_string()

    def set_style(self, style):
        """Set the style of the table from a predefined set of styles.

        Parameters
        ----------
        style: Style

        It can be one of the following:

        * BeautifulTable.STYLE_DEFAULT
        * BeautifulTable.STYLE_DOTTED
        * BeautifulTable.STYLE_MYSQL
        * BeautifulTable.STYLE_SEPERATED
        * BeautifulTable.STYLE_COMPACT
        * BeautifulTable.STYLE_MARKDOWN
        * BeautifulTable.STYLE_RESTRUCTURED_TEXT
        """
        if not isinstance(style, Style):
            error_msg = ("allowed values for style are: "
                         + ', '.join("{}.{}".format(type(self).__name__, i.name) for i in Style))
            raise ValueError(error_msg)
        style_template = style.value
        self.left_border_char = style_template.left_border_char
        self.right_border_char = style_template.right_border_char
        self.top_border_char = style_template.top_border_char
        self.bottom_border_char = style_template.bottom_border_char
        self.header_seperator_char = style_template.header_seperator_char
        self.column_seperator_char = style_template.column_seperator_char
        self.row_seperator_char = style_template.row_seperator_char
        self.intersection_char = style_template.intersection_char

    def auto_calculate_width(self):
        """Calculate width of column automatically based on data."""
        table_width = self.get_table_width()
        offset = table_width - sum(self._column_widths)
        widths = [(self._left_padding_widths[index] + self._right_padding_widths[index]) for index in range(self._column_count)]
        for index, column in enumerate(zip(*self._table)):
            max_length = (max(len(str(convert_to_numeric(i, self.numeric_precision)))
                          for i in column))
            max_length = max(max_length, len(str(self._column_headers[index])))
            widths[index] += max_length

        sum_ = sum(widths)
        desired_sum = self._max_table_width - offset

        temp_sum = 0
        flag = [0] * len(widths)
        for i, width in enumerate(widths):
            if width < desired_sum / self._column_count:
                temp_sum += width
                flag[i] = 1

        avail_space = desired_sum - temp_sum
        actual_space = sum_ - temp_sum
        for i, _ in enumerate(widths):
            if not flag[i]:
                widths[i] = int(round(widths[i] * avail_space / actual_space))
        self.column_widths = widths

    def set_padding_widths(self, pad_width):
        """Set width for left and rigth padding of the columns of the table.

        Parameters
        ----------
        pad_width : array_like
            pad widths for the columns.
        """
        self.left_padding_widths = pad_width
        self.right_padding_widths = pad_width

    def sort(self, key, reverse=False):
        """Stable sort of the table *IN-PLACE* with respect to a column.

        Parameters
        ----------
        key: int, str
            index or header of the column. Normal list rules apply.
        reverse : bool
            If `True` then table is sorted as if each comparison was reversed.
        """
        if isinstance(key, int):
            index = key
        elif isinstance(key, str):
            index = self.get_column_index(key)
        else:
            raise TypeError("'key' must either be 'int' or 'str'")
        self._table.sort(key=operator.itemgetter(index), reverse=reverse)

    def copy(self):
        """Return a shallow copy of the table.

        Returns
        -------
        BeautifulTable:
            shallow copy of the BeautifulTable instance.
        """
        return self[:]

    def get_column_header(self, index):
        """Get header of a column from it's index.

        Parameters
        ----------
        index: int
            Normal list rules apply.
        """
        return self._column_headers[index]

    def get_column_index(self, header):
        """Get index of a column from it's header.

        Parameters
        ----------
        header: str
            header of the column.

        Raises
        ------
        ValueError:
            If no column could be found corresponding to `header`.
        """
        try:
            index = self._column_headers.index(header)
            return index
        except ValueError:
            raise_suppressed(KeyError("'{}' is not a header for any column".format(header)))

    def get_column(self, key):
        """Return an iterator to a column.

        Parameters
        ----------
        key : int, str
            index of the column, or the header of the column.
            If index is specified, then normal list rules apply.

        Raises
        ------
        TypeError:
            If key is not of type `int`, or `str`.

        Returns
        -------
        iter:
            Iterator to the specified column.
        """
        if isinstance(key, int):
            index = key
        elif isinstance(key, str):
            index = self.get_column_index(key)
        else:
            raise TypeError("key must be an int or str, not {}".format(type(key).__name__))
        return iter(map(operator.itemgetter(index), self._table))

    def reverse(self):
        """Reverse the table row-wise *IN PLACE*."""
        self._table.reverse()

    def pop_row(self, index=-1):
        """Remove and return row at index (default last).

        Parameters
        ----------
        index : int
            index of the row. Normal list rules apply.
        """
        row = self._table.pop(index)
        return row

    def pop_column(self, index=-1):
        """Remove and return row at index (default last).

        Parameters
        ----------
        index : int, str
            index of the column, or the header of the column.
            If index is specified, then normal list rules apply.

        Raises
        ------
        TypeError:
            If index is not an instance of `int`, or `str`.

        IndexError:
            If Table is empty.
        """
        if isinstance(index, int):
            pass
        elif isinstance(index, str):
            index = self.get_column_index(index)
        else:
            raise TypeError("column index must be an integer or a string, not {}".format(type(index).__name__))
        if self._column_count == 0:
            raise IndexError("pop from empty table")
        if self._column_count == 1:
            # This is the last column. So we should clear the table to avoid
            # empty rows
            self.clear(clear_metadata=True)
        else:
            # Not the last column. safe to pop from row
            self._column_count -= 1
            self._column_alignments._pop(index)
            self._column_widths._pop(index)
            self._left_padding_widths._pop(index)
            self._right_padding_widths._pop(index)
            self._column_headers._pop(index)
            for row in self._table:
                row._pop(index)

    def insert_row(self, index, row):
        """Insert a row before index in the table.

        Parameters
        ----------
        index : int
            List index rules apply

        row : iterable
            Any iterable of appropriate length.

        Raises
        ------
        TypeError:
            If `row` is not an iterable.

        ValueError:
            If size of `row` is inconsistent with the current number
            of columns.
        """
        row = self._validate_row(row)
        row_obj = RowData(self, row)
        self._table.insert(index, row_obj)

    def append_row(self, row):
        """Append a row to end of the table.

        Parameters
        ----------
        row : iterable
            Any iterable of appropriate length.

        """
        self.insert_row(len(self._table), row)

    def update_row(self, key, value):
        """Update a column named `header` in the table.

        If length of column is smaller than number of rows, lets say
        `k`, only the first `k` values in the column is updated.

        Parameters
        ----------
        key : int or slice
            index of the row, or a slice object.

        value : iterable
            If an index is specified, `value` should be an iterable
            of appropriate length. Instead if a slice object is
            passed as key, value should be an iterable of rows.

        Raises
        ------
        IndexError:
            If index specified is out of range.

        TypeError:
            If `value` is of incorrect type.

        ValueError:
            If length of row does not matches number of columns.
        """
        if isinstance(key, int):
            row = self._validate_row(value, init_table_if_required=False)
            row_obj = RowData(self, row)
            self._table[key] = row_obj
        elif isinstance(key, slice):
            row_obj_list = []
            for row in value:
                row_ = self._validate_row(row, init_table_if_required=True)
                row_obj_list.append(RowData(self, row_))
            self._table[key] = row_obj_list
        else:
            raise TypeError("key must be an integer or a slice object")

    def update_column(self, header, column):
        """Update a column named `header` in the table.

        If length of column is smaller than number of rows, lets say
        `k`, only the first `k` values in the column is updated.

        Parameters
        ----------
        header : str
            Header of the column

        column : iterable
            Any iterable of appropriate length.

        Raises
        ------
        TypeError:
            If length of `column` is shorter than number of rows.

        ValueError:
            If no column exists with title `header`.
        """
        index = self.get_column_index(header)
        if not isinstance(header, str):
            raise TypeError("header must be of type str")
        for row, new_item in zip(self._table, column):
            row[index] = new_item

    def insert_column(self, index, header, column):
        """Insert a column before `index` in the table.

        If length of column is bigger than number of rows, lets say
        `k`, only the first `k` values of `column` is considered.
        If column is shorter than 'k', ValueError is raised.

        Note that Table remains in consistent state even if column
        is too short. Any changes made by this method is rolled back
        before raising the exception.

        Parameters
        ----------
        index : int
            List index rules apply.

        header : str
            Title of the column.

        column : iterable
            Any iterable of appropriate length.

        Raises
        ------
        TypeError:
            If `header` is not of type `str`.

        ValueError:
            If length of `column` is shorter than number of rows.
        """
        if self._column_count == 0:
            self.column_headers = HeaderData(self, [header])
            self._table = [RowData(self, [i]) for i in column]
        else:
            if not isinstance(header, str):
                raise TypeError("header must be of type str")
            column_length = 0
            for i, (row, new_item) in enumerate(zip(self._table, column)):
                row._insert(index, new_item)
                column_length = i
            if column_length == len(self._table) - 1:
                self._column_count += 1
                self._column_headers._insert(index, header)
                self._column_alignments._insert(index, self.default_alignment)
                self._column_widths._insert(index, 0)
                self._left_padding_widths._insert(index, self.default_padding)
                self._right_padding_widths._insert(index, self.default_padding)
            else:
                # Roll back changes so that table remains in consistent state
                for j in range(column_length, -1, -1):
                    self._table[j]._pop(index)
                raise ValueError("length of 'column' should be atleast {}, got {}".format(len(self._table), column_length + 1))

    def append_column(self, header, column):
        """Append a column to end of the table.

        Parameters
        ----------
        header : str
            Title of the column

        column : iterable
            Any iterable of appropriate length.
        """
        self.insert_column(self._column_count, header, column)

    def clear(self, clear_metadata=False):
        """Clear the contents of the table.

        Clear all rows of the table, and if specified clears all column specific
        data.

        Parameters
        ----------
        clear_metadata : bool, optional
            If it is true(default False), all metadata of columns such as their
            alignment, padding, width, etc. are also cleared and number of
            columns is set to 0.
        """
        # Cannot use clear method to support Python 2.7
        del self._table[:]
        if clear_metadata:
            self._initialize_table(0)

    def _get_horizontal_line(self, char):
        """Get a horizontal line for the table.

        Internal method used to actually get all horizontal lines in the table.
        Column width should be set prior to calling this method. This method
        detects intersection and handles it according to the value of
        `intersection_char`.

        Parameters
        ----------
        char : str
            Character used to draw the line.

        Returns
        -------
        str
            String which will be printed as the Top border of the table.
        """
        table_width = self.get_table_width()
        intersection = self.intersection_char
        try:
            line = list(char * (int(table_width/len(char)) + 1))[:table_width]
        except ZeroDivisionError:
            line = [' '] * table_width

        if len(line) == 0:
            return ''
        # Only if Special Intersection is enabled and horizontal line is
        # visible
        if self.intersection_char and not char.isspace():
            # If left border is enabled and it is visible
            if self.left_border_char:
                if not self.left_border_char.isspace() or self.intersection_char.isspace():
                    length = min(len(self.left_border_char),
                                 len(self.intersection_char))
                    for i in range(length):
                        line[i] = intersection[i]
            # If right border is enabled and it is visible
            if self.right_border_char:
                if not self.right_border_char.isspace() or self.intersection_char.isspace():
                    length = min(len(self.right_border_char),
                                 len(self.intersection_char))
                    for i in range(length):
                        line[-i-1] = intersection[-i-1]
            # If column seperator is enabled and it is visible
            if self.column_seperator_char:
                if not self.column_seperator_char.isspace() or self.intersection_char.isspace():
                    index = len(self.left_border_char)
                    for i in range(self._column_count-1):
                        index += (self._column_widths[i])
                        length = min(len(self.column_seperator_char),
                                     len(self.intersection_char))
                        for i in range(length):
                            line[index+i] = intersection[i]
                        index += len(self.column_seperator_char)

        return ''.join(line)

    def get_top_border(self):
        """Get the Top border of table.

        Column width should be set prior to calling this method.

        Returns
        -------
        str
            String which will be printed as the Top border of the table.
        """
        return self._get_horizontal_line(self.top_border_char)

    def get_header_seperator(self):
        """Get the Header seperator of table.

        Column width should be set prior to calling this method.

        Returns
        -------
        str
            String which will be printed as Header seperator of the table.
        """
        return self._get_horizontal_line(self.header_seperator_char)

    def get_row_seperator(self):
        """Get the Row seperator of table.

        Column width should be set prior to calling this method.

        Returns
        -------
        str
            String which will be printed as Row seperator of the table.
        """
        return self._get_horizontal_line(self.row_seperator_char)

    def get_bottom_border(self):
        """Get the Bottom border of table.

        Column width should be set prior to calling this method.

        Returns
        -------
        str
            String which will be printed as the Bottom border of the table.
        """
        return self._get_horizontal_line(self.bottom_border_char)

    def get_table_width(self):
        """Get the width of the table as number of characters.

        Column width should be set prior to calling this method.

        Returns
        -------
        int
            Width of the table as number of characters.
        """
        if self.column_count == 0:
            return 0
        width = sum(self._column_widths)
        width += ((self._column_count - 1)
                  * len(self.column_seperator_char))
        width += len(self.left_border_char)
        width += len(self.right_border_char)
        return width

    def get_string(self, recalculate_width=True):
        """Get the table as a String.

        Parameters
        ----------
        recalculate_width : bool, optional
            If width for each column should be recalculated(default True).
            Note that width is always calculated if it wasn't set
            explicitly when this method is called for the first time ,
            regardless of the value of `recalculate_width`.

        Returns
        -------
        str:
            Table as a string.
        """
        # Empty table. returning empty string.
        if len(self._table) == 0:
            return ''

        if self.serialno and self.column_count > 0:
            self.insert_column(0, 'SN', range(1, len(self) + 1))

        # Should widths of column be recalculated
        if recalculate_width or sum(self._column_widths) == 0:
            self.auto_calculate_width()

        string_ = []

        # Drawing the top border
        if self.top_border_char:
            string_.append(
                self.get_top_border())

        # Print headers if not empty or only spaces
        if ''.join(self._column_headers).strip():
            headers = str(self._column_headers)
            string_.append(headers)

            if self.header_seperator_char:
                string_.append(
                    self.get_header_seperator())

        # Printing rows
        first_row_encountered = False
        for row in self._table:
            if first_row_encountered and self.row_seperator_char:
                string_.append(
                    self.get_row_seperator())
            first_row_encountered = True
            content = str(row)
            string_.append(content)

        # Drawing the bottom border
        if self.bottom_border_char:
            string_.append(
                self.get_bottom_border())

        if self.serialno and self.column_count > 0:
            self.pop_column(0)

        return '\n'.join(string_)
