import numpy as np
import pytest
from sklearn.utils.validation import check_is_fitted, NotFittedError

from src.helpers.features import production_rate_dataset
from src.models.injection_rate_crm import InjectionRateCRM


# Initializing variables outside of the class since pytest ignores classes
# with a constructor.
q = np.array([2, 3, 4, 5, 6])
inj1 = 2 * q
inj2 = 3 * q
inj3 = 0.5 * q

class TestInjectionRateCRM():


    def test_fit_two_injectors(self):
        X, y = production_rate_dataset(q, inj1, inj2)
        ircrm = InjectionRateCRM().fit(X, y)
        assert(ircrm.tau_ is not None)
        assert(ircrm.tau_ > 1 and ircrm.tau_ < 30)
        assert(ircrm.gains_ is not None)
        assert(len(ircrm.gains_) == 2)
        f1 = ircrm.gains_[0]
        f2 = ircrm.gains_[1]
        assert(0 <= f1 <= 1)
        assert(0 <= f2 <= 1)
        sum_of_gains = f1 + f2
        assert(abs(1 - sum_of_gains) <= 1.e-5)


    def test_fit_three_injectors(self):
        X, y = production_rate_dataset(q, inj1, inj2, inj3)
        ircrm = InjectionRateCRM().fit(X, y)
        assert(ircrm.tau_ is not None)
        assert(ircrm.tau_ > 1 and ircrm.tau_ < 30)
        assert(ircrm.gains_ is not None)
        assert(len(ircrm.gains_) == 3)
        f1 = ircrm.gains_[0]
        f2 = ircrm.gains_[1]
        f3 = ircrm.gains_[2]
        assert(0 <= f1 <= 1)
        assert(0 <= f2 <= 1)
        assert(0 <= f3 <= 1)
        sum_of_gains = f1 + f2 + f3
        assert(abs(1 - sum_of_gains) <= 1.e-5)


    def test_fit_X_y_different_shape(self):
        X, y = production_rate_dataset(q, inj1, inj2, inj3)
        X = X[:-2]
        with pytest.raises(ValueError):
            ircrm = InjectionRateCRM().fit(X, y)


    def test_predict_with_unfitted_estimator_raises_error(self):
        X, y = production_rate_dataset(q, inj1, inj2, inj3)
        ircrm = InjectionRateCRM()
        with pytest.raises(NotFittedError):
            ircrm.predict(X)


    def test_predict_two_injectors(self):
        X, y = production_rate_dataset(q, inj1, inj2)
        ircrm = InjectionRateCRM().fit(X, y)
        # There is no helper to construct the prediction matrix
        # since the prediction matrix is constructed by the cross validator
        X = np.array([q[1:], inj1[1:], inj2[1:]]).T
        y_hat, injection_rates = ircrm.predict(X)
        assert(y_hat is not None)
        assert(len(y_hat) == 4)
        assert(injection_rates is not None)
        assert(len(injection_rates) == 8)


    def test_predict_three_injectors(self):
        X, y = production_rate_dataset(q, inj1, inj2, inj3)
        ircrm = InjectionRateCRM().fit(X, y)
        # There is no helper to construct the prediction matrix
        # since the prediction matrix is constructed by the cross validator
        X = np.array([q[1:], inj1[1:], inj2[1:], inj3[1:]]).T
        y_hat = ircrm.predict(X)
        y_hat, injection_rates = ircrm.predict(X)
        assert(y_hat is not None)
        assert(len(y_hat) == 4)
        assert(injection_rates is not None)
        assert(len(injection_rates) == 12)
