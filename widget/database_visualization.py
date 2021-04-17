"""
Наглядное отображение Базы Данных, включает:
    Общие графики:
        - круговые диаграммы кол-во обнаруженных людей за 1 день, за промежуток времени
        - столбчатые диаграммы кол-во обнаруженных людей за 1 день, за промежуток времени
    Отдельного человека:
        - линейный график температуры
        - карта температур
        - карта схожести с данным человеком
"""
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import widget.models as models

mpl.use('Qt5Agg')


class DBVisualization(FigureCanvas):
    def __init__(self, parent=None, width: float = 10, height: float = 10, dpi: int = 100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(111)
        super(DBVisualization, self).__init__(figure)
        self._theme = None

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, value):
        if isinstance(value, dict):
            self._theme = value

    def create_pie_chart_number_persons(self, low: str = None, high: str = None):
        pass

    def create_histogram_number_persons(self, low: str = None, high: str = None):
        pass

    def create_line_graph_temperatures(self, statistics: list[models.Statistic]):
        pass

    def create_map_temperatures(self, statistics: list[models.Statistic]):
        pass

    def create_map_similar(self, statistics: list[models.Statistic]):
        pass

    def show(self):
        pass
