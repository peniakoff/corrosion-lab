"""CSV loading, validation, and template handling."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from corrosionlab.constants import TIME_COLUMN
from corrosionlab.i18n import LocalizedError

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATA_PATH = DATA_DIR / "oxidation_data.csv"
TEMPLATE_PATH = DATA_DIR / "template.csv"


class DataValidationError(LocalizedError):
    """Raised when uploaded CSV does not match the expected schema."""


def load_csv(source: Path | str | bytes) -> pd.DataFrame:
    """Load oxidation data from a file path or uploaded bytes."""
    if isinstance(source, bytes):
        from io import BytesIO

        df = pd.read_csv(BytesIO(source))
    else:
        df = pd.read_csv(source)
    return validate_dataframe(df)


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the oxidation data schema."""
    if df.empty:
        raise DataValidationError("csv_empty")

    if TIME_COLUMN not in df.columns:
        raise DataValidationError(
            "missing_time_column",
            column=TIME_COLUMN,
            columns=", ".join(df.columns),
        )

    numeric_cols = [TIME_COLUMN, *get_sample_columns(df)]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[TIME_COLUMN].isna().any():
        raise DataValidationError("invalid_time_values", column=TIME_COLUMN)

    if (df[TIME_COLUMN] < 0).any():
        raise DataValidationError("negative_time")

    df = df.sort_values(TIME_COLUMN).reset_index(drop=True)
    return df


def get_sample_columns(
    df: pd.DataFrame,
    *,
    exclude: tuple[str, ...] = (TIME_COLUMN,),
) -> list[str]:
    """Return mass columns excluding time and optional exclusions."""
    return [col for col in df.columns if col not in exclude]


def load_default_data() -> pd.DataFrame:
    """Load bundled thesis dataset (Table 9.1)."""
    return load_csv(DEFAULT_DATA_PATH)


def load_template_bytes() -> bytes:
    """Return template CSV bytes for download."""
    return TEMPLATE_PATH.read_bytes()
