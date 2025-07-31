# -*- coding: utf-8 -*-
"""
データ検証ユーティリティ
"""

import re
from datetime import datetime
from typing import Any, Tuple, List, Dict
import pandas as pd

class DataValidator:
    """データ検証クラス"""
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> Tuple[bool, str]:
        """従業員IDの検証"""
        if not employee_id or len(str(employee_id).strip()) == 0:
            return False, "従業員IDが空です"
        
        # 英数字のみ許可
        if not re.match(r'^[A-Za-z0-9]+$', str(employee_id)):
            return False, "従業員IDは英数字のみ使用可能です"
        
        return True, "OK"
    
    @staticmethod
    def validate_time_format(time_str: str) -> Tuple[bool, str]:
        """時間形式の検証 (HH:MM)"""
        if not time_str:
            return False, "時間が入力されていません"
        
        if not re.match(r'^\d{1,2}:\d{2}$', str(time_str)):
            return False, "時間形式が正しくありません (HH:MM形式で入力してください)"
        
        try:
            hour, minute = map(int, str(time_str).split(':'))
            if hour < 0 or hour > 23:
                return False, "時間は0-23の範囲で入力してください"
            if minute < 0 or minute > 59:
                return False, "分は0-59の範囲で入力してください"
        except ValueError:
            return False, "時間形式が正しくありません"
        
        return True, "OK"
    
    @staticmethod
    def validate_date_format(date_str: str) -> Tuple[bool, str]:
        """日付形式の検証"""
        if not date_str:
            return False, "日付が入力されていません"
        
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True, "OK"
        except ValueError:
            try:
                datetime.strptime(str(date_str), '%Y/%m/%d')
                return True, "OK"
            except ValueError:
                return False, "日付形式が正しくありません (YYYY-MM-DD または YYYY/MM/DD)"
    
    @staticmethod
    def validate_hourly_wage(wage: Any) -> Tuple[bool, str]:
        """時給の検証"""
        try:
            wage_float = float(wage)
            if wage_float < 800:
                return False, "時給は800円以上で入力してください"
            if wage_float > 10000:
                return False, "時給は10000円以下で入力してください"
            return True, "OK"
        except (ValueError, TypeError):
            return False, "時給は数値で入力してください"
    
    @staticmethod
    def validate_skill_level(skill: Any) -> Tuple[bool, str]:
        """スキルレベルの検証"""
        try:
            skill_int = int(skill)
            if skill_int < 1 or skill_int > 5:
                return False, "スキルレベルは1-5の範囲で入力してください"
            return True, "OK"
        except (ValueError, TypeError):
            return False, "スキルレベルは整数で入力してください"

class BusinessRuleValidator:
    """業務ルール検証クラス"""
    
    @staticmethod
    def validate_work_hours(start_time: str, end_time: str, break_minutes: int = 0) -> Tuple[bool, str, int]:
        """勤務時間の妥当性を検証"""
        try:
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            
            # 日をまたぐ場合の処理
            if end_dt < start_dt:
                end_dt = end_dt.replace(day=start_dt.day + 1)
            
            total_minutes = int((end_dt - start_dt).total_seconds() / 60)
            work_minutes = total_minutes - break_minutes
            
            if work_minutes <= 0:
                return False, "実働時間がマイナスまたは0です", 0
            
            if work_minutes > 960:  # 16時間
                return False, "1日の勤務時間は16時間以内にしてください", work_minutes
            
            # 6時間以上の場合は45分以上の休憩が必要
            if work_minutes > 360 and break_minutes < 45:
                return False, "6時間を超える勤務には45分以上の休憩が必要です", work_minutes
            
            # 8時間以上の場合は60分以上の休憩が必要
            if work_minutes > 480 and break_minutes < 60:
                return False, "8時間を超える勤務には60分以上の休憩が必要です", work_minutes
            
            return True, "OK", work_minutes
            
        except ValueError:
            return False, "時間形式が正しくありません", 0
    
    @staticmethod
    def validate_consecutive_work_days(employee_shifts: List[Dict]) -> Tuple[bool, str]:
        """連続勤務日数の検証"""
        if len(employee_shifts) < 6:
            return True, "OK"
        
        # 日付でソート
        sorted_shifts = sorted(employee_shifts, key=lambda x: x.get('date', ''))
        
        consecutive_days = 1
        max_consecutive = 1
        
        for i in range(1, len(sorted_shifts)):
            prev_date = datetime.strptime(sorted_shifts[i-1]['date'], '%Y-%m-%d')
            curr_date = datetime.strptime(sorted_shifts[i]['date'], '%Y-%m-%d')
            
            if (curr_date - prev_date).days == 1:
                consecutive_days += 1
                max_consecutive = max(max_consecutive, consecutive_days)
            else:
                consecutive_days = 1
        
        if max_consecutive > 6:
            return False, f"連続勤務が{max_consecutive}日続いています（法定上限: 6日）"
        
        return True, "OK"
    
    @staticmethod
    def validate_weekly_work_hours(employee_shifts: List[Dict]) -> Tuple[bool, str]:
        """週間労働時間の検証"""
        total_minutes = sum(shift.get('work_minutes', 0) for shift in employee_shifts)
        total_hours = total_minutes / 60
        
        if total_hours > 40:
            return False, f"週間労働時間が{total_hours:.1f}時間です（法定上限: 40時間）"
        
        return True, "OK"