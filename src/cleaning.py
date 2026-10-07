import re

import pandas as pd


COLUMN_ALIASES = {
    "YearsCodingProf": "YearsCodePro",
    "FormalEducation": "EdLevel",
    "LanguageWorkedWith": "LanguageHaveWorkedWith",
    "ConvertedSalary": "ConvertedCompYearly",
}

REQUIRED_COLUMNS = [
    "YearsCodePro",
    "Country",
    "EdLevel",
    "LanguageHaveWorkedWith",
    "Employment",
    "ConvertedCompYearly",
]


def normalize_survey_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Map Stack Overflow 2018 column names to the project's standard names."""
    dataframe = dataframe.copy()
    rename_map = {
        source: target
        for source, target in COLUMN_ALIASES.items()
        if source in dataframe.columns and target not in dataframe.columns
    }
    return dataframe.rename(columns=rename_map)


def parse_years_experience(value: object) -> float:
    """Convert numeric or survey-range experience values to approximate years."""
    if pd.isna(value):
        return float("nan")

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.notna(numeric_value):
        return float(numeric_value)

    text = str(value).strip().lower()
    special_values = {
        "less than a year": 0.5,
        "less than 1 year": 0.5,
        "more than 50 years": 51.0,
        "20 or more years": 20.0,
    }
    if text in special_values:
        return special_values[text]

    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)", text)
    if range_match:
        lower_bound, upper_bound = map(float, range_match.groups())
        return (lower_bound + upper_bound) / 2

    open_range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:or more|\+)", text)
    if open_range_match:
        return float(open_range_match.group(1))

    less_than_match = re.search(r"less than\s*(\d+(?:\.\d+)?)", text)
    if less_than_match:
        return float(less_than_match.group(1)) / 2

    more_than_match = re.search(r"more than\s*(\d+(?:\.\d+)?)", text)
    if more_than_match:
        return float(more_than_match.group(1)) + 1

    return float("nan")


def clean_salary_data(
    dataframe: pd.DataFrame,
    min_salary: float = 5000,
    max_salary: float = 500000,
    full_time_only: bool = True,
) -> pd.DataFrame:
    """Standardize and filter survey rows for salary modeling."""
    if min_salary > max_salary:
        raise ValueError("min_salary must be less than or equal to max_salary")

    cleaned = normalize_survey_columns(dataframe)
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in cleaned.columns
    ]
    if missing_columns:
        raise ValueError(
            "Missing required survey columns: " + ", ".join(missing_columns)
        )

    cleaned["ConvertedCompYearly"] = pd.to_numeric(
        cleaned["ConvertedCompYearly"], errors="coerce"
    )
    cleaned["YearsCodePro"] = cleaned["YearsCodePro"].apply(
        parse_years_experience
    )
    cleaned["LanguageHaveWorkedWith"] = cleaned[
        "LanguageHaveWorkedWith"
    ].astype("string").str.strip()

    cleaned = cleaned.dropna(subset=REQUIRED_COLUMNS)
    cleaned = cleaned[
        cleaned["ConvertedCompYearly"].between(min_salary, max_salary)
    ]

    if full_time_only:
        employment = (
            cleaned["Employment"]
            .astype("string")
            .str.casefold()
            .str.replace(r"[^a-z]+", " ", regex=True)
            .str.strip()
        )
        cleaned = cleaned[employment.eq("employed full time")]

    cleaned = cleaned[cleaned["LanguageHaveWorkedWith"].ne("")]
    return cleaned.reset_index(drop=True)