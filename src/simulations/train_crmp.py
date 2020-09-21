import pickle
import dill as pickle

from sklearn.linear_model import (BayesianRidge, ElasticNetCV, LassoCV,
        LinearRegression)

from src.data.read_crmp import (injectors, net_productions, producers,
         producer_names)
from src.helpers.cross_validation import (forward_walk_splitter,
        train_model_with_cv)
from src.helpers.features import (net_production_dataset,
        production_rate_dataset)
from src.helpers.models import serialized_model_path, is_CV_model
from src.models.crmp import CRMP


# Production Rate Training
for i in range(len(producers)):
    models = [
        BayesianRidge(), CRMP(), ElasticNetCV, LassoCV, LinearRegression()
    ]
    X, y = production_rate_dataset(producers[i], *injectors)
    train_split, test_split, train_test_seperation_idx = forward_walk_splitter(X, y, 2)
    X_train = X[:train_test_seperation_idx]
    y_train = y[:train_test_seperation_idx]

    for model in models:
        if is_CV_model(model):
            model = train_model_with_cv(X, y, model, train_split)
        model = model.fit(X_train, y_train)
        pickled_model = serialized_model_path('crmp', model, producer_names[i])
        with open(pickled_model, 'wb') as f:
            pickle.dump(model, f)


# Net Production Training
for i in range(len(producers)):
    models = [
        BayesianRidge(), CRMP(), ElasticNetCV, LassoCV, LinearRegression()
    ]
    X, y = net_production_dataset(net_productions[i], producers[i], *injectors)
    train_split, test_split, train_test_seperation_idx = forward_walk_splitter(X, y, 2)
    X_train = X[:train_test_seperation_idx]
    y_train = y[:train_test_seperation_idx]

    for model in models:
        if is_CV_model(model):
            model = train_model_with_cv(X, y, model, train_split)
        model = model.fit(X_train, y_train)
        pickled_model = serialized_model_path(
            'net_crm', model, 'Net {}'.format(producer_names[i])
        )
        with open(pickled_model, 'wb') as f:
            pickle.dump(model, f)
