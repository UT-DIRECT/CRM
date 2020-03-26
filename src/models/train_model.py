import matplotlib.pyplot as plt
import numpy as np

from lmfit import Parameters, Model
from scipy.optimize import curve_fit
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import *
from sklearn.metrics  import r2_score, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR, NuSVR, LinearSVR

from ..helpers.figures import plot_helper, fig_filename, fig_dir

filename = "/Users/akhilpotla/ut/research/crm_validation/data/interim/CRMP_Corrected_July16_2018.csv"

class CRM():

    def __init__(self, filename):
        [
            self.Time, self.Random_inj1, self.Random_inj2, self.Fixed_inj1,
            self.Net_Fixed_inj1, self.Fixed_inj2, self.Net_Fixed_inj2,
            self.Prod1, self.Net_Prod1, self.Prod2, self.Net_Prod2,
            self.Prod3, self.Net_Prod3, self.Prod4, self.Net_Prod4
        ] = np.loadtxt(filename, delimiter=',', skiprows=1).T
        self.producers = np.array(
            [self.Prod1, self.Prod2, self.Prod3, self.Prod4]
        )
        self.producer_names = [
            'Producer 1', 'Producer 2', 'Producer 3', 'Producer 4'
        ]
        self.net_production_by_producer = np.array(
            [self.Net_Prod1, self.Net_Prod2, self.Net_Prod3, self.Net_Prod4]
        )
        self.q2 = lambda X, f1, f2, tau: X[0] * np.exp(-1 / tau) + (1 - np.exp(-1 / tau)) * (X[1] * f1 + X[2] * f2)
        self.N2 = lambda X: X[0] + X[1]
        self.p0 = .5, .5, 5
        self.step_sizes = np.linspace(2, 12, num=11)
        self.output_header = "producer, step_size, CRM_r2, CSE_mse, Linear_Regression_r2, Linear_Regression_mse, Bayesian_Ridge_r2, Bayesian_Ridge_mse"
        self.net_production_forward_walk_predictions_output_file = '/Users/akhilpotla/ut/research/crm_validation/data/interim/net_production_forward_walk_predictions.txt'

    def fit_producer(self, producer):
        X = np.array([
            producer[:-1], self.Fixed_inj1[:-1], self.Fixed_inj2[:-1]
        ])
        y = producer[1:]
        model = Model(self.q2, independent_vars=['X'])
        params = Parameters()

        params.add('f1', value=0.5, min=0, max=1)
        params.add('f2', expr='1-f1')
        params.add('tau', value=5, min=1, max=30)
        results = model.fit(y, X=X, params=params)

        pars = []
        pars.append(results.values['f1'])
        pars.append(results.values['f2'])
        pars.append(results.values['tau'])
        return pars

    def fit_producers(self):
        t = self.Time[1:]
        producers = self.producers
        with open('/Users/akhilpotla/ut/research/crm_validation/data/interim/crm_producers_fit_results.txt', 'w') as f:
            for i in range(len(producers)):
                producer = producers[i]
                X = np.array([
                    producer[:-1], self.Fixed_inj1[:-1], self.Fixed_inj2[:-1]
                ])
                y = producer[1:]
                [f1, f2, tau] = self.fit_producer(producer)
                q2 = self.q2(X, f1, f2, tau)
                r2 = r2_score(q2, y)
                mse = mean_squared_error(q2, y)
                f.write('==========================================================\n')
                f.write('Producer {}\n'.format(i + 1))
                f.write('r2 score: {}\n'.format(r2))
                f.write('MSE: {}\n'.format(mse))
                f.write('\n\n')
                plt.figure()
                plt.scatter(t, y)
                plt.plot(t, q2, 'r')
                plt.text(80, 0.5, 'R-squared = %0.8f' % r2)
                plot_helper(
                    title='Producer {}'.format(i + 1),
                    xlabel='Time',
                    ylabel='Production Rate',
                    legend=['CRM', 'Data'],
                    save=True
                )
                plt.close()

    def fit_net_production(self, N1, q2):
        return N1 + q2

    def fit_net_productions(self):
        t = self.Time[1:]
        producers = self.producers
        net_productions = self.net_production_by_producer
        for i in range(len(producers)):
            producer = producers[i]
            net_production = net_productions[i]
            [f1, f2, tau] = self.fit_producer(producer)
            X = np.array([
                producer[:-1], self.Fixed_inj1[:-1], self.Fixed_inj2[:-1]
            ])
            q2 = self.q2(X, f1, f2, tau)
            X = [net_production[:-1], q2]
            y = net_production[1:]
            predicted_net_production = self.N2(X)
            r2 = r2_score(y, predicted_net_production)
            plt.figure()
            plt.scatter(t, y)
            plt.plot(t, predicted_net_production, 'r')
            plt.text(80, 0.5, 'R-squared = %0.8f' % r2)
            plot_helper(
                title='Producer {}'.format(i + 1),
                xlabel='Time',
                ylabel='Net Production',
                legend=['CRM', 'Data'],
                save=True
            )
            plt.close()

    def crm_predict_net_production(self):
        net_productions = self.net_production_by_producer
        producers = self.producers
        with open('/Users/akhilpotla/ut/research/crm_validation/data/interim/crm_forward_walk_results.txt', 'w') as f:
            for i in range(len(self.producers)):
                producer = self.producers[i]
                net_production = net_productions[i]
                X = np.array([
                    producer[:-1], self.Fixed_inj1[:-1], self.Fixed_inj2[:-1]
                ])
                [f1, f2, tau] = self.fit_producer(producer)
                q2 = self.q2(X, f1, f2, tau)
                X2 = np.array([net_production[:-1], q2]).T
                y2 = net_production[1:]
                f.write('==========================================================\n')
                f.write('PRODUCER {}\n'.format(i + 1))
                for step_size in self.step_sizes:
                    [tscv, n_splits] = self.time_series_cross_validator(X2, step_size)
                    r2_sum = 0
                    mse_sum = 0
                    for train_index, test_index in tscv.split(X2):
                        x_train, x_test = (X2[train_index]).T, (X2[test_index]).T
                        y_train, y_test = y2[train_index], y2[test_index]
                        y_predict = self.N2(x_test)
                        r2_sum += r2_score(y_predict, y_test)
                        mse_sum += mean_squared_error(y_predict, y_test)
                    f.write('step size: {}\n'.format(step_size))
                    f.write('Average r2: {}\n'.format(r2_sum / n_splits))
                    f.write('Average MSE: {}\n'.format(mse_sum/ n_splits))
                    f.write('\n')
                f.write('\n\n')

    def net_production_forward_walk_predictions(self):
        net_productions = self.net_production_by_producer
        producers = self.producers
        with open(self.net_production_forward_walk_predictions_output_file, 'w') as f:
            f.write('{}\n'.format(self.output_header))
            for i in range(len(producers)):
                producer = self.producers[i]
                net_production = net_productions[i]
                X = np.array([
                    producer[:-1], self.Fixed_inj1[:-1], self.Fixed_inj2[:-1]
                ])
                [f1, f2, tau] = self.fit_producer(producer)
                q2 = self.q2(X, f1, f2, tau)
                X2 = np.array([net_production[:-1], q2]).T
                y = net_production[1:]
                models = [LinearRegression(), BayesianRidge()]
                for step_size in self.step_sizes:
                    r2_sum = 0
                    mse_sum = 0
                    tscv, n_splits = self.time_series_cross_validator(X2, step_size)
                    for train_index, test_index in tscv.split(X2):
                        x_train, x_test = (X2[train_index]).T, (X2[test_index]).T
                        y_train, y_test = y[train_index], y[test_index]
                        y_predict = self.N2(x_test)
                        r2_sum += r2_score(y_predict, y_test)
                        mse_sum += mean_squared_error(y_predict, y_test)
                    CRM_r2 = r2_sum / n_splits
                    CRM_mse = mse_sum / n_splits
                    models_performance_parameters = []
                    for model in models:
                        r2, mse = self.forward_walk_and_ML(X.T, y, model, step_size)
                        models_performance_parameters.append(r2)
                        models_performance_parameters.append(mse)
                    f.write('{} {} {} {} {} {} {} {}\n'.format(i + 1, int(step_size), CRM_r2, CRM_mse, *models_performance_parameters))

    def net_production_forward_walk_predictions_plot(self):
        labels = [int(step_size) for step_size in self.step_sizes]
        prediction_results = np.genfromtxt(self.net_production_forward_walk_predictions_output_file, skip_header=1)
        x = np.arange(len(labels))
        width = 0.3
        for i in range(4):
            fig, ax = plt.subplots()
            producer = i + 1
            producer_rows = np.where(prediction_results[:,0] == producer)
            producer_results = prediction_results[producer_rows]
            CRM_mse = producer_results[:, 3]
            Linear_Regression_mse = producer_results[:, 5]
            Bayesian_Ridge_mse = producer_results[:, 7]
            rects1 = ax.bar(x - width, CRM_mse, width, label='CRM, mse')
            rects2 = ax.bar(x, Linear_Regression_mse, width, label='Linear Regression, mse')
            rects3 = ax.bar(x + width, Bayesian_Ridge_mse, width, label='Bayesian Ridge, mse')
            xlabel = 'Step Size'
            ylabel = 'Mean Squared Error'
            title = 'Producer {}'.format(producer)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_yscale('log')
            ax.set_title(title)
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend()
            fig_file = fig_filename(title, xlabel, ylabel)
            plt.savefig('{}{}'.format(fig_dir, fig_file))

    def time_series_cross_validator(self, X, step_size):
        n_splits = (int(len(X) / step_size) - 1)
        tscv = TimeSeriesSplit(n_splits=n_splits)
        return [tscv, n_splits]

    def forward_walk_and_ML(self, X, y, model, step_size):
        [tscv, n_splits] = self.time_series_cross_validator(X, step_size)
        r2_sum = 0
        mse_sum = 0
        for train_index, test_index in tscv.split(X):
            x_train, x_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            model.fit(x_train, y_train)
            y_predict = model.predict(x_test)
            r2_sum += r2_score(y_predict, y_test)
            mse_sum += mean_squared_error(y_predict, y_test)
        return ((r2_sum / n_splits), (mse_sum / n_splits))

    def fit_ML_production_rate(self):
        producers = self.producers
        with open('/Users/akhilpotla/ut/research/crm_validation/data/interim/train_output_production_rate.txt', 'w') as f:
            for i in range(len(producers)):
                production = producers[i]
                X = np.array([
                    production[:-1], self.Net_Fixed_inj1[:-1], self.Net_Fixed_inj2[:-1]
                ]).T
                y = production[1:]
                n_splits = (int(len(X) / 2) - 1)
                tscv = TimeSeriesSplit(n_splits=n_splits)
                models = [LinearRegression(), BayesianRidge()]
                # models = [LinearRegression(), Lasso(alpha=0, max_iter=100, tol=0.0001),
                #         Ridge(), ElasticNet(),  Lars(),
                #         LassoLars(), OrthogonalMatchingPursuit(), BayesianRidge(),
                #         ARDRegression(), SGDRegressor(), PassiveAggressiveRegressor(),
                #         KernelRidge(), SVR(), NuSVR(), LinearSVR(),
                #         KNeighborsRegressor(n_neighbors=3),
                #         RadiusNeighborsRegressor(radius=10000),
                #         GaussianProcessRegressor(), MLPRegressor(hidden_layer_sizes=(60,))]
                f.write('==========================================================\n')
                f.write('Producer {}\n'.format(i + 1))
                for model in models:
                    f.write('model: {}\n'.format(type(model)))
                    for step_size in self.step_sizes:
                        r2, mse = self.forward_walk_and_ML(X, y, model, step_size)
                        f.write('step size: {}\n'.format(step_size))
                        f.write('Average r2: {}\n'.format(r2))
                        f.write('Average MSE: {}\n'.format(mse))
                        f.write('\n')
                f.write('\n')
                f.write('\n')
                f.write('\n')

    def predict_ML_net_production(self):
        producers = self.producers
        net_productions = self.net_production_by_producer
        with open('/Users/akhilpotla/ut/research/crm_validation/data/interim/train_output_net_production.txt', 'w') as f:
            for i in range(len(producers)):
                production = producers[i]
                net_production = self.net_production_by_producer[i]
                X = np.array([
                    production[:-1], net_production[:-1], self.Net_Fixed_inj1[:-1], self.Net_Fixed_inj2[:-1]
                ]).T
                y = net_production[1:]
                models = [LinearRegression(), BayesianRidge()]
                # models = [LinearRegression(), Lasso(alpha=0, max_iter=100, tol=0.0001),
                #         Ridge(), ElasticNet(),  Lars(),
                #         LassoLars(), OrthogonalMatchingPursuit(), BayesianRidge(),
                #         ARDRegression(), SGDRegressor(), PassiveAggressiveRegressor(),
                #         KernelRidge(), SVR(), NuSVR(), LinearSVR(),
                #         KNeighborsRegressor(n_neighbors=3),
                #         RadiusNeighborsRegressor(radius=10000),
                #         GaussianProcessRegressor(), MLPRegressor(hidden_layer_sizes=(60,))]
                f.write('==========================================================\n')
                f.write('Producer {}\n'.format(i + 1))
                for model in models:
                    f.write('model: {}\n'.format(type(model)))
                    for step_size in self.step_sizes:
                        r2, mse = self.forward_walk_and_ML(X, y, model, step_size)
                        f.write('step size: {}\n'.format(step_size))
                        f.write('Average r2: {}\n'.format(r2))
                        f.write('Average MSE: {}\n'.format(mse))
                        f.write('\n')
                f.write('\n')
                f.write('\n')
                f.write('\n')

    def plot_producers_vs_time(self):
        plt.figure()
        plt.plot(self.Time, self.producers.T)
        plot_helper(
            title='Production Rate vs Time',
            xlabel='Time',
            ylabel='Production Rate',
            legend=self.producer_names,
            save=True
        )
        plt.close()

    def plot_net_production_vs_time(self):
        plt.figure()
        plt.plot(self.Time, self.net_production_by_producer.T)
        plot_helper(
            title='Total Production vs Time',
            xlabel='Time',
            ylabel='Net Production',
            legend=self.producer_names,
            save=True
        )
        plt.close()

    def plot_producers_vs_injector(self):
        injectors = [self.Fixed_inj1, self.Fixed_inj2]
        for i in range(len(injectors)):
            plt.figure()
            for producer in self.producers:
                plt.scatter(injectors[i], producer)
            plot_helper(
                title='Injector {}'.format(i + 1),
                xlabel='Injection Rate',
                ylabel='Production Rate',
                legend=self.producer_names,
                save=True
            )
            plt.close()

    def plot_net_production_vs_injector(self):
        net_injections = [self.Net_Fixed_inj1, self.Net_Fixed_inj2]
        for i in range(len(net_injections)):
            plt.figure()
            for net_production in self.net_production_by_producer:
                plt.plot(self.Net_Fixed_inj1, net_production)
            plot_helper(
                title='Injector {}'.format(i + 1),
                xlabel='Injection Rate',
                ylabel='Net Production',
                legend=self.producer_names,
                save=True
            )
            plt.close()

    def production_rate_predictions(self):
        pass

    def net_production_predictions(self):
        self.crm_predict_net_production()
        self.predict_ML_net_production()

model = CRM(filename)
model.fit_producers()
model.fit_net_productions()
model.plot_producers_vs_time()
model.plot_net_production_vs_time()
model.plot_producers_vs_injector()
model.plot_net_production_vs_injector()
model.fit_ML_production_rate()
model.net_production_predictions()
model.net_production_forward_walk_predictions()
model.net_production_forward_walk_predictions_plot()
