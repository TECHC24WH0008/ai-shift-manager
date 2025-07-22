import pandas as pd

def is_leader(staff):
    return staff.role == "責任者"

def assign_shifts(staffs, config):
    DAYS = config["DAYS"]
    HOURS = config["HOURS"]
    BUSY_HOURS = config["BUSY_HOURS"]
    BUSY_NUM = config["BUSY_NUM"]
    NORMAL_NUM = config["NORMAL_NUM"]
    LEADER_NEEDED = config["LEADER_NEEDED"]

    # 各スタッフの割当状況を初期化
    for s in staffs:
        s.assigned_days = 0
        s.assigned_slots = []

    slots = []
    for day in DAYS:
        for hour in HOURS:
            busy = hour in BUSY_HOURS
            need_num = BUSY_NUM if busy else NORMAL_NUM
            slots.append({
                "day": day,
                "hour": hour,
                "busy": busy,
                "need_num": need_num,
                "assigned": []
            })

    # 1. ルール優先で割り当て（連続勤務ルール無効化）
    for slot in slots:
        day, hour = slot["day"], slot["hour"]
        candidates = [
            s for s in staffs
            if (day in s.preferred_days and
                hour in s.available_times and
                s.assigned_days < s.max_days)
            # 連続勤務ルールは完全に考慮しない
        ]
        # 優先：責任者
        leaders = [c for c in candidates if is_leader(c)]
        leaders.sort(key=lambda s: (-s.ability, s.assigned_days))
        leader_count = 0
        for leader in leaders:
            if leader_count < LEADER_NEEDED and leader.name not in slot["assigned"]:
                slot["assigned"].append(leader.name)
                leader.assigned_days += 1
                leader.assigned_slots.append((day, hour))
                leader_count += 1
        # 他スタッフ
        others = [c for c in candidates if c.name not in slot["assigned"]]
        others.sort(key=lambda s: (-s.ability, s.assigned_days))
        for other in others:
            if len(slot["assigned"]) < slot["need_num"]:
                slot["assigned"].append(other.name)
                other.assigned_days += 1
                other.assigned_slots.append((day, hour))

    # 2. 空き枠があればルール無視で埋める（連続勤務ルールなし）
    for slot in slots:
        # 責任者割当が足りない場合
        leader_needed = LEADER_NEEDED - sum(
            1 for n in slot["assigned"] if any(s.name == n and is_leader(s) for s in staffs)
        )
        if leader_needed > 0:
            for s in staffs:
                if is_leader(s) and s.name not in slot["assigned"]:
                    slot["assigned"].append(s.name)
                    s.assigned_days += 1
                    s.assigned_slots.append((slot["day"], slot["hour"]))
                    leader_needed -= 1
                    if leader_needed == 0:
                        break
        # 残り枠を全スタッフから順に埋める（連続勤務ルールなし）
        while len(slot["assigned"]) < slot["need_num"]:
            for s in staffs:
                if s.name not in slot["assigned"]:
                    slot["assigned"].append(s.name)
                    s.assigned_days += 1
                    s.assigned_slots.append((slot["day"], slot["hour"]))
                    break

    return slots

def save_shift_to_excel(slots, output_path):
    out_rows = []
    for slot in slots:
        out_rows.append({
            "日": slot["day"],
            "時間": slot["hour"],
            "忙しい": "○" if slot["busy"] else "",
            "必要人数": slot["need_num"],
            "割当スタッフ": ",".join(slot["assigned"])
        })
    out_df = pd.DataFrame(out_rows)
    with pd.ExcelWriter(output_path) as writer:
        out_df.to_excel(writer, index=False, sheet_name="Schedule")