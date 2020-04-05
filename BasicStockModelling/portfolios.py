import datetime

import monte_carlo_sim
import portfolio
import matplotlib.pyplot as plt
import numpy as np
import beautifultable as btable


def project_transactions(transaction, lookback_days, projection_days, iterations=1):
    historical_data = monte_carlo_sim.LoadHistoricalData(transaction.symbol)
    # historical_data.load_data_for_date_range(end=transaction.purchase_date, duration=lookback_days)
    historical_data.load_data_for_date_range(end=datetime.date(2020, 1, 1), duration=lookback_days)
    stock_change_sampler = monte_carlo_sim.StockChangeSampler(historical_data.get_price_change_data(), random_seed=0)
    projector = monte_carlo_sim.StockProjector(stock_change_sampler)
    all_projections = []
    for i in range(iterations):
        projection = projector.project(projection_days, transaction.purchase_price)
        all_projections.append(projection)
    all_projections = np.array(all_projections)
    projection_means = np.mean(all_projections, axis=0)
    projection_2_std = np.std(all_projections, axis=0)
    so_far = historical_data.load_data_for_date_range(start=transaction.purchase_date, end=datetime.datetime.today()).get_price_data()
    return projection_means, projection_2_std, all_projections, so_far


def plot_one_projection(projection):
    plt.plot(projection, 'x-')


AMMAR_PORTFOLIO = [portfolio.Transaction('IVOG', datetime.date(2020, 3, 25), 90.00, 11),
                   portfolio.Transaction('UAL', datetime.date(2020, 3, 20), 28.81, 40),
                   portfolio.Transaction('UBER', datetime.date(2020, 3, 18), 20.00, 100),
                   portfolio.Transaction('AAL', datetime.date(2020, 4, 3), 10.00, 100),
                   portfolio.Transaction('JETS', datetime.date(2020, 4, 3), 12.50, 100),
                   portfolio.Transaction('MGM', datetime.date(2020, 4, 2), 11.00, 100)]
ITERATIONS = 100


def plot_single_projection(mean, std, all, so_far):
    step = 10
    mean_sub = mean[::step]
    std_sub = std[::step]
    plt.errorbar(range(0, len(mean), step), mean_sub, yerr=std_sub)
    for projection in all:
        plt.plot(projection, alpha=0.2)
    plt.plot(mean)
    plt.plot(so_far, 'g:')
    plt.title('Symbol: {}'.format(transaction.symbol))
    plt.show()


table = btable.BeautifulTable()
project_out_days = 600
print('Iterations: {}'.format(ITERATIONS))
table.column_headers = ['Symbol', 'Purchase Price', 'Current Price', 'Current Return (%)', 'Projected Out {} Days'.format(project_out_days), 'Projected Return (%)']
for transaction in AMMAR_PORTFOLIO:
    all_projections = []
    mean, std, all, so_far = project_transactions(transaction, 200, project_out_days, 10)
    # plot_single_projection(mean, std, all, so_far)
    percent_return = (so_far[-1] - transaction.purchase_price) / transaction.purchase_price * 100
    projected_return = (mean[-1] - transaction.purchase_price) / transaction.purchase_price * 100
    table.append_row([transaction.symbol, transaction.purchase_price, so_far[-1], percent_return, mean[-1], projected_return])
print(table)