class DefaultStyle(object):
    left_border_char = '|'
    right_border_char = '|'
    top_border_char = '-'
    bottom_border_char = '-'
    header_seperator_char = '-'
    column_seperator_char = '|'
    row_seperator_char = '-'
    intersection_char = '+'


class MySQLStyle(DefaultStyle):
    pass


class SeperatedStyle(DefaultStyle):
    top_border_char = '='
    header_seperator_char = '='


class CompactStyle(DefaultStyle):
    left_border_char = ''
    right_border_char = ''
    top_border_char = ''
    bottom_border_char = ''
    header_seperator_char = '-'
    column_seperator_char = ' '
    row_seperator_char = ''
    intersection_char = ' '


class DottedStyle(object):
    left_border_char = ':'
    right_border_char = ':'
    top_border_char = '.'
    bottom_border_char = '.'
    header_seperator_char = '.'
    column_seperator_char = ':'
    row_seperator_char = ''
    intersection_char = ''


class MarkdownStyle(DefaultStyle):
    top_border_char = ''
    bottom_border_char = ''
    row_seperator_char = ''
    intersection_char = '|'


class RestructuredTextStyle(CompactStyle):
    top_border_char = '='
    bottom_border_char = '='
    header_seperator_char = '='
