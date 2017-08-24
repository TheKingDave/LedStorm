from ownColor import ownColor


class ColorCalc(object):

    def __init__(self, columns, extra):
        self.columns = columns
        self.extra = extra

    def column_color(self, data, column):
        return ownColor(255, 255, 255)

    def pixel_color(self, column_color, row_on, column, row, pixel):
        return column_color if row_on else ownColor(0, 0, 0)