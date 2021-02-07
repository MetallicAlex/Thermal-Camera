from matplotlib import pyplot as plt, ticker, dates
import pandas as pd
import numpy as np
import models
import datetime as dt


class Visualization:
    def __init__(self):
        pass

    @staticmethod
    def __get_statistics_strangers():
        pass

    @staticmethod
    def __get_statistics_from_database(employee_id, start_date=None, end_date=None):
        with models.get_session() as session:
            employee = session.query(models.Employee.name).filter(models.Employee.id == employee_id).scalar()
            if start_date and end_date is not None:
                statistics = session.query(models.Statistic.time, models.Statistic.temperature) \
                    .filter(models.Statistic.id_employee == employee_id,
                            models.Statistic.time >= start_date,
                            models.Statistic.time <= end_date).all()
            else:
                statistics = session.query(models.Statistic.time, models.Statistic.temperature) \
                    .filter(models.Statistic.id_employee == employee_id).all()
        return statistics, employee

    @staticmethod
    def __get_similar_from_database(employee_id, start_date=None, end_date=None):
        with models.get_session() as session:
            employee = session.query(models.Employee.name).filter(models.Employee.id == employee_id).scalar()
            if start_date and end_date is not None:
                similar = session.query(models.Statistic.time, models.Statistic.similar) \
                    .filter(models.Statistic.id_employee == employee_id,
                            models.Statistic.time >= start_date,
                            models.Statistic.time <= end_date).all()
            else:
                similar = session.query(models.Statistic.time, models.Statistic.similar) \
                    .filter(models.Statistic.id_employee == employee_id).all()
        return similar, employee

    @staticmethod
    def __statistic_to_dataframe(data, name='temperature'):
        statistics = {'x': [], 'y': [], 'date': [], 'time': [], name: []}
        for datetime, temperature in data:
            time = datetime.strptime(datetime.strftime('%H:%M'), '%H:%M')
            statistics['date'].append(datetime.strftime('%Y-%m-%d'))
            statistics['time'].append(datetime.strftime('%H:%M'))
            statistics[name].append(float(temperature))
            statistics['y'].append(time.second + time.minute * 60 + time.hour * 3600)
        statistics['x'] = dates.date2num(statistics['date'])
        return pd.DataFrame(data=statistics).sort_index()

    @staticmethod
    def show_plot_employee(employee_id, start_date=None, end_date=None):
        with plt.style.context('seaborn'):
            statistics, employee = Visualization.__get_statistics_from_database(employee_id, start_date, end_date)
            times = np.array([time.strftime('%Y-%m-%d %H:%M:%S') for time, _ in statistics])
            temperatures = np.array([float(temperature) for _, temperature in statistics])
            df = pd.DataFrame(temperatures, index=times)
            ax = plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
            df.plot(kind='line', style='k-', legend=False,
                    xlabel='Datetime', ylabel='Temperature', title=employee, grid=True, ax=ax)
            plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='xx-small')
        plt.show()

    @staticmethod
    def show_plot_employees(employees_id, start_date=None, end_date=None):
        with models.get_session() as session:
            """statistics = session.query(models.Employee.name, models.Statistic.id_employee,
                                       models.Statistic.time, models.Statistic.temperature) \
                .join(models.Employee, models.Employee.id == models.Statistic.id_employee) \
                .filter(models.Employee.id.in_(employees_id)).all()"""
            with plt.style.context('seaborn'):
                fig, axes = plt.subplots(nrows=len(employees_id), ncols=1)
                fig.subplots_adjust(wspace=0.5, hspace=0.5)
                for index, employee_id in enumerate(employees_id):
                    statistics, employee = Visualization.__get_statistics_from_database(employee_id, start_date, end_date)
                    times = np.array([time.strftime('%Y-%m-%d') for time, _ in statistics])
                    temperatures = np.array([float(temperature) for _, temperature in statistics])
                    # Create plot
                    df = pd.DataFrame(temperatures, index=times)
                    axes[index].set_xticks(temperatures)
                    axes[index].xaxis.set_major_locator(ticker.MultipleLocator(2))
                    labels = axes[index].set_xticklabels(times, horizontalalignment='center',
                                                         fontweight='light', fontsize='xx-small')
                    for i, label in enumerate(labels):
                        label.set_y(label.get_position()[1] - (i % 2) * 0.075)
                    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='x-small')
                    df.plot(kind='line', style='ko-', legend=False,
                            xlabel='Datetime', ylabel='Temperature', title=employee, grid=True, ax=axes[index])
        plt.show()

    @staticmethod
    def show_temperature_map_employee(employee_id, start_date=None, end_date=None):
        statistics, employee = Visualization.__get_statistics_from_database(employee_id)
        df = Visualization.__statistic_to_dataframe(statistics)
        with plt.style.context('seaborn-notebook'):
            ax = df.plot.hexbin(x='x', y='y', C='temperature', gridsize=10,
                                cmap='coolwarm', title=employee, grid=False,
                                vmin=35.0, vmax=38.5)
            ax.set_xlabel("Date")
            ax.set_ylabel("Time")
            ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: str(dt.timedelta(seconds=x))))
        plt.show()

    @staticmethod
    def show_similar_map_employee(employee_id, start_date=None, end_date=None):
        similar, employee = Visualization.__get_similar_from_database(employee_id)
        df = Visualization.__statistic_to_dataframe(similar, name='similar')
        with plt.style.context('seaborn-notebook'):
            ax = df.plot.hexbin(x='x', y='y', C='similar', gridsize=10,
                                cmap='inferno', title=employee, grid=False, vmin=0.2, vmax=1)
            ax.set_xlabel("Date")
            ax.set_ylabel("Time")
            ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: str(dt.timedelta(seconds=x))))
        plt.show()

    @staticmethod
    def show_plot_comers(start_date=None, end_date=None):
        pass


if __name__ == '__main__':
    Visualization.show_plot_employee(3)
    Visualization.show_plot_employees(employees_id=[1, 3, 4, 5], start_date='2021-01-17 00:00:00',
                                      end_date='2021-01-20 23:59:59')
    Visualization.show_temperature_map_employee(1)
    Visualization.show_temperature_map_employee(3)
    Visualization.show_similar_map_employee(3)
    Visualization.show_similar_map_employee(1)
    Visualization.show_similar_map_employee(2)
