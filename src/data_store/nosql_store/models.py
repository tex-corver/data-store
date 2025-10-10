from typing import Any

import pydantic


class DataFrame(pydantic.BaseModel):
    # Placeholder for DataFrame class
    data: Any  # Expected: 'pandas.DataFrame' or 'polars.DataFrame'
    data_type: str  # 'pandas' or 'polars'
