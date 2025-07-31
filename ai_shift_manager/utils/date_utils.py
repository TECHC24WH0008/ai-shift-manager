# -*- coding: utf-8 -*-
"""
日付・時間関連ユーティリティ
"""

from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict
import calendar
import locale

class DateUtils:
    """日付ユーティリティクラス"""
    
    @staticmethod
    def get_japanese_weekday(date_obj: date) -> str:
        """日本語の曜日を取得"""
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        return weekdays[date_obj.weekday()]
    
    @staticmethod
    def get_month_calendar(year: int, month: int) -> List[List[int]]:
        """月のカレンダーを取得"""
        cal = calendar.monthcalendar(year, month)
        return cal
    
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[str]:
        """日付範囲のリストを取得"""
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def get_week_dates(target_date: str) -> Tuple[str, str, List[str]]:
        """指定日を含む週の日付リストを取得"""
        target = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 月曜日を週の開始とする
        monday = target - timedelta(days=target.weekday())
        sunday = monday + timedelta(days=6)
        
        week_dates = []
        current = monday
        for i in range(7):
            week_dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d'), week_dates
    
    @staticmethod
    def is_holiday(date_obj: date) -> bool:
        """祝日判定（簡易版）"""
        # 基本的な祝日のみ実装
        holidays = {
            (1, 1): "元日",
            (2, 11): "建国記念の日",
            (4, 29): "昭和の日",
            (5, 3): "憲法記念日",
            (5, 4): "みどりの日",
            (5, 5): "こどもの日",
            (11, 3): "文化の日",
            (11, 23): "勤労感謝の日",
            (12, 23): "天皇誕生日"
        }
        
        return (date_obj.month, date_obj.day) in holidays
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """分を時間:分形式に変換"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}:{mins:02d}"
    
    @staticmethod
    def parse_time_to_minutes(time_str: str) -> int:
        """HH:MM形式を分に変換"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute
        except:
            return 0
    
    @staticmethod
    def get_business_days(start_date: str, end_date: str) -> List[str]:
        """営業日（平日）のリストを取得"""
        dates = DateUtils.get_date_range(start_date, end_date)
        business_days = []
        
        for date_str in dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            # 土日と祝日を除外
            if date_obj.weekday() < 5 and not DateUtils.is_holiday(date_obj):
                business_days.append(date_str)
        
        return business_days

class TimeSlotManager:
    """時間帯管理クラス"""
    
    def __init__(self):
        self.default_slots = [
            {"name": "早朝", "start": "06:00", "end": "09:00"},
            {"name": "午前", "start": "09:00", "end": "12:00"},
            {"name": "午後", "start": "13:00", "end": "17:00"},
            {"name": "夕方", "start": "17:00", "end": "20:00"},
            {"name": "夜間", "start": "20:00", "end": "23:00"}
        ]
    
    def get_time_slot(self, time_str: str) -> str:
        """時間から時間帯を判定"""
        try:
            time_minutes = DateUtils.parse_time_to_minutes(time_str)
            
            for slot in self.default_slots:
                start_minutes = DateUtils.parse_time_to_minutes(slot["start"])
                end_minutes = DateUtils.parse_time_to_minutes(slot["end"])
                
                if start_minutes <= time_minutes < end_minutes:
                    return slot["name"]
            
            return "その他"
        except:
            return "不明"
    
    def get_overlapping_slots(self, start_time: str, end_time: str) -> List[str]:
        """勤務時間と重複する時間帯を取得"""
        try:
            start_minutes = DateUtils.parse_time_to_minutes(start_time)
            end_minutes = DateUtils.parse_time_to_minutes(end_time)
            
            # 日をまたぐ場合
            if end_minutes < start_minutes:
                end_minutes += 24 * 60
            
            overlapping = []
            for slot in self.default_slots:
                slot_start = DateUtils.parse_time_to_minutes(slot["start"])
                slot_end = DateUtils.parse_time_to_minutes(slot["end"])
                
                # 重複判定
                if not (end_minutes <= slot_start or start_minutes >= slot_end):
                    overlapping.append(slot["name"])
            
            return overlapping
        except:
            return []