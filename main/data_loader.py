import pandas as pd
from models import Staff

def load_staffs_from_excel(file_path: str) -> list:
    df = pd.read_excel(file_path, sheet_name="Staff")
    staffs = []
    for _, row in df.iterrows():
        staffs.append(
            Staff(
                name=row["スタッフ名"],
                ability=row["能力"],
                role=row["役職"],
                max_days=row["勤務日数"],
                available_times=[int(t) for t in str(row["勤務可能時間"]).split(",")],
                preferred_days=[int(d) for d in str(row["希望勤務日"]).split(",")]
            )
        )
    return staffs

def save_shift_to_excel(shift_table, file_path: str):
    # シフト表の書き出し例（簡易的）
    records = []
    for slot in shift_table.slots:
        records.append({
            "日": slot.date,
            "時間": slot.hour,
            "忙しい": slot.busy,
            "必要人数": slot.required_num,
            "責任者必要": slot.required_leader,
            "割当スタッフ": ",".join(slot.assigned_staff)
        })
    pd.DataFrame(records).to_excel(file_path, index=False, sheet_name="Schedule")