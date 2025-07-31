# -*- coding: utf-8 -*-
"""
シフト管理サービス
シフト作成・最適化・分析のビジネスロジック
"""

import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Tuple, Optional
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import app_config
from core.templates import ShiftTemplates
from utils.validators import BusinessRuleValidator
from utils.date_utils import DateUtils, TimeSlotManager

class ShiftService:
    """シフト管理サービス"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.time_slot_manager = TimeSlotManager()
        self.validator = BusinessRuleValidator()
        
    def create_optimal_shift(self, date_range: Tuple[str, str], 
                           requirements: Dict[str, Any]) -> Dict[str, Any]:
        """最適なシフトを作成"""
        start_date, end_date = date_range
        dates = DateUtils.get_date_range(start_date, end_date)
        
        shift_plan = {
            "period": {"start": start_date, "end": end_date},
            "shifts": {},
            "summary": {},
            "issues": [],
            "optimization_score": 0
        }
        
        # 各日のシフトを作成
        for date_str in dates:
            daily_shift = self._create_daily_shift(date_str, requirements)
            shift_plan["shifts"][date_str] = daily_shift
            
            # 問題点をチェック
            issues = self._validate_daily_shift(daily_shift, date_str)
            shift_plan["issues"].extend(issues)
        
        # 全体の最適化
        shift_plan = self._optimize_shift_plan(shift_plan, requirements)
        
        # サマリー作成
        shift_plan["summary"] = self._create_shift_summary(shift_plan)
        
        return shift_plan
    
    def _create_daily_shift(self, date_str: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """1日のシフトを作成"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = DateUtils.get_japanese_weekday(date_obj)
        is_weekend = weekday in ['土', '日']
        
        # 必要人数を決定
        required_staff = requirements.get('min_staff', {})
        min_staff_count = required_staff.get('土日' if is_weekend else '平日', 2)
        
        # 時間帯別要件
        time_slots = requirements.get('time_slots', [])
        
        daily_shift = {
            "date": date_str,
            "weekday": weekday,
            "is_weekend": is_weekend,
            "time_slots": {},
            "total_staff": 0,
            "coverage_rate": 0,
            "issues": []
        }
        
        # 各時間帯のシフトを作成
        for slot in time_slots:
            slot_shift = self._assign_staff_to_slot(date_str, slot, min_staff_count)
            daily_shift["time_slots"][slot["name"]] = slot_shift
            daily_shift["total_staff"] += len(slot_shift.get("assigned_staff", []))
        
        # カバー率計算
        required_total = len(time_slots) * min_staff_count
        actual_total = daily_shift["total_staff"]
        daily_shift["coverage_rate"] = (actual_total / required_total * 100) if required_total > 0 else 100
        
        return daily_shift
    
    def _assign_staff_to_slot(self, date_str: str, time_slot: Dict, min_count: int) -> Dict[str, Any]:
        """時間帯にスタッフを割り当て"""
        slot_info = {
            "time_slot": time_slot["name"],
            "start_time": time_slot["start"],
            "end_time": time_slot["end"],
            "required_count": min_count,
            "assigned_staff": [],
            "coverage_rate": 0
        }
        
        if not self.data_manager or self.data_manager.staff_data is None:
            # サンプルデータで代用
            sample_staff = self._get_sample_staff_for_slot(time_slot, min_count)
            slot_info["assigned_staff"] = sample_staff
            slot_info["coverage_rate"] = (len(sample_staff) / min_count * 100) if min_count > 0 else 100
            return slot_info
        
        # 実際のスタッフデータから割り当て
        available_staff = self._get_available_staff(date_str, time_slot)
        
        # 優先度に基づいてソート
        sorted_staff = sorted(available_staff, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # 必要人数まで割り当て
        assigned = sorted_staff[:min_count]
        slot_info["assigned_staff"] = assigned
        slot_info["coverage_rate"] = (len(assigned) / min_count * 100) if min_count > 0 else 100
        
        return slot_info
    
    def _get_sample_staff_for_slot(self, time_slot: Dict, count: int) -> List[Dict]:
        """サンプルスタッフデータを生成"""
        sample_names = ["田中太郎", "佐藤花子", "鈴木次郎", "山田美咲", "高橋健太", "渡辺由美"]
        sample_roles = ["スタッフ", "リーダー", "責任者"]
        
        staff_list = []
        for i in range(min(count, len(sample_names))):
            staff_list.append({
                "employee_id": f"EMP{i+1:03d}",
                "name": sample_names[i],
                "role": sample_roles[i % len(sample_roles)],
                "skill_level": 3 + (i % 3),
                "priority_score": 80 - (i * 5)
            })
        
        return staff_list
    
    def _get_available_staff(self, date_str: str, time_slot: Dict) -> List[Dict]:
        """指定日時に利用可能なスタッフを取得"""
        if not self.data_manager or self.data_manager.staff_data is None:
            return []
        
        available_staff = []
        
        for _, staff_row in self.data_manager.staff_data.iterrows():
            # 基本的な利用可能性チェック
            if self._is_staff_available(staff_row, date_str, time_slot):
                staff_info = {
                    "employee_id": staff_row.get("従業員ID"),
                    "name": staff_row.get("氏名"),
                    "department": staff_row.get("部門"),
                    "role": staff_row.get("役職", "スタッフ"),
                    "skill_level": staff_row.get("スキルレベル", 3),
                    "hourly_wage": staff_row.get("時給", 1000),
                    "priority_score": self._calculate_priority_score(staff_row, date_str, time_slot)
                }
                available_staff.append(staff_info)
        
        return available_staff
    
    def _is_staff_available(self, staff_row: pd.Series, date_str: str, time_slot: Dict) -> bool:
        """スタッフの利用可能性をチェック"""
        # 基本的なチェック（実際の実装では更に詳細な条件を追加）
        
        # 雇用形態チェック
        employment_type = staff_row.get("雇用形態", "")
        if employment_type == "休職中":
            return False
        
        # 希望勤務時間チェック（簡易版）
        preferred_hours = staff_row.get("希望勤務時間", "")
        if preferred_hours == "午前のみ" and time_slot.get("start", "") > "12:00":
            return False
        if preferred_hours == "夕方以降" and time_slot.get("end", "") < "17:00":
            return False
        
        return True
    
    def _calculate_priority_score(self, staff_row: pd.Series, date_str: str, time_slot: Dict) -> float:
        """スタッフの優先度スコアを計算"""
        score = 50.0  # ベーススコア
        
        # スキルレベル
        skill_level = staff_row.get("スキルレベル", 3)
        score += skill_level * 10
        
        # 勤続期間
        if "勤続月数" in staff_row:
            tenure_months = staff_row.get("勤続月数", 0)
            score += min(tenure_months * 0.5, 20)  # 最大20点
        
        # 雇用形態
        employment_type = staff_row.get("雇用形態", "")
        if employment_type == "正社員":
            score += 15
        elif employment_type == "パート":
            score += 10
        
        # 役職
        role = staff_row.get("役職", "")
        if "リーダー" in role or "責任者" in role:
            score += 20
        elif "主任" in role:
            score += 10
        
        return score
    
    def _validate_daily_shift(self, daily_shift: Dict, date_str: str) -> List[str]:
        """日次シフトの妥当性を検証"""
        issues = []
        
        # カバー率チェック
        if daily_shift["coverage_rate"] < 80:
            issues.append(f"{date_str}: 人員不足（カバー率{daily_shift['coverage_rate']:.1f}%）")
        
        # 各時間帯のチェック
        for slot_name, slot_info in daily_shift["time_slots"].items():
            if slot_info["coverage_rate"] < 100:
                issues.append(f"{date_str} {slot_name}: 必要人数不足")
        
        return issues
    
    def _optimize_shift_plan(self, shift_plan: Dict, requirements: Dict) -> Dict[str, Any]:
        """シフト計画を最適化"""
        # 連続勤務のチェックと調整
        self._optimize_consecutive_work_days(shift_plan)
        
        # 労働時間の均等化
        self._balance_work_hours(shift_plan)
        
        # 最適化スコアの計算
        shift_plan["optimization_score"] = self._calculate_optimization_score(shift_plan)
        
        return shift_plan
    
    def _optimize_consecutive_work_days(self, shift_plan: Dict):
        """連続勤務日数を最適化"""
        # 従業員別の勤務日を集計
        employee_schedules = {}
        
        for date_str, daily_shift in shift_plan["shifts"].items():
            for slot_name, slot_info in daily_shift["time_slots"].items():
                for staff in slot_info["assigned_staff"]:
                    emp_id = staff["employee_id"]
                    if emp_id not in employee_schedules:
                        employee_schedules[emp_id] = []
                    employee_schedules[emp_id].append({
                        "date": date_str,
                        "slot": slot_name,
                        "staff_info": staff
                    })
        
        # 連続勤務をチェックして調整
        for emp_id, schedule in employee_schedules.items():
            sorted_schedule = sorted(schedule, key=lambda x: x["date"])
            
            # 連続勤務日数をチェック
            consecutive_days = 1
            for i in range(1, len(sorted_schedule)):
                prev_date = datetime.strptime(sorted_schedule[i-1]["date"], '%Y-%m-%d')
                curr_date = datetime.strptime(sorted_schedule[i]["date"], '%Y-%m-%d')
                
                if (curr_date - prev_date).days == 1:
                    consecutive_days += 1
                    if consecutive_days > 6:  # 法定上限
                        # 調整が必要
                        shift_plan["issues"].append(f"従業員{emp_id}: 連続勤務{consecutive_days}日")
                else:
                    consecutive_days = 1
    
    def _balance_work_hours(self, shift_plan: Dict):
        """労働時間を均等化"""
        # 従業員別の労働時間を集計
        employee_hours = {}
        
        for date_str, daily_shift in shift_plan["shifts"].items():
            for slot_name, slot_info in daily_shift["time_slots"].items():
                # 時間帯の労働時間を計算
                start_time = slot_info["start_time"]
                end_time = slot_info["end_time"]
                
                try:
                    start_minutes = DateUtils.parse_time_to_minutes(start_time)
                    end_minutes = DateUtils.parse_time_to_minutes(end_time)
                    if end_minutes < start_minutes:  # 日をまたぐ場合
                        end_minutes += 24 * 60
                    work_minutes = end_minutes - start_minutes
                except:
                    work_minutes = 480  # デフォルト8時間
                
                for staff in slot_info["assigned_staff"]:
                    emp_id = staff["employee_id"]
                    if emp_id not in employee_hours:
                        employee_hours[emp_id] = 0
                    employee_hours[emp_id] += work_minutes
        
        # 労働時間の偏りをチェック
        if employee_hours:
            avg_hours = sum(employee_hours.values()) / len(employee_hours)
            for emp_id, hours in employee_hours.items():
                if hours > avg_hours * 1.5:  # 平均の1.5倍以上
                    shift_plan["issues"].append(f"従業員{emp_id}: 労働時間過多（{hours/60:.1f}時間）")
                elif hours < avg_hours * 0.5:  # 平均の0.5倍以下
                    shift_plan["issues"].append(f"従業員{emp_id}: 労働時間不足（{hours/60:.1f}時間）")
    
    def _calculate_optimization_score(self, shift_plan: Dict) -> float:
        """最適化スコアを計算"""
        score = 100.0
        
        # 問題点による減点
        issue_count = len(shift_plan["issues"])
        score -= issue_count * 5  # 1問題につき5点減点
        
        # カバー率による評価
        total_coverage = 0
        shift_count = 0
        
        for daily_shift in shift_plan["shifts"].values():
            total_coverage += daily_shift["coverage_rate"]
            shift_count += 1
        
        if shift_count > 0:
            avg_coverage = total_coverage / shift_count
            if avg_coverage < 90:
                score -= (90 - avg_coverage) * 0.5
        
        return max(score, 0)
    
    def _create_shift_summary(self, shift_plan: Dict) -> Dict[str, Any]:
        """シフトサマリーを作成"""
        total_shifts = len(shift_plan["shifts"])
        total_issues = len(shift_plan["issues"])
        
        # 全体統計
        total_staff_assignments = 0
        total_coverage = 0
        
        for daily_shift in shift_plan["shifts"].values():
            total_staff_assignments += daily_shift["total_staff"]
            total_coverage += daily_shift["coverage_rate"]
        
        avg_coverage = total_coverage / total_shifts if total_shifts > 0 else 0
        
        summary = {
            "period_days": total_shifts,
            "total_staff_assignments": total_staff_assignments,
            "average_coverage_rate": round(avg_coverage, 1),
            "total_issues": total_issues,
            "optimization_score": shift_plan["optimization_score"],
            "status": self._determine_shift_status(avg_coverage, total_issues),
            "recommendations": self._generate_recommendations(shift_plan)
        }
        
        return summary
    
    def _determine_shift_status(self, avg_coverage: float, issue_count: int) -> str:
        """シフトの状態を判定"""
        if avg_coverage >= 95 and issue_count == 0:
            return "excellent"
        elif avg_coverage >= 90 and issue_count <= 2:
            return "good"
        elif avg_coverage >= 80 and issue_count <= 5:
            return "warning"
        else:
            return "critical"
    
    def _generate_recommendations(self, shift_plan: Dict) -> List[str]:
        """改善提案を生成"""
        recommendations = []
        
        # 問題に基づく提案
        issues = shift_plan["issues"]
        
        if any("人員不足" in issue for issue in issues):
            recommendations.append("追加スタッフの採用を検討してください")
        
        if any("連続勤務" in issue for issue in issues):
            recommendations.append("連続勤務を避けるシフト調整を行ってください")
        
        if any("労働時間過多" in issue for issue in issues):
            recommendations.append("労働時間の均等化を図ってください")
        
        if shift_plan["optimization_score"] < 70:
            recommendations.append("シフト配置の全面的な見直しを推奨します")
        
        if not recommendations:
            recommendations.append("現在のシフトは良好な状態です")
        
        return recommendations

    def find_substitute_candidates(self, absent_employee: Dict, shift_info: Dict) -> List[Dict]:
        """代替候補を検索"""
        if not self.data_manager or self.data_manager.staff_data is None:
            return self._get_sample_substitute_candidates(absent_employee, shift_info)
        
        candidates = []
        
        for _, staff_row in self.data_manager.staff_data.iterrows():
            if staff_row.get("従業員ID") == absent_employee.get("employee_id"):
                continue  # 欠勤者は除外
            
            # 利用可能性チェック
            if self._is_staff_available(staff_row, shift_info.get("date"), shift_info):
                candidate = {
                    "employee_id": staff_row.get("従業員ID"),
                    "name": staff_row.get("氏名"),
                    "department": staff_row.get("部門"),
                    "role": staff_row.get("役職", "スタッフ"),
                    "skill_level": staff_row.get("スキルレベル", 3),
                    "experience": self._get_experience_level(staff_row),
                    "availability": "○",
                    "score": self._calculate_substitute_score(staff_row, absent_employee, shift_info),
                    "workload": self._calculate_current_workload(staff_row),
                    "past_substitutions": 0  # 実装時に実際のデータから取得
                }
                candidates.append(candidate)
        
        # スコア順にソート
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return candidates[:5]  # 上位5名
    
    def _get_sample_substitute_candidates(self, absent_employee: Dict, shift_info: Dict) -> List[Dict]:
        """サンプル代替候補を生成"""
        sample_candidates = [
            {
                "employee_id": "EMP002",
                "name": "佐藤花子",
                "department": "営業部",
                "role": "リーダー",
                "skill_level": 5,
                "experience": "高",
                "availability": "○",
                "score": 92,
                "workload": 65,
                "past_substitutions": 8
            },
            {
                "employee_id": "EMP004",
                "name": "山田美咲",
                "department": "営業部",
                "role": "スタッフ",
                "skill_level": 4,
                "experience": "中",
                "availability": "○",
                "score": 78,
                "workload": 45,
                "past_substitutions": 3
            },
            {
                "employee_id": "EMP005",
                "name": "高橋健太",
                "department": "総務部",
                "role": "スタッフ",
                "skill_level": 2,
                "experience": "低",
                "availability": "△",
                "score": 58,
                "workload": 80,
                "past_substitutions": 1
            }
        ]
        
        return sample_candidates
    
    def _get_experience_level(self, staff_row: pd.Series) -> str:
        """経験レベルを判定"""
        skill_level = staff_row.get("スキルレベル", 3)
        tenure_months = staff_row.get("勤続月数", 0)
        
        if skill_level >= 4 and tenure_months >= 12:
            return "高"
        elif skill_level >= 3 and tenure_months >= 6:
            return "中"
        else:
            return "低"
    
    def _calculate_substitute_score(self, staff_row: pd.Series, absent_employee: Dict, shift_info: Dict) -> float:
        """代替候補のスコアを計算"""
        score = 50.0
        
        # 基本的な適性
        score += staff_row.get("スキルレベル", 3) * 8
        
        # 部門の一致
        if staff_row.get("部門") == absent_employee.get("department"):
            score += 20
        
        # 役職レベル
        role = staff_row.get("役職", "")
        if "リーダー" in role:
            score += 15
        elif "責任者" in role:
            score += 20
        
        # 勤続期間
        tenure_months = staff_row.get("勤続月数", 0)
        score += min(tenure_months * 0.3, 15)
        
        return min(score, 100)
    
    def _calculate_current_workload(self, staff_row: pd.Series) -> float:
        """現在の作業負荷を計算"""
        # 簡易実装（実際は勤務予定から計算）
        employment_type = staff_row.get("雇用形態", "")
        
        if employment_type == "正社員":
            return 70.0
        elif employment_type == "パート":
            return 50.0
        else:
            return 30.0