# Authors: Pradumna Suryawanshi <pradumnasuryawanshi@gmail.com>
# License: BSD 3 clause

from typing import List, Optional, Union

import pandas as pd

from feature_engine.dataframe_checks import _is_dataframe
from feature_engine.imputation.base_imputer import BaseImputer
from feature_engine.variable_manipulation import _check_input_parameter_variables


class DropMissingData(BaseImputer):
    """
    DropMissingData() will delete rows containing missing values. It provides
    similar functionality to pandas.drop_na().

    It works for numerical and categorical variables. You can enter the list of
    variables for which missing values should be evaluated. Alternatively, the imputer
    will evaluate missing data in all variables in the dataframe.

    More details in the :ref:`User Guide <drop_missing_data>`.

    Parameters
    ----------
    missing_only: bool, default=True
        If `True`, rows will be dropped when they show missing data in variables with
        missing data in the train set, that is, in the data set used in `fit()`. If
        `False`, rows will be dropped if there is missing data in any of the variables.
        This parameter only works when `threshold=None`, otherwise it is ignored.

    variables: list, default=None
        The list of variables to consider for the imputation. If None, the imputer will
        evaluate missing data in all variables in the dataframe. Alternatively, the
        imputer will evaluate missing data only in the variables in the list.

        Note that if `missing_only=True` only variables with missing data in the train
        set will be considered to drop a row, which might be a subset of the indicated
        list.

    threshold: int or float, default=None
        Require that percentage of non-NA values in a row to keep it. If
        `threshold=1`, all variables need to have data to keep the row. If
        `threshold=0.5`, 50% of the variables need to have data to keep the row.
        If `threshold=0.01`, 10% of the variables need to have data to keep the row.
        If `thresh=None`, rows with NA in any of the variables will be dropped.

    Attributes
    ----------
    variables_:
        The variables for which missing data will be examined to decide if a row is
        dropped. The attribute `variables_` is different from the parameter `variables`
        when the latter is `None`, or when only a subset of the indicated variables
        show NA in the train set if `missing_only=True`.

    n_features_in_:
        The number of features in the train set used in fit.

    Methods
    -------
    fit:
        Find the variables for which missing data should be evaluated.
    transform:
        Remove rows with missing data.
    fit_transform:
        Fit to the data, then transform it.
    return_na_data:
        Returns a dataframe with the rows that contain missing data.
    """

    def __init__(
        self,
        missing_only: bool = True,
        threshold: Union[None, int, float] = None,
        variables: Union[None, int, str, List[Union[str, int]]] = None,
    ) -> None:

        if not isinstance(missing_only, bool):
            raise ValueError(
                "missing_only takes values True or False. "
                f"Got {missing_only} instead."
            )

        if threshold is not None:
            if not isinstance(threshold, (int, float)) or not (0 < threshold <= 1):
                raise ValueError(
                    "threshold must be a value between 0 < x <= 1. "
                    f"Got {threshold} instead."
                )

        self.variables = _check_input_parameter_variables(variables)
        self.missing_only = missing_only
        self.threshold = threshold

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Find the variables for which missing data should be evaluated to decide if a
        row should be dropped.

        Parameters
        ----------
        X: pandas dataframe of shape = [n_samples, n_features]
            The training data set.

        y: pandas Series, default=None
            y is not needed in this imputation. You can pass None or y.
        """

        # check input dataframe
        X = _is_dataframe(X)

        # find variables for which indicator should be added

        # if threshold, then missing_only is ignored:
        if self.threshold is not None:
            if not self.variables:
                self.variables_ = [var for var in X.columns]
            else:
                self.variables_ = self.variables

        # if threshold is None, we have the option to identify
        # variables with NA only.
        else:
            if self.missing_only:
                if not self.variables:
                    self.variables_ = [
                        var for var in X.columns if X[var].isnull().sum() > 0
                    ]
                else:
                    self.variables_ = [
                        var for var in self.variables if X[var].isnull().sum() > 0
                    ]

            else:
                if not self.variables:
                    self.variables_ = [var for var in X.columns]
                else:
                    self.variables_ = self.variables

        self.n_features_in_ = X.shape[1]

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows with missing data.

        Parameters
        ----------
        X: pandas dataframe of shape = [n_samples, n_features]
            The dataframe to be transformed.

        Returns
        -------
        X_new: pandas dataframe
            The complete case dataframe for the selected variables, of shape
            [n_samples - n_samples_with_na, n_features]
        """

        X = self._check_transform_input_and_state(X)

        if self.threshold:
            X.dropna(
                thresh=len(self.variables_) * self.threshold,
                subset=self.variables_,
                axis=0,
                inplace=True,
            )
        else:
            X.dropna(axis=0, how="any", subset=self.variables_, inplace=True)

        return X

    def return_na_data(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Returns the subset of the dataframe with the rows with missing values. That is,
        the subset of the dataframe that would be removed with the `transform()` method.
        This method may be useful in production, for example if we want to store or log
        the removed observations, that is, rows that will not be fed into the model.

        Parameters
        ----------
        X_na: pandas dataframe of shape = [n_samples_with_na, features]
            The subset of the dataframe with the rows with missing data.
        """

        X = self._check_transform_input_and_state(X)

        if self.threshold:
            idx = pd.isnull(X[self.variables_]).mean(axis=1) >= self.threshold
            idx = idx[idx]
        else:
            idx = pd.isnull(X[self.variables_]).any(1)
            idx = idx[idx]

        return X.loc[idx.index, :]
