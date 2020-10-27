import pandas as pd

from src.config import INPUTS
from src.data.read_crmp import (injectors, net_productions, producers,
     producer_names)
from src.helpers.cross_validation import forward_walk_splitter
from src.helpers.features import net_production_dataset
from src.helpers.models import load_models, model_namer, test_model
from src.simulations import step_sizes


# Net Production Predictions

# Loading the previously serialized models
trained_models = load_models('icrmp')

# Loading the net production models up by producer
net_production_models_by_producer = {}
for producer in producer_names:
    producer_label = producer.lower().replace(' ', '_')
    keys_for_producer = []
    for key in trained_models.keys():
        if producer_label in key and 'net_' in key:
            keys_for_producer.append(key)
    net_production_models_by_producer[producer] = [trained_models[key] for key in keys_for_producer]

N_predictions_file = INPUTS['crmp']['N_predictions']
N_predictions_metrics_file = INPUTS['crmp']['N_predictions_metrics']
N_predictions_data = {
    'Producer': [], 'Model': [], 'Step size': [], 't_start': [], 't_end': [],
    't_i': [], 'Prediction': []
}
N_metrics_data = {
    'Producer': [], 'Model': [], 'Step size': [], 'r2': [], 'MSE': []
}
for i in range(len(producers)):
    producer_name = producer_names[i]
    producer_number = i + 1
    models = net_production_models_by_producer[producer_name]
    X, y = net_production_dataset(net_productions[i], producers[i], *injectors)

    for model in models:
        for step_size in step_sizes:
            test_split = forward_walk_splitter(X, y, step_size)[1]
            r2, mse, y_hat, time_step = test_model(X, y, model, test_split)
            N_metrics_data['Producer'].append(producer_number)
            N_metrics_data['Model'].append(model_namer(model))
            N_metrics_data['Step size'].append(step_size)
            N_metrics_data['r2'].append(r2)
            N_metrics_data['MSE'].append(mse)
            for i in range(len(y_hat)):
                y_hat_i = y_hat[i]
                time_step_i = time_step[i]
                t_start = time_step_i[0] + 2
                t_end = time_step_i[-1] + 2
                for k in range(len(y_hat_i)):
                    y_i = y_hat_i[k]
                    t_i = time_step_i[k] + 2
                    N_predictions_data['Producer'].append(producer_number)
                    N_predictions_data['Model'].append(model_namer(model))
                    N_predictions_data['Step size'].append(step_size)
                    N_predictions_data['t_start'].append(t_start)
                    N_predictions_data['t_end'].append(t_end)
                    N_predictions_data['t_i'].append(t_i)
                    N_predictions_data['Prediction'].append(y_i)

N_metrics_df = pd.DataFrame(N_metrics_data)
N_metrics_df.to_csv(N_predictions_metrics_file)
N_predictions_df = pd.DataFrame(N_predictions_data)
N_predictions_df.to_csv(N_predictions_file)

