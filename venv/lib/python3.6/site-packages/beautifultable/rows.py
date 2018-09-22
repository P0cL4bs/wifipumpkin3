import itertools
from .utils import convert_to_numeric
from .base import BaseRow
from .enums import WidthExceedPolicy

class RowData(BaseRow):
    def _get_row_within_width(self, row):
        """Process a row so that it is clamped by column_width.

        Parameters
        ----------
        row : array_like
             A single row.

        Returns
        -------
        list of list:
            List representation of the `row` after it has been processed according
            to width exceed policy.
        """
        list_of_rows = []
        if (self._table.width_exceed_policy is WidthExceedPolicy.WEP_STRIP or
                self._table.width_exceed_policy is WidthExceedPolicy.WEP_ELLIPSIS):
            # Let's strip the row
            delimiter = '' if self._table.width_exceed_policy is WidthExceedPolicy.WEP_STRIP else '...'
            row_item_list = []
            for index, row_item in enumerate(row):
                left_pad = self._table._column_pad * self._table.left_padding_widths[index]
                right_pad = self._table._column_pad * self._table.right_padding_widths[index]
                clmp_str = left_pad + self._clamp_string(row_item, index, delimiter) + right_pad
                row_item_list.append(clmp_str)
            list_of_rows.append(row_item_list)
        elif self._table.width_exceed_policy is WidthExceedPolicy.WEP_WRAP:
            # Let's wrap the row
            row_item_list = []
            for i in itertools.count():
                line_empty = True
                for index, row_item in enumerate(row):
                    width = self._table.column_widths[index] - self._table.left_padding_widths[index] - self._table.right_padding_widths[index]
                    left_pad = self._table._column_pad * self._table.left_padding_widths[index]
                    right_pad = self._table._column_pad * self._table.right_padding_widths[index]
                    clmp_str = row_item[i*width:(i+1)*width]
                    if len(clmp_str) != 0:
                        line_empty = False
                    row_item_list.append(left_pad + clmp_str + right_pad)
                if line_empty:
                    break
                else:
                    list_of_rows.append(row_item_list)
                    row_item_list = []

        if len(list_of_rows) == 0:
            return [['']*self._table.column_count]
        else:
            return list_of_rows

    def _clamp_string(self, row_item, column_index, delimiter=''):
        """Clamp `row_item` to fit in column referred by column_index.

        This method considers padding and appends the delimiter if `row_item`
        needs to be truncated.

        Parameters
        ----------
        row_item: str
            String which should be clamped.

        column_index: int
            Index of the column `row_item` belongs to.

        delimiter: str
            String which is to be appended to the clamped string.

        Returns
        -------
        str
            The modified string which fits in it's column.
        """
        width = (self._table.column_widths[column_index]
                 - self._table.left_padding_widths[column_index]
                 - self._table.right_padding_widths[column_index])
        if len(row_item) <= width:
            return row_item
        else:
            if width-len(delimiter) >= 0:
                clamped_string = (row_item[:width-len(delimiter)]
                                  + delimiter)
            else:
                clamped_string = delimiter[:width]
            assert len(clamped_string) == width
            return clamped_string

    def __str__(self):
        """Return a string representation of a row."""
        row = [convert_to_numeric(item, self._table.numeric_precision)
               for item in self._row]
        table = self._table
        width = table.column_widths
        align = table.column_alignments
        sign = table.sign_mode
        for i in range(table.column_count):
            try:
                row[i] = '{:{sign}}'.format(row[i], sign=sign.value)
            except ValueError:
                row[i] = str(row[i])
        string = []
        if len(row) > 0:
            list_of_rows = self._get_row_within_width(row)
            for row_ in list_of_rows:
                for i in range(table.column_count):
                    row_[i] = '{:{align}{width}}'.format(
                        str(row_[i]), align=align[i].value, width=width[i])
                content = table.column_seperator_char.join(row_)
                content = table.left_border_char + content
                content += table.right_border_char
                string.append(content)
        return '\n'.join(string)


class HeaderData(RowData):
    def __init__(self, table, row):
        for i in row:
            self.validate(i)
        RowData.__init__(self, table, row)

    def __getitem__(self, key):
        return self._row[key]

    def __setitem__(self, key, value):
        self.validate(value)
        if not isinstance(key, int):
            raise TypeError("header indices must be integers, not {}".format(type(key).__name__))
        self._row[key] = value

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError("header must be of type 'str', got {}".format(type(value).__name__))
