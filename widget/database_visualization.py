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

    def create_pie_chart_temperatures(
            self,
            threshold: int = 37.5,
            current_day: str = None,
            title: str = 'All time passage of people'  # Passage of people for the current day
    ):
        self.ax.clear()
        self.figure.set_facecolor('#272c36')
        labels = ['Profile', 'Stranger']
        if current_day is None:
            low = None
            high = None
        else:
            low = current_day + ' 00:00:00'
            high = current_day + ' 23:59:59'
        number_passages = [
            self.database_management.get_number_statistics(low=low, high=high),
            self.database_management.get_number_stranger_statistics(low=low, high=high)
        ]
        number_all_persons = np.array(number_passages).sum()
        if number_all_persons == 0:
            data = [1, 1]
        else:
            data = number_passages
        number_normal_temp_stats = self.database_management \
            .get_number_normal_temperature_statistics(threshold=threshold, low=low, high=high)
        number_normal_temp_stranger_stats = self.database_management \
            .get_number_normal_temperature_stranger_statistics(threshold=threshold, low=low, high=high)
        number_temperatures = [
            number_normal_temp_stats,
            number_passages[0] - number_normal_temp_stats,
            number_normal_temp_stranger_stats,
            number_passages[1] - number_normal_temp_stranger_stats
        ]
        if np.array(number_temperatures).sum() == 0:
            data_temperatures = [1, 1, 1, 1]
        else:
            data_temperatures = number_temperatures
        print(number_temperatures, number_passages)
        colors_temperatures = ['#BB9BB6', '#E9B9D2', '#BB9BB6', '#E9B9D2']
        colors = ['#686277', '#907E97']
        wedges, texts = self.ax.pie(
            data,
            colors=colors,
            startangle=45,
            frame=False,
            pctdistance=0.7,
            wedgeprops=dict(width=0.5)
        )
        wedges2, texts2 = self.ax.pie(
            data_temperatures,
            colors=colors_temperatures,
            radius=0.75,
            startangle=45
        )
        centre_circle = plt.Circle((0, 0), 0.5, color='black', fc='#272c36', linewidth=0)
        self.ax.add_artist(centre_circle)
        bbox_props = dict(boxstyle='square,pad=0.3', fc='#272c36', ec='w', lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle='-', color='w'),
                  bbox=bbox_props, zorder=0, va='center',
                  color='w')
        j = 0
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            connectionstyle = 'angle,angleA=0,angleB={}'.format(ang)
            kw['arrowprops'].update({'connectionstyle': connectionstyle})
            self.ax.annotate(f'{labels[i]} '
                             f'{np.round(100 * number_passages[i] / number_all_persons, 2)}%\n'
                             f'({number_passages[i]} [N - {number_temperatures[j]}; A - {number_temperatures[j + 1]}])',
                             xy=(x, y),
                             xytext=(1.35 * np.sign(x), 1.4 * y),
                             horizontalalignment='center', **kw)
            j += 2
        self.ax.set_title(title, color='w')
        # self.ax.legend([wedges, wedges2], [data, data_temperatures],
        #                title='Passage',
        #                loc='center left',
        #                bbox_to_anchor=(1, 0, 0.5, 1))

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

    def save(self, filename):
        self.figure.savefig(filename)
