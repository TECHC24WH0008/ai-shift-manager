from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Staff:
    name: str
    ability: int         # 能力（数値でスコア化）
    role: str            # 役職
    max_days: int        # 勤務日数上限
    available_times: List[int]  # 勤務可能な時間（例: [9,10,11,...]）
    preferred_days: List[int]   # 希望勤務日（例: [1,2,3,4,5,6,7]）

@dataclass
class ShiftSlot:
    date: int            # 曜日（1-7）
    hour: int            # 時間帯（0-23）
    busy: bool           # 忙しい時間帯か
    required_num: int    # 必要人数
    required_leader: bool
    assigned_staff: List[str] = field(default_factory=list)

@dataclass
class ShiftTable:
    slots: List[ShiftSlot]