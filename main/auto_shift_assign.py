import pandas as pd

STAFF_FILE = "staff.xlsx"
SHEET = "Staff"
DAYS = [1,2,3,4,5,6,7]
HOURS = list(range(8,21))  # 8〜20時
BUSY_HOURS = set([11,12,13,17,18,19])
BUSY_NUM = 4
NORMAL_NUM = 3
LEADER_NEEDED = 1
MAX_CONSECUTIVE = 3

df = pd.read_excel(STAFF_FILE, sheet_name=SHEET)
staffs = []
for _, row in df.iterrows():
    staffs.append({
        "name": row["スタッフ名"],
        "ability": int(row["能力"]),
        "role": row["役職"],
        "max_days": int(row["勤務日数"]),
        "available_times": [int(x) for x in str(row["勤務可能時間"]).split(",")],
        "preferred_days": [int(x) for x in str(row["希望勤務日"]).split(",")],
        "assigned_days": 0,
        "assigned_slots": []
    })

slots = []
for d in DAYS:
    for h in HOURS:
        busy = h in BUSY_HOURS
        need_num = BUSY_NUM if busy else NORMAL_NUM
        slots.append({
            "day": d,
            "hour": h,
            "busy": busy,
            "need_num": need_num,
            "assigned": []
        })

def is_leader(name):
    return df[df["スタッフ名"]==name]["役職"].values[0]=="責任者"

# 1. ルール優先で割り当て
for slot in slots:
    day, hour = slot["day"], slot["hour"]
    candidates = []
    for s in staffs:
        # 希望日・時間・勤務日数制限
        if day in s["preferred_days"] and hour in s["available_times"] and s["assigned_days"] < s["max_days"]:
            # 連勤制限
            assigned_days = [d for d,h in s["assigned_slots"]]
            if assigned_days:
                assigned_days.append(day)
                assigned_days = sorted(set(assigned_days))
                streak, max_streak = 1, 1
                for i in range(1, len(assigned_days)):
                    if assigned_days[i] - assigned_days[i-1] == 1:
                        streak += 1
                        max_streak = max(max_streak, streak)
                    else:
                        streak = 1
                if max_streak > MAX_CONSECUTIVE:
                    continue
            candidates.append(s)
    # 優先：責任者
    leaders = [c for c in candidates if c["role"]=="責任者"]
    leaders.sort(key=lambda s: (-s["ability"], s["assigned_days"]))
    leader_count = 0
    for leader in leaders:
        if leader_count < LEADER_NEEDED and leader["name"] not in slot["assigned"]:
            slot["assigned"].append(leader["name"])
            leader["assigned_days"] += 1
            leader["assigned_slots"].append((day, hour))
            leader_count += 1
    # 他スタッフ
    others = [c for c in candidates if c["name"] not in slot["assigned"]]
    others.sort(key=lambda s: (-s["ability"], s["assigned_days"]))
    for other in others:
        if len(slot["assigned"]) < slot["need_num"]:
            slot["assigned"].append(other["name"])
            other["assigned_days"] += 1
            other["assigned_slots"].append((day, hour))

# 2. 空き枠があればルール無視で埋める
for slot in slots:
    # 責任者割当が足りない場合
    leaders_needed = LEADER_NEEDED - sum([1 for n in slot["assigned"] if is_leader(n)])
    if leaders_needed > 0:
        for s in staffs:
            if s["role"]=="責任者" and s["name"] not in slot["assigned"]:
                slot["assigned"].append(s["name"])
                s["assigned_days"] += 1
                s["assigned_slots"].append((slot["day"], slot["hour"]))
                leaders_needed -= 1
                if leaders_needed == 0:
                    break
    # 残り枠を全スタッフから順に埋める
    while len(slot["assigned"]) < slot["need_num"]:
        for s in staffs:
            if s["name"] not in slot["assigned"]:
                slot["assigned"].append(s["name"])
                s["assigned_days"] += 1
                s["assigned_slots"].append((slot["day"], slot["hour"]))
                break

# 結果出力
result = []
for slot in slots:
    result.append({
        "日": slot["day"],
        "時間": slot["hour"],
        "忙しい": "○" if slot["busy"] else "",
        "必要人数": slot["need_num"],
        "割当スタッフ": ",".join(slot["assigned"])
    })
df_out = pd.DataFrame(result)
df_out.to_excel("assigned_shift.xlsx", index=False, sheet_name="Schedule")

print("全枠埋めて割り当て完了：assigned_shift.xlsx に出力しました")
