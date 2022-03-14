import pytest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.utils.estimator_checks import check_estimator

from feature_engine.estimator_checks import (
    check_all_types_variables_assignment,
    check_feature_names_in,
    check_numerical_variables_assignment,
    check_raises_error_when_input_not_a_df,
    check_raises_non_fitted_error,
)
from feature_engine.wrappers import SklearnTransformerWrapper


def test_sklearn_transformer_wrapper():
    check_estimator(SklearnTransformerWrapper(transformer=SimpleImputer()))


@pytest.mark.parametrize(
    "estimator", [SklearnTransformerWrapper(transformer=OrdinalEncoder())]
)
def test_check_estimator_from_feature_engine(estimator):
    check_raises_non_fitted_error(estimator)
    check_raises_error_when_input_not_a_df(estimator)
    check_feature_names_in(estimator)


def test_check_variables_assignment():
    check_numerical_variables_assignment(
        SklearnTransformerWrapper(transformer=StandardScaler())
    )
    check_all_types_variables_assignment(
        SklearnTransformerWrapper(transformer=OrdinalEncoder())
    )


def test_raises_error_when_no_transformer_passed():
    # this selectors need an estimator as an input param
    # test error otherwise.
    with pytest.raises(TypeError):
        SklearnTransformerWrapper()
