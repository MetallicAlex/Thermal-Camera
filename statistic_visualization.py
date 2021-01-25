from matplotlib import pyplot as plt, ticker
import pandas as pd
import numpy as np
import models


class Visualization:
    def __init__(self):
        pass

    @staticmethod
    def show_plot_employee(employee_id, start_date=None, end_date=None):
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
            times = np.array([time.strftime('%Y-%m-%d %H:%M:%S') for time, _ in statistics])
            temperatures = np.array([float(temperature) for _, temperature in statistics])
            df = pd.DataFrame(temperatures, index=times)
            ax = plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            df.plot(kind='line', style='ko-', legend=False,
                    xlabel='Datetime', ylabel='Temperature', title=employee, grid=True, ax=ax)
            plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='x-small')
            plt.show()

    @staticmethod
    def show_plot_employees(employees_id, start_date=None, end_date=None):
        with models.get_session() as session:
            """statistics = session.query(models.Employee.name, models.Statistic.id_employee,
                                       models.Statistic.time, models.Statistic.temperature) \
                .join(models.Employee, models.Employee.id == models.Statistic.id_employee) \
                .filter(models.Employee.id.in_(employees_id)).all()"""
            fig, axes = plt.subplots(nrows=len(employees_id), ncols=1)
            fig.subplots_adjust(wspace=0.5, hspace=0.5)
            for index, employee_id in enumerate(employees_id):
                employee = session.query(models.Employee.name).filter(models.Employee.id == employee_id).scalar()
                if start_date and end_date is not None:
                    statistics = session.query(models.Statistic.time, models.Statistic.temperature) \
                        .filter(models.Statistic.id_employee == employee_id,
                                models.Statistic.time >= start_date,
                                models.Statistic.time <= end_date).all()
                else:
                    statistics = session.query(models.Statistic.time, models.Statistic.temperature) \
                        .filter(models.Statistic.id_employee == employee_id).all()
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
        pass


if __name__ == '__main__':
    Visualization.show_plot_employee(2)
    Visualization.show_plot_employees(employees_id=[1, 2, 3, 4], start_date='2021-01-17 00:00:00',
                                      end_date='2021-01-20 23:59:59')
