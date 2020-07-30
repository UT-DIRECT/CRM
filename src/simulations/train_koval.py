import pickle
import dill as pickle

from sklearn.model_selection import train_test_split

from src.data.read_wfsim import f_w, W_t
from src.helpers.features import production_rate_dataset
from src.helpers.models import serialized_model_path
from src.models.koval import Koval

X = W_t[:-1]
y = f_w[1:]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=1, shuffle=False
)
koval = Koval().fit(X=X_train, y=y_train)

pickled_model = serialized_model_path('koval', koval)
with open(pickled_model, 'wb') as f:
    pickle.dump(koval, f)
