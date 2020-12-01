import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.visualization import INPUTS


sensitivity_analysis_fit_file = INPUTS['crmp']['crmp']['fit']['sensitivity_analysis']
sensitivity_analysis_fit_df = pd.read_csv(sensitivity_analysis_fit_file)
best_guesses_fit_file = INPUTS['crmp']['crmp']['fit']['best_guesses']
best_guesses_fit_data = {
    'tau_initial': [], 'f1_initial': [], 'f2_initial': [], 'MSE': []
}

sensitivity_analysis_predict_file = INPUTS['crmp']['crmp']['predict']['sensitivity_analysis']
sensitivity_analysis_predict_df = pd.read_csv(sensitivity_analysis_predict_file)
best_guesses_predict_file = INPUTS['crmp']['crmp']['predict']['best_guesses']
best_guesses_predict_data = {
    'tau_initial': [], 'f1_initial': [], 'f2_initial': [], 'MSE': []
}

f1 = np.linspace(0, 1, 11)
f2 = np.ones(11) - f1
tau = np.linspace(0.01, 100, 101)
p0s = []
for i in tau:
    for j in range(len(f1)):
        p0s.append([i, f1[j], f2[j]])

def _initial_guesses_from_df(df, tau, f1):
    return df.loc[(df['tau_initial'] == tau) & (df['f1_initial'] == f1)]


def best_initial_guesses_fit():
    for p0 in p0s:
        df = _initial_guesses_from_df(
            sensitivity_analysis_fit_df, p0[0], p0[1]
        )
        summed_df = df.sum(axis=0)
        best_guesses_fit_data['tau_initial'].append(p0[0])
        best_guesses_fit_data['f1_initial'].append(p0[1])
        best_guesses_fit_data['f2_initial'].append(p0[2])
        best_guesses_fit_data['MSE'].append(summed_df['MSE'])

    best_guesses_df = pd.DataFrame(best_guesses_fit_data)
    best_guesses_df.to_csv(best_guesses_fit_file)


def best_initial_guesses_predict():
    for p0 in p0s:
        df = _initial_guesses_from_df(
            sensitivity_analysis_predict_df, p0[0], p0[1]
        )
        summed_df = df.sum(axis=0)
        best_guesses_predict_data['tau_initial'].append(p0[0])
        best_guesses_predict_data['f1_initial'].append(p0[1])
        best_guesses_predict_data['f2_initial'].append(p0[2])
        best_guesses_predict_data['MSE'].append(summed_df['MSE'])

    best_guesses_df = pd.DataFrame(best_guesses_predict_data)
    best_guesses_df.to_csv(best_guesses_predict_file)


best_initial_guesses_fit()
best_initial_guesses_predict()
