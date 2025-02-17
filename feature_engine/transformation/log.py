# Authors: Soledad Galli <solegalli@protonmail.com>
# License: BSD 3 clause

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from feature_engine.base_transformers import BaseNumericalTransformer
from feature_engine.validation import _return_tags
from feature_engine.variable_manipulation import _check_input_parameter_variables


class LogTransformer(BaseNumericalTransformer):
    """
    The LogTransformer() applies the natural logarithm or the base 10 logarithm to
    numerical variables. The natural logarithm is the logarithm in base e.

    The LogTransformer() only works with positive values. If the variable
    contains a zero or a negative value the transformer will return an error.

    A list of variables can be passed as an argument. Alternatively, the transformer
    will automatically select and transform all variables of type numeric.

    More details in the :ref:`User Guide <log_transformer>`.

    Parameters
    ----------
    variables: list, default=None
        The list of numerical variables to transform. If None, the transformer
        will find and select all numerical variables.

    base: string, default='e'
        Indicates if the natural or base 10 logarithm should be applied. Can take
        values 'e' or '10'.

    Attributes
    ----------
    variables_:
        The group of variables that will be transformed.

    n_features_in_:
        The number of features in the train set used in fit.

    Methods
    -------
    fit:
        This transformer does not learn parameters.
    transform:
        Transform the variables using the logarithm.
    fit_transform:
        Fit to data, then transform it.
    inverse_transform:
        Convert the data back to the original representation.
    """

    def __init__(
        self,
        variables: Union[None, int, str, List[Union[str, int]]] = None,
        base: str = "e",
    ) -> None:

        if base not in ["e", "10"]:
            raise ValueError("base can take only '10' or 'e' as values")

        self.variables = _check_input_parameter_variables(variables)
        self.base = base

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        This transformer does not learn parameters.

        Selects the numerical variables and determines whether the logarithm
        can be applied on the selected variables, i.e., it checks that the variables
        are positive.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features].
            The training input samples. Can be the entire dataframe, not just the
            variables to transform.

        y: pandas Series, default=None
            It is not needed in this transformer. You can pass y or None.
        """

        # check input dataframe
        X = super().fit(X)

        # check contains zero or negative values
        if (X[self.variables_] <= 0).any().any():
            raise ValueError(
                "Some variables contain zero or negative values, can't apply log"
            )

        self.n_features_in_ = X.shape[1]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the variables with the logarithm.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features]
            The data to be transformed.

        Returns
        -------
        X_new: pandas dataframe
            The dataframe with the transformed variables.
        """

        # check input dataframe and if class was fitted
        X = super().transform(X)

        # check contains zero or negative values
        if (X[self.variables_] <= 0).any().any():
            raise ValueError(
                "Some variables contain zero or negative values, can't apply log"
            )

        # transform
        if self.base == "e":
            X.loc[:, self.variables_] = np.log(X.loc[:, self.variables_])
        elif self.base == "10":
            X.loc[:, self.variables_] = np.log10(X.loc[:, self.variables_])

        return X

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the data back to the original representation.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features]
            The data to be transformed.

        Returns
        -------
        X_tr: pandas dataframe
            The dataframe with the transformed variables.
        """

        # check input dataframe and if class was fitted
        X = super().transform(X)

        # inverse_transform
        if self.base == "e":
            X.loc[:, self.variables_] = np.exp(X.loc[:, self.variables_])
        elif self.base == "10":
            X.loc[:, self.variables_] = np.array(10 ** X.loc[:, self.variables_])

        return X

    def _more_tags(self):
        tags_dict = _return_tags()
        # =======  this tests fail because the transformers throw an error
        # when the values are 0. Nothing to do with the test itself but
        # mostly with the data created and used in the test
        msg = (
            "transformers raise errors when data contains zeroes, thus this check fails"
        )
        tags_dict["_xfail_checks"]["check_estimators_dtypes"] = msg
        tags_dict["_xfail_checks"]["check_estimators_fit_returns_self"] = msg
        tags_dict["_xfail_checks"]["check_pipeline_consistency"] = msg
        tags_dict["_xfail_checks"]["check_estimators_overwrite_params"] = msg
        tags_dict["_xfail_checks"]["check_estimators_pickle"] = msg
        tags_dict["_xfail_checks"]["check_transformer_general"] = msg

        return tags_dict


class LogCpTransformer(BaseNumericalTransformer):
    """
    The LogCpTransformer() applies the transformation log(x + C), where C is a positive
    constant, to the input variable. It applies the natural logarithm or the base 10
    logarithm, where the natural logarithm is logarithm in base e.

    The logarithm can only be applied to numerical non-negative values. If the
    variable contains a zero or a negative value after adding a constant C, the
    transformer will return an error.

    A list of variables can be passed as an argument. Alternatively, the transformer
    will automatically select and transform all variables of type numeric.

    More details in the :ref:`User Guide <log_cp>`.

    Parameters
    ----------
    variables: list, default=None
        The list of numerical variables to transform. If None, the transformer
        will find and select all numerical variables. If C is a dictionary, then this
        parameter is ignored and the variables to transform are selected from the
        dictionary keys.

    base: string, default='e'
        Indicates if the natural or base 10 logarithm should be applied. Can take
        values 'e' or '10'.

    C: "auto", int or dict, default="auto"
        The constant C to add to the variable before the logarithm, i.e., log(x + C).

        - If int, then log(x + C)
        - If "auto", then C = abs(min(x)) + 1
        - If dict, dictionary mapping the constant C to apply to each variable.

        Note, when C is a dictionary, the parameter `variables` is ignored.

    Attributes
    ----------
    variables_:
        The group of variables that will be transformed.

    C_:
        The constant C to add to each variable. If C = "auto" a dictionary with
        C = abs(min(variable)) + 1.

    n_features_in_:
        The number of features in the train set used in fit.

    Methods
    -------
    fit:
        Learn the constant C.
    transform:
        Transform the variables with the logarithm of x plus C.
    fit_transform:
        Fit to data, then transform it.
    inverse_transform:
        Convert the data back to the original representation.
    """

    def __init__(
        self,
        variables: Union[None, int, str, List[Union[str, int]]] = None,
        base: str = "e",
        C: Union[int, float, str, Dict[Union[str, int], Union[float, int]]] = "auto",
    ) -> None:

        if base not in ["e", "10"]:
            raise ValueError("base can take only '10' or 'e' as values")

        if not isinstance(C, (int, float, dict)) and not C == "auto":
            raise ValueError("C can take only 'auto', integers or floats")

        self.variables = _check_input_parameter_variables(variables)
        self.base = base
        self.C = C

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Learn the constant C to add to the variable before the logarithm transformation
        if C="auto".

        Select the numerical variables or check that the variables entered by the user
        are numerical. Then check that the selected variables are positive after
        addition of C.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features].
            The training input samples. Can be the entire dataframe, not just the
            variables to transform.

        y: pandas Series, default=None
            It is not needed in this transformer. You can pass y or None.
        """

        # check input dataframe
        if isinstance(self.C, dict):
            X = super()._select_variables_from_dict(X, self.C)
        else:
            X = super().fit(X)

        self.C_ = self.C

        # calculate C to add to each variable
        if self.C == "auto":
            self.C_ = dict(X[self.variables_].min(axis=0).abs() + 1)

        # check variables are positive after adding C
        if (X[self.variables_] + self.C_ <= 0).any().any():
            raise ValueError(
                "Some variables contain zero or negative values after adding"
                + "constant C, can't apply log"
            )

        self.n_features_in_ = X.shape[1]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the variables with the logarithm of x plus a constant C.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features]
            The data to be transformed.

        Returns
        -------
        X_new: pandas dataframe
            The dataframe with the transformed variables.
        """

        # check input dataframe and if class was fitted
        X = super().transform(X)

        # check variable is positive after adding c
        if (X[self.variables_] + self.C_ <= 0).any().any():
            raise ValueError(
                "Some variables contain zero or negative values after adding"
                + "constant C, can't apply log"
            )

        # transform
        if self.base == "e":
            X.loc[:, self.variables_] = np.log(X.loc[:, self.variables_] + self.C_)
        elif self.base == "10":
            X.loc[:, self.variables_] = np.log10(X.loc[:, self.variables_] + self.C_)

        return X

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the data back to the original representation.

        Parameters
        ----------
        X: Pandas DataFrame of shape = [n_samples, n_features]
            The data to be transformed.

        Returns
        -------
        X_tr: Pandas dataframe
            The dataframe with the transformed variables.
        """

        # check input dataframe and if class was fitted
        X = super().transform(X)

        # inverse transform
        if self.base == "e":
            X.loc[:, self.variables_] = np.exp(X.loc[:, self.variables_]) - self.C_
        elif self.base == "10":
            X.loc[:, self.variables_] = 10 ** X.loc[:, self.variables_] - self.C_

        return X
