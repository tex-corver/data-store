from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

DataFrameType = Literal["pandas", "polars"]


@dataclass
class DataFrame:
    """_summary_"""

    data: "pl.DataFrame" | "pl.DataFrame"  # type: ignore  # noqa: F821
    data_type: DataFrameType
