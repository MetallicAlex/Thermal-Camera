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
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from widget.management import DBManagement

mpl.use('Qt5Agg')


class DBVisualization(FigureCanvas):
    def __init__(self, lang: dict, parent=None, width: float = 10, height: float = 10, dpi: int = 100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.database_management = DBManagement()
        self._lang = lang
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
            stat_time: tuple = None,
            temperature: tuple = None,
            name: str = None,
            identifiers: list = None,
            devices: list = None,
            title: str = 'All time passage of people'  # Passage of people for the current day
    ):
        self.ax.clear()
        number_passages = self.database_management.get_number_statistics(
            time=stat_time,
            temperature=temperature,
            name=name,
            identifiers=identifiers,
            devices=devices
        )
        number_all_persons = np.array(number_passages).sum()
        if number_all_persons == 0:
            data = (1, 1)
            number_all_persons = 2
        else:
            data = number_passages
        number_normal_temp_stats, number_normal_temp_stranger_stats = \
            self.database_management.get_number_normal_temperature_statistics(
                threshold=threshold,
                time=stat_time,
                temperature=temperature,
                name=name,
                identifiers=identifiers,
                devices=devices
            )
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
        colors_temperatures = ['#84F9BD', '#F0939D', '#84F9BD', '#F0939D']
        colors = ['#87B7E3', '#91D1EE']
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
        centre_circle = plt.Circle((0, 0), 0.5, color='white', fc='white', linewidth=0)
        self.ax.add_artist(centre_circle)
        bbox_props = dict(boxstyle='square,pad=0.3', fc='white', ec='#09376B', lw=1.5)
        kw = dict(arrowprops=dict(arrowstyle='-', color='#09376B'),
                  bbox=bbox_props, zorder=0, va='center',
                  color='#09376B')
        j = 0
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            connectionstyle = 'angle,angleA=0,angleB={}'.format(ang)
            kw['arrowprops'].update({'connectionstyle': connectionstyle})
            self.ax.annotate(
                f'{np.round(100 * data[i] / number_all_persons, 2)}% '
                f'({number_passages[i]})\n'
                f'[{self._lang["pie"]["short_norm_temp"]} - {number_temperatures[j]};'
                f' {self._lang["pie"]["short_heat_temp"]} - {number_temperatures[j + 1]}]',
                xy=(x, y),
                xytext=(2 * np.sign(x), 1.5 * y),
                horizontalalignment='center', fontsize=16, **kw)
            j += 2
        self.ax.set_title(title, color='#09376B', fontsize=20, weight='regular')
        self.ax.legend(
            [*wedges, *wedges2],
            [
                self._lang['pie']['legend_profile'],
                self._lang['pie']['legend_stranger'],
                self._lang['pie']['legend_norm_temp'],
                self._lang['pie']['legend_heat_temp']
            ],
            loc='best',
            bbox_to_anchor=(0.1, 0.7),
            fontsize=14,
            framealpha=0,
            labelcolor='#09376B'
        )

    def create_pie_chart_number_persons(self, low: str = None, high: str = None):
        pass

    def create_histogram_temperatures(self, identifier: int, time: tuple = None, temperature: tuple = None):
        pass

    def create_line_graph_temperatures(self, identifier: int, time: tuple = None, temperature: tuple = None):
        name = self.database_management.get_profile_name(identifier)
        statistics = self.database_management.get_statistics(
            identifiers=[identifier],
            time=time,
            temperature=temperature
        )
        statistics.sort(key=lambda x: x.time)
        temperatures = []
        times = []
        for statistic in statistics:
            temperatures.append(float(statistic.temperature))
            times.append(statistic.time.timestamp())
        self.ax.clear()
        temperatures = np.array(temperatures)
        times = np.array(times)
        self.ax.plot(times, temperatures, '#87B7E3', linewidth=3, marker='o')
        self.ax.grid(True, color='#09376B')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_ylabel(self._lang['chart1']['y'], color='#09376B', fontsize=20)
        self.ax.set_title(name, color='#09376B', fontsize=24, weight='regular')
        labels = [datetime.datetime.fromtimestamp(item).strftime('%m/%d %H:%M') for item in
                  self.ax.get_xticks().tolist()]
        self.ax.set_xticklabels(labels, color='#09376B')
        self.ax.tick_params(colors='#09376B', which='both')

    def create_map_temperatures(self, identifier: int, time: tuple = None, temperature: tuple = None):
        name = self.database_management.get_profile_name(identifier)
        statistics = self.database_management.get_statistics(
            identifiers=[identifier],
            time=time,
            temperature=temperature
        )
        statistics.sort(key=lambda x: x.time)
        temperatures = []
        times = []
        dates = []
        for statistic in statistics:
            temperatures.append(float(statistic.temperature))
            time = statistic.time.time()
            times.append(datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=0).total_seconds())
            dates.append(statistic.time.date())
        dates = mdates.date2num(dates)
        self.ax.clear()
        hb = self.ax.hexbin(x=dates, y=times, C=temperatures, cmap='viridis', gridsize=25)
        cb = self.figure.colorbar(hb, ax=self.ax, pad=0)
        cb.outline.set_visible(False)
        cb.set_label(self._lang['chart2']['bar'], fontsize=20, color='#09376B')
        cb.ax.tick_params(color='#09376B', labelcolor='#09376B')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        labels = [
            str(datetime.timedelta(seconds=item))
            for item in self.ax.get_yticks().tolist()
        ]
        self.ax.set_yticklabels(labels, color='#09376B')
        labels = [
            mdates.num2date(item).strftime('%m-%d')
            for item in self.ax.get_xticks().tolist()
        ]
        self.ax.set_xticklabels(labels, color='#09376B')
        self.ax.tick_params(colors='#09376B', which='both')
        self.ax.set_title(name, color='#09376B', fontsize=24)

    def create_map_similar(self, statistics: list):
        pass

    def save(self, filename):
        self.figure.savefig(filename)
