from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class PlantInfo:
    korean_name: str
    scientific_name: Optional[str]
    max_height_cm: float
    max_width_cm: float
    evergreen: Optional[bool] = None
    flowering_months: Optional[list[int]] = None
    flower_color: Optional[str] = None
    fruit: Optional[bool] = None
    autumn_color: Optional[str] = None
    winter_interest: Optional[str] = None
    pruning_required: Optional[bool] = None
    seasonal_growth_features: Optional[Dict[str, str]] = None
    form_features: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
