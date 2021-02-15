# import numpy as np
# import pytest
# from sklearn.utils.validation import check_is_fitted, NotFittedError
#
# from src.helpers.features import net_production_dataset
# from src.models.icrmp import ICRMP
#
#
# # Initializing variables outside of the class since pytest ignores classes
# # with a constructor.
# N = np.array([2, 5, 9, 14, 20])
# q = np.array([2, 3, 4, 5, 6])
# inj1 = 2 * q
# inj2 = 3 * q
# inj3 = 0.5 * q
#
# class TestICRMP():
#
#
#     def test_fit_two_injectors(self):
#         X, y = net_production_dataset(N, q, inj1, inj2)
#         icrmp = ICRMP().fit(X, y)
#         assert(icrmp.tau_ is not None)
#         assert(icrmp.tau_ > 1 and icrmp.tau_ < 30)
#         assert(icrmp.gains_ is not None)
#         assert(len(icrmp.gains_) == 2)
#         f1 = icrmp.gains_[0]
#         f2 = icrmp.gains_[1]
#         assert(0 <= f1 <= 1)
#         assert(0 <= f2 <= 1)
#         sum_of_gains = f1 + f2
#         assert(abs(1 - sum_of_gains) <= 1.e-5)
#
#
#     def test_fit_three_injectors(self):
#         X, y = net_production_dataset(N, q, inj1, inj2, inj3)
#         icrmp = ICRMP().fit(X, y)
#         assert(icrmp.tau_ is not None)
#         assert(icrmp.tau_ > 1 and icrmp.tau_ < 30)
#         assert(icrmp.gains_ is not None)
#         assert(len(icrmp.gains_) == 3)
#         f1 = icrmp.gains_[0]
#         f2 = icrmp.gains_[1]
#         f3 = icrmp.gains_[2]
#         assert(0 <= f1 <= 1)
#         assert(0 <= f2 <= 1)
#         assert(0 <= f3 <= 1)
#         sum_of_gains = f1 + f2 + f3
#         assert(abs(1 - sum_of_gains) <= 1.e-5)
#
#
#     def test_fit_X_y_different_shape(self):
#         X, y = net_production_dataset(N, q, inj1, inj2, inj3)
#         X = X[:-2]
#         with pytest.raises(ValueError):
#             icrmp = ICRMP().fit(X, y)
#
#
#     def test_predict_unfitted_icrmp_raises_error(self):
#         X, y = net_production_dataset(N, q, inj1, inj2, inj3)
#         icrmp = ICRMP()
#         with pytest.raises(NotFittedError):
#             icrmp.predict(X)
#
#
#     def test_predict_two_injectors(self):
#         X, y = net_production_dataset(N, q, inj1, inj2)
#         icrmp = ICRMP().fit(X, y)
#         # There is no helper to construct the prediction matrix
#         # since the prediction matrix is constructed by the cross validator
#         X = np.array([N[1:], q[1:], inj1[1:], inj2[1:]]).T
#         y_hat = icrmp.predict(X)
#         assert(y_hat is not None)
#         assert(len(y_hat) == 4)
#
#
#     def test_predict_three_injectors(self):
#         X, y = net_production_dataset(N, q, inj1, inj2, inj3)
#         icrmp = ICRMP().fit(X, y)
#         # There is no helper to construct the prediction matrix
#         # since the prediction matrix is constructed by the cross validator
#         X = np.array([N[1:], q[1:], inj1[1:], inj2[1:], inj3[1:]]).T
#         y_hat = icrmp.predict(X)
#         assert(y_hat is not None)
#         assert(len(y_hat) == 4)
