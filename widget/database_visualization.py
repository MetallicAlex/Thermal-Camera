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
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from widget.management import DBManagement

mpl.use('Qt5Agg')


class DBVisualization(FigureCanvas):
    def __init__(self, parent=None, width: float = 10, height: float = 10, dpi: int = 100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        # 55aaff
        # 272c36
        self.database_management = DBManagement()
        self.ax = self.figure.add_subplot(111)
        super(DBVisualization, self).__init__(self.figure)
        self._theme = None
        # self._customization()

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, value):
        if isinstance(value, dict):
            self._theme = value

    def _customization(self):
        self.figure.set_facecolor('#272c36')
        self.figure.set_edgecolor('#55aaff')
        self.ax.set_facecolor('#272c36')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('r')
        self.ax.spines['bottom'].set_color('r')
        self.ax.spines['left'].set_linewidth(3)
        self.ax.set_title('Title', fontsize=20)
        # self.ax.grid(color='#55aaff', linestyle='--', linewidth=2)

    def create_pie_chart_temperatures(self, threshold: int = 37.5, identifiers: list = None):
        # bb13d1
        self.figure.set_facecolor('#272c36')
        labels = ['Profile', 'Stranger']
        number_passages = [
            self.database_management.get_number_statistics(identifiers),
            self.database_management.get_number_stranger_statistics()
        ]
        number_all_persons = np.array(number_passages).sum()
        number_normal_temp_stats = self.database_management\
            .get_number_normal_temperature_statistics(threshold=threshold)
        number_normal_temp_stranger_stats = self.database_management \
            .get_number_normal_temperature_stranger_statistics(threshold=threshold)
        number_temperatures = [
            number_normal_temp_stats,
            number_passages[0] - number_normal_temp_stats,
            number_normal_temp_stranger_stats,
            number_passages[1] - number_normal_temp_stranger_stats
        ]
        colors = ['#ff6666', '#99ff99']
        colors = ['#49b6fc', '#fb7c33']
        wedges, texts = self.ax.pie(
            number_passages,
            colors=colors,
            startangle=45,
            frame=False,
            pctdistance=0.7,
            wedgeprops=dict(width=0.5)
        )
        centre_circle = plt.Circle((0, 0), 0.5, color='black', fc='#272c36', linewidth=0)
        self.ax.add_artist(centre_circle)
        bbox_props = dict(boxstyle='square,pad=0.3', fc='#272c36', ec='w', lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle='-', color='w'),
                  bbox=bbox_props, zorder=0, va='center',
                  color='w')
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: 'right', 1: 'left'}[int(np.sign(x))]
            connectionstyle = 'angle,angleA=0,angleB={}'.format(ang)
            print(texts[i])
            print(wedges[i])
            kw['arrowprops'].update({'connectionstyle': connectionstyle})
            self.ax.annotate(f'{labels[i]} {np.round(100*number_passages[i]/number_all_persons, 2)}% ({number_passages[i]})',
                             xy=(x, y),
                             xytext=(1.35 * np.sign(x), 1.4 * y),
                             horizontalalignment='center', **kw)
        self.ax.set_title(r'Person Passage', color='w')

    def create_pie_chart_number_persons(self, low: str = None, high: str = None):
        pass

    def create_histogram_number_persons(self, low: str = None, high: str = None):
        pass

    def create_line_graph_temperatures(self, statistics: list):
        pass

    def create_map_temperatures(self, statistics: list):
        pass

    def create_map_similar(self, statistics: list):
        pass

    def show(self):
        self.draw()
