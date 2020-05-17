import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models import (injectors, net_productions,
    producers, producer_names, step_sizes, Time)
from src.helpers.figures import bar_plot_helper, bar_plot_formater, plot_helper
from src.visualization import q_predictions_metrics_file


def producers_vs_time():
    plt.figure()
    plt.plot(Time, producers.T)
    plot_helper(
        title='Production Rate vs Time',
        xlabel='Time',
        ylabel='Production Rate',
        legend=producer_names,
        save=True
    )


def net_production_vs_time():
    plt.figure()
    plt.plot(Time, net_productions.T)
    plot_helper(
        title='Total Production vs Time',
        xlabel='Time',
        ylabel='Net Production',
        legend=producer_names,
        save=True
    )


def producers_vs_injector():
    for i in range(len(injectors)):
        plt.figure()
        for producer in producers:
            plt.scatter(injectors[i], producer)
        plot_helper(
            title='Injector {}'.format(i + 1),
            xlabel='Injection Rate',
            ylabel='Production Rate',
            legend=producer_names,
            save=True
        )


def net_production_estimators_and_time_steps():
    x_labels = [int(step_size) for step_size in step_sizes]
    predictions_metrics_df = pd.read_csv(q_predictions_metrics_file)
    x = np.arange(len(x_labels))
    width = 0.15
    bar_labels = [
        'CRM, mse', 'Linear Regression, mse', 'Bayesian Ridge, mse',
        'Lasso, mse', 'Elastic, mse'
    ]
    for i in range(len(producers)):
        producer = i + 1
        producer_rows_df = predictions_metrics_df.loc[predictions_metrics_df['Producer'] == producer]
        crm_mse = []
        linear_regression_mse = []
        bayesian_ridge_mse = []
        lasso_mse = []
        elastic_mse = []
        heights = [
            crm_mse, linear_regression_mse, bayesian_ridge_mse, lasso_mse,
            elastic_mse
        ]
        models = ['CRM', 'LinearRegression', 'BayesianRidge', 'Lasso', 'ElasticNet']
        for i in range(len(models)):
            mses = producer_rows_df.loc[producer_rows_df['Model'] == models[i]]
            for step_size in step_sizes:
                mse = mses.loc[mses['Step size'] == step_size]['MSE']
                heights[i].append(float(mse))

        title = 'Production Rate Estimators Producer {}'.format(producer)
        xlabel = 'Step Size'
        ylabel = 'Mean Squared Error'
        bar_plot_helper(width, x, x_labels, bar_labels, heights)
        bar_plot_formater(x, x_labels, title, xlabel, ylabel)


def net_production_good_estimators_and_time_steps():
    x_labels = [int(step_size) for step_size in step_sizes]
    predictions_metrics_df = pd.read_csv(q_predictions_metrics_file)
    x = np.arange(len(x_labels))
    width = 0.23
    bar_labels = [
        'CRM, mse', 'Linear Regression, mse', 'Bayesian Ridge, mse'
    ]
    for i in range(len(producers)):
        producer = i + 1
        producer_rows_df = predictions_metrics_df.loc[predictions_metrics_df['Producer'] == producer]
        crm_mse = []
        linear_regression_mse = []
        bayesian_ridge_mse = []
        heights = [
            crm_mse, linear_regression_mse, bayesian_ridge_mse
        ]
        models = ['CRM', 'LinearRegression', 'BayesianRidge']
        for i in range(len(models)):
            mses = producer_rows_df.loc[producer_rows_df['Model'] == models[i]]
            for step_size in step_sizes:
                mse = mses.loc[mses['Step size'] == step_size]['MSE']
                heights[i].append(float(mse))

        title = 'Production Rate Estimators Good Estimator MSEs Producer {}'.format(producer)
        xlabel = 'Step Size'
        ylabel = 'Mean Squared Error'
        bar_plot_helper(width, x, x_labels, bar_labels, heights)
        bar_plot_formater(x, x_labels, title, xlabel, ylabel)


def animated_net_production_predictions():
    pass


producers_vs_time()
net_production_vs_time()
producers_vs_injector()
net_production_estimators_and_time_steps()
net_production_good_estimators_and_time_steps()
