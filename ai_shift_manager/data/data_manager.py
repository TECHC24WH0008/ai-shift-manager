# -*- coding: utf-8 -*-
"""
データ管理クラス
スタッフ情報、シフトデータ、勤怠データの管理を行う
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from .database_manager import DatabaseManager

class DataManager:
    """データ管理の中核クラス（SQLite統合版）"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        
        if use_database:
            # SQLiteデータベースを使用
            self.db = DatabaseManager()
            logging.info("SQLiteデータベースモードで初期化")
        else:
            # 従来のCSV/JSONファイルを使用
            self.staff_data = pd.DataFrame()
            self.shift_data = pd.DataFrame()
            self.timecard_data = pd.DataFrame()
            self.config_data = {}
            
            # データファイルパス
            self.staff_file = "sample_staff_info.csv"
            self.timecard_file = "sample_timecard.csv"
            self.shift_requests_file = "sample_shift_requests.csv"
            self.config_file = "data_config.json"
            
            # 初期化
            self.load_all_data()
            logging.info("CSVファイルモードで初期化")
    
    def load_all_data(self):
        """すべてのデータを読み込み"""
        try:
            self.load_staff_data()
            self.load_timecard_data()
            self.load_shift_requests()
            self.load_config()
            logging.info("データの読み込みが完了しました")
        except Exception as e:
            logging.error(f"データ読み込みエラー: {e}")
    
    def load_staff_data(self):
        """スタッフデータを読み込み"""
        if os.path.exists(self.staff_file):
            self.staff_data = pd.read_csv(self.staff_file, encoding='utf-8')
        else:
            self.staff_data = pd.DataFrame(columns=[
                '従業員ID', '氏名', '部門', '役職', '時給', '雇用形態',
                '入社日', 'スキルレベル', '希望勤務時間', '連絡先', '備考'
            ])
    
    def load_timecard_data(self):
        """勤怠データを読み込み"""
        if os.path.exists(self.timecard_file):
            self.timecard_data = pd.read_csv(self.timecard_file, encoding='utf-8')
        else:
            self.timecard_data = pd.DataFrame(columns=[
                '日付', '従業員ID', '氏名', '出勤時間', '退勤時間',
                '休憩時間', '実働時間', '部門', '業務内容', '評価'
            ])
    
    def load_shift_requests(self):
        """シフト希望データを読み込み"""
        if os.path.exists(self.shift_requests_file):
            self.shift_data = pd.read_csv(self.shift_requests_file, encoding='utf-8')
        else:
            self.shift_data = pd.DataFrame(columns=[
                '従業員ID', '氏名', '希望日', '希望時間帯', '優先度', '理由'
            ])
    
    def load_config(self):
        """設定データを読み込み"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        else:
            self.config_data = {
                "business_hours": {"start": "09:00", "end": "18:00"},
                "break_time": 60,
                "min_staff_per_shift": 2,
                "max_consecutive_days": 5
            }
    
    def get_staff_list(self) -> List[Dict]:
        """スタッフ一覧を取得"""
        if self.use_database:
            return self.db.get_staff_list()
        else:
            return self.staff_data.to_dict('records')
    
    def get_staff_by_id(self, staff_id: str) -> Optional[Dict]:
        """IDでスタッフ情報を取得"""
        if self.use_database:
            return self.db.get_staff_by_id(staff_id)
        else:
            staff = self.staff_data[self.staff_data['従業員ID'] == staff_id]
            return staff.iloc[0].to_dict() if not staff.empty else None
    
    def add_staff(self, staff_info: Dict) -> bool:
        """スタッフを追加"""
        if self.use_database:
            # データベース用のキー名に変換
            db_staff_info = self.convert_to_db_format(staff_info)
            return self.db.add_staff(db_staff_info)
        else:
            try:
                new_staff = pd.DataFrame([staff_info])
                self.staff_data = pd.concat([self.staff_data, new_staff], ignore_index=True)
                self.save_staff_data()
                return True
            except Exception as e:
                logging.error(f"スタッフ追加エラー: {e}")
                return False
    
    def update_staff(self, staff_id: str, staff_info: Dict) -> bool:
        """スタッフ情報を更新"""
        if self.use_database:
            db_staff_info = self.convert_to_db_format(staff_info)
            return self.db.update_staff(staff_id, db_staff_info)
        else:
            try:
                mask = self.staff_data['従業員ID'] == staff_id
                for key, value in staff_info.items():
                    self.staff_data.loc[mask, key] = value
                self.save_staff_data()
                return True
            except Exception as e:
                logging.error(f"スタッフ更新エラー: {e}")
                return False
    
    def delete_staff(self, staff_id: str) -> bool:
        """スタッフを削除"""
        if self.use_database:
            return self.db.delete_staff(staff_id)
        else:
            try:
                self.staff_data = self.staff_data[self.staff_data['従業員ID'] != staff_id]
                self.save_staff_data()
                return True
            except Exception as e:
                logging.error(f"スタッフ削除エラー: {e}")
                return False
    
    def search_staff(self, search_term: str, department: str = None) -> List[Dict]:
        """スタッフ検索"""
        if self.use_database:
            return self.db.search_staff(search_term, department)
        else:
            # CSV版の検索実装
            filtered_data = self.staff_data[
                self.staff_data['氏名'].str.contains(search_term, na=False) |
                self.staff_data['従業員ID'].str.contains(search_term, na=False)
            ]
            if department:
                filtered_data = filtered_data[filtered_data['部門'] == department]
            return filtered_data.to_dict('records')
    
    def convert_to_db_format(self, staff_info: Dict) -> Dict:
        """CSV形式からDB形式にキー名を変換"""
        key_mapping = {
            '従業員ID': 'staff_id',
            '氏名': 'name',
            '部門': 'department',
            '役職': 'position',
            '時給': 'hourly_wage',
            '雇用形態': 'employment_type',
            '入社日': 'hire_date',
            'スキルレベル': 'skill_level',
            '希望勤務時間': 'preferred_hours',
            '連絡先': 'contact',
            '備考': 'notes'
        }
        
        db_format = {}
        for csv_key, db_key in key_mapping.items():
            if csv_key in staff_info:
                db_format[db_key] = staff_info[csv_key]
        
        return db_format
    
    def get_timecard_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """勤怠データを取得"""
        data = self.timecard_data.copy()
        
        if start_date:
            data = data[data['日付'] >= start_date]
        if end_date:
            data = data[data['日付'] <= end_date]
        
        return data.to_dict('records')
    
    def add_timecard_entry(self, entry: Dict) -> bool:
        """勤怠記録を追加"""
        try:
            new_entry = pd.DataFrame([entry])
            self.timecard_data = pd.concat([self.timecard_data, new_entry], ignore_index=True)
            self.save_timecard_data()
            return True
        except Exception as e:
            logging.error(f"勤怠記録追加エラー: {e}")
            return False
    
    def get_shift_requests(self, date: str = None) -> List[Dict]:
        """シフト希望を取得"""
        data = self.shift_data.copy()
        
        if date:
            data = data[data['希望日'] == date]
        
        return data.to_dict('records')
    
    def save_staff_data(self):
        """スタッフデータを保存"""
        self.staff_data.to_csv(self.staff_file, index=False, encoding='utf-8')
    
    def save_timecard_data(self):
        """勤怠データを保存"""
        self.timecard_data.to_csv(self.timecard_file, index=False, encoding='utf-8')
    
    def save_shift_data(self):
        """シフトデータを保存"""
        self.shift_data.to_csv(self.shift_requests_file, index=False, encoding='utf-8')
    
    def save_config(self):
        """設定データを保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        return {
            "total_staff": len(self.staff_data),
            "active_staff": len(self.staff_data[self.staff_data['雇用形態'] != '退職']),
            "total_shifts": len(self.shift_data),
            "total_timecard_entries": len(self.timecard_data)
        }