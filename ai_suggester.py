def suggest_replacement(staffs, shift_slot, used_staffs, absent_name=None):
    candidates = []
    for s in staffs:
        if s.name in used_staffs or s.name == absent_name:
            continue

        score = 0
        reasons = []

        # 希望勤務日
        if shift_slot["day"] in s.preferred_days:
            score += 5
            reasons.append("希望日")
        else:
            reasons.append("希望日外")

        # 勤務可能時間
        if shift_slot["hour"] in s.available_times:
            score += 5
            reasons.append("時間OK")
        else:
            reasons.append("時間外")

        # 勤務日数制限
        if s.assigned_days < s.max_days:
            score += 3
            reasons.append("勤務可能")
        else:
            reasons.append("勤務日数超")

        # 責任者優先
        if hasattr(s, "role") and s.role == "責任者":
            score += 2
            reasons.append("責任者")
        else:
            reasons.append("一般")

        # 能力値（ルールではないが参考に加点）
        score += s.ability

        candidates.append({
            "name": s.name,
            "score": score,
            "reason": "・".join(reasons)
        })

    # スコア順で最大3名返す（候補が2名未満なら全員返す）
    candidates.sort(key=lambda x: -x["score"])
    return candidates[:max(2, min(3, len(candidates)))]