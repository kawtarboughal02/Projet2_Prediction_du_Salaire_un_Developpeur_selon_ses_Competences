from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "survey_results_public.csv"
PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "donnees_salaires_developpeurs.csv"
)


def load_raw_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the original Stack Overflow survey CSV."""
    return pd.read_csv(path)


def load_processed_data(path: str | Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load the cleaned developer salary dataset."""
    return pd.read_csv(path)