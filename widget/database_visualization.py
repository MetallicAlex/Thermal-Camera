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
            stat_time: tuple = None,
            temperature: tuple = None,
            name: str = None,
            identifiers: list = None,
            devices: list = None,
            title: str = 'All time passage of people'  # Passage of people for the current day
    ):
        self.ax.clear()
        # self.figure.set_facecolor('#272c36')
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
        print(number_temperatures, number_passages)
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
                f'[N - {number_temperatures[j]}; H - {number_temperatures[j + 1]}]',
                xy=(x, y),
                xytext=(2 * np.sign(x), 1.5 * y),
                horizontalalignment='center', fontsize=16, **kw)
            j += 2
        self.ax.set_title(title, color='#09376B', fontsize=20, weight='regular')
        self.ax.legend(
            [*wedges, *wedges2],
            ['Profile Passage', 'Stranger Passage', 'Normal Temperature (N)', 'Heat Temperature (H)'],
            loc='best',
            bbox_to_anchor=(0.1, 0.7),
            fontsize=14,
            framealpha=0,
            labelcolor='#09376B'
        )

    def create_pie_chart_number_persons(self, low: str = None, high: str = None):
        pass

    def create_histogram_number_persons(self, low: str = None, high: str = None):
        pass

    def create_line_graph_temperatures(self, statistics: list):
        statistics = self.database_management.get_statistics(identifiers=[1])
        statistics.sort(key=lambda x: x.time)
        temperatures = []
        times = []
        dates = []
        for statistic in statistics:
            temperatures.append(float(statistic.temperature))
            time = statistic.time.time()
            times.append(datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds())
            dates.append(statistic.time.date())
        dates = mdates.date2num(dates)
        self.ax.clear()
        # self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # self.ax.xaxis_date()
        self.ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        self.ax.set(
            ylim=(
                dates[0],
                dates[-1]
            ),
            xlim=(
                datetime.timedelta(hours=0, minutes=0, seconds=0).total_seconds(),
                datetime.timedelta(hours=23, minutes=59, seconds=59).total_seconds()
            )
        )
        hb = self.ax.hexbin(y=dates, x=times, C=temperatures, cmap='coolwarm', bins='log')

    def create_map_temperatures(self):
        statistics = self.database_management.get_statistics(identifiers=[1])
        print(len(statistics))
        statistics.sort(key=lambda x: x.time)
        temperatures = []
        times = []
        dates = []
        for statistic in statistics:
            temperatures.append(float(statistic.temperature))
            time = statistic.time.time()
            times.append(datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds())
            dates.append(statistic.time.date())
        dates = mdates.date2num(dates)
        print(len(times))
        print(dates)
        self.ax.clear()
        # self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # self.ax.xaxis_date()
        self.ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        self.ax.set(
            xlim=(
                dates[0],
                dates[-1]
            ),
            ylim=(
                datetime.timedelta(hours=0, minutes=0, seconds=0).total_seconds(),
                datetime.timedelta(hours=23, minutes=59, seconds=59).total_seconds()
            )
        )
        hb = self.ax.scatter(x=dates, y=times, s=100, c=temperatures, cmap='coolwarm')
        cb = self.figure.colorbar(hb, ax=self.ax)

        self.ax.set_title('title', color='#09376B', fontsize=20, weight='regular')
        # ax = df.plot.hexbin(x='x', y='y', C='temperature', gridsize=10,
        #                     cmap='coolwarm', title=employee, grid=False,
        #                     vmin=35.0, vmax=38.5)
        # ax.set_xlabel("Date")
        # ax.set_ylabel("Time")
        # ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        # ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: str(dt.timedelta(seconds=x))))

    def create_map_similar(self, statistics: list):
        pass

    def save(self, filename):
        self.figure.savefig(filename)
