from collections import defaultdict
from pathlib import Path

import pandas as pd
import tomllib

_LOC_PATH = Path(__file__).parent.joinpath(r"locations.toml")
_LOCATIONS = tomllib.loads(_LOC_PATH.read_text())
_DTYPE_MAP = defaultdict(
    lambda: object, int=pd.Int64Dtype(), float=pd.Float64Dtype(), str=pd.StringDtype()
)


class DataLoader:
    @classmethod
    def get_csv(cls, data_id, **kwargs) -> pd.DataFrame:
        try:
            data_info = _LOCATIONS["data"]["csv"][data_id]
            dir_path = Path(__file__).parent.joinpath(data_info["dir"])
            schema_path = dir_path.joinpath(data_info["schema"])
            data_path = dir_path.joinpath(data_info["file"])

            if "dtype" not in kwargs:
                schema = tomllib.loads(schema_path.read_text())
                for k, v in schema.items():
                    schema[k] = _DTYPE_MAP[v]
                kwargs["dtype"] = schema

            return pd.read_csv(data_path, **kwargs)

        except KeyError:
            raise ValueError(f"Unknown `data_id`, {data_id!s}.")


__all__ = ("DataLoader",)
