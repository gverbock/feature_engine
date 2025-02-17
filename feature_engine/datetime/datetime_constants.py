import numpy as np

FEATURES_SUPPORTED = [
    "month",
    "quarter",
    "semester",
    "year",
    "week",
    "day_of_week",
    "day_of_month",
    "day_of_year",
    "weekend",
    "month_start",
    "month_end",
    "quarter_start",
    "quarter_end",
    "year_start",
    "year_end",
    "leap_year",
    "days_in_month",
    "hour",
    "minute",
    "second",
]

FEATURES_SUFFIXES = {
    "month": "_month",
    "quarter": "_quarter",
    "semester": "_semester",
    "year": "_year",
    "week": "_week",
    "day_of_week": "_day_of_week",
    "day_of_month": "_day_of_month",
    "day_of_year": "_day_of_year",
    "weekend": "_weekend",
    "month_start": "_month_start",
    "month_end": "_month_end",
    "quarter_start": "_quarter_start",
    "quarter_end": "_quarter_end",
    "year_start": "_year_start",
    "year_end": "_year_end",
    "leap_year": "_leap_year",
    "days_in_month": "_days_in_month",
    "hour": "_hour",
    "minute": "_minute",
    "second": "_second",
}

FEATURES_FUNCTIONS = {
    "month": lambda x: x.dt.month,
    "quarter": lambda x: x.dt.quarter,
    "semester": lambda x: np.where(x.dt.month <= 6, 1, 2).astype(np.int64),
    "year": lambda x: x.dt.year,
    "week": lambda x: x.dt.isocalendar().week.astype(np.int64),
    "day_of_week": lambda x: x.dt.dayofweek,
    "day_of_month": lambda x: x.dt.day,
    "day_of_year": lambda x: x.dt.dayofyear,
    "weekend": lambda x: np.where(x.dt.dayofweek <= 4, 0, 1).astype(np.int64),
    "month_start": lambda x: x.dt.is_month_start.astype(np.int64),
    "month_end": lambda x: x.dt.is_month_end.astype(np.int64),
    "quarter_start": lambda x: x.dt.is_quarter_start.astype(np.int64),
    "quarter_end": lambda x: x.dt.is_quarter_end.astype(np.int64),
    "year_start": lambda x: x.dt.is_year_start.astype(np.int64),
    "year_end": lambda x: x.dt.is_year_end.astype(np.int64),
    "leap_year": lambda x: x.dt.is_leap_year.astype(np.int64),
    "days_in_month": lambda x: x.dt.days_in_month.astype(np.int64),
    "hour": lambda x: x.dt.hour,
    "minute": lambda x: x.dt.minute,
    "second": lambda x: x.dt.second,
}

FEATURES_DEFAULT = [
    "month",
    "year",
    "day_of_week",
    "day_of_month",
    "hour",
    "minute",
    "second",
]
