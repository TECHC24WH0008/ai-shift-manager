# -*- coding: utf-8 -*-
"""
SQLiteデータベース管理
スタッフ、シフト、勤怠データの効率的な管理
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import os

class DatabaseManager:
    """SQLiteデータベース管理クラス"""
    
    def __init__(self, db_path: str = "shift_manager.db"):
        self.db_path = db_path
        self.connection = None
        
        # データベース初期化
        self.initialize_database()
    
    def initialize_database(self):
        """データベースとテーブルの初期化"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            
            # テーブル作成
            self.create_tables()
            
            # インデックス作成
            self.create_indexes()
            
            logging.info(f"データベース初期化完了: {self.db_path}")
            
        except Exception as e:
            logging.error(f"データベース初期化エラー: {e}")
            raise
    
    def create_tables(self):
        """テーブル作成"""
        cursor = self.connection.cursor()
        
        # スタッフマスターテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_master (
                staff_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                hourly_wage INTEGER,
                employment_type TEXT,
                hire_date DATE,
                skill_level INTEGER,
                preferred_hours TEXT,
                contact TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # シフトマスターテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shift_master (
                shift_id TEXT PRIMARY KEY,
                staff_id TEXT,
                shift_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                break_minutes INTEGER DEFAULT 0,
                role TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff_master (staff_id)
            )
        ''')
        
        # 勤怠記録テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timecard_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT NOT NULL,
                work_date DATE NOT NULL,
                clock_in_time TIMESTAMP,
                clock_out_time TIMESTAMP,
                break_minutes INTEGER DEFAULT 0,
                actual_work_minutes INTEGER,
                overtime_minutes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'present',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff_master (staff_id)
            )
        ''')
        
        # 希望シフトテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shift_preferences (
                preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT NOT NULL,
                day_of_week INTEGER,  -- 0=月曜, 6=日曜
                preferred_start_time TIME,
                preferred_end_time TIME,
                availability_level INTEGER,  -- 1=不可, 2=可能, 3=希望, 4=強く希望
                special_notes TEXT,
                effective_from DATE,
                effective_to DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff_master (staff_id)
            )
        ''')
        
        # 欠勤記録テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS absence_records (
                absence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id TEXT NOT NULL,
                absence_date DATE NOT NULL,
                absence_type TEXT,  -- sick, personal, emergency, etc.
                reason TEXT,
                substitute_staff_id TEXT,
                notification_time TIMESTAMP,
                status TEXT DEFAULT 'pending',  -- pending, covered, uncovered
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff_master (staff_id),
                FOREIGN KEY (substitute_staff_id) REFERENCES staff_master (staff_id)
            )
        ''')
        
        # 設定テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT,
                setting_type TEXT,  -- string, integer, boolean, json
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 監査ログテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                action TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
                old_values TEXT,  -- JSON
                new_values TEXT,  -- JSON
                user_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
    
    def create_indexes(self):
        """インデックス作成（パフォーマンス向上）"""
        cursor = self.connection.cursor()
        
        # よく使用される検索条件にインデックスを作成
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_staff_department ON staff_master(department)",
            "CREATE INDEX IF NOT EXISTS idx_staff_active ON staff_master(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_shift_date ON shift_master(shift_date)",
            "CREATE INDEX IF NOT EXISTS idx_shift_staff_date ON shift_master(staff_id, shift_date)",
            "CREATE INDEX IF NOT EXISTS idx_timecard_date ON timecard_records(work_date)",
            "CREATE INDEX IF NOT EXISTS idx_timecard_staff_date ON timecard_records(staff_id, work_date)",
            "CREATE INDEX IF NOT EXISTS idx_absence_date ON absence_records(absence_date)",
            "CREATE INDEX IF NOT EXISTS idx_preferences_staff ON shift_preferences(staff_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.connection.commit()
    
    # === スタッフ管理 ===
    def add_staff(self, staff_data: Dict) -> bool:
        """スタッフ追加"""
        try:
            cursor = self.connection.cursor()
            
            # スタッフIDの自動生成
            if 'staff_id' not in staff_data or not staff_data['staff_id']:
                staff_data['staff_id'] = self.generate_staff_id()
            
            # 監査ログ用
            self.log_action('staff_master', staff_data['staff_id'], 'INSERT', None, staff_data)
            
            cursor.execute('''
                INSERT INTO staff_master 
                (staff_id, name, department, position, hourly_wage, employment_type, 
                 hire_date, skill_level, preferred_hours, contact, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                staff_data.get('staff_id'),
                staff_data.get('name'),
                staff_data.get('department'),
                staff_data.get('position'),
                staff_data.get('hourly_wage'),
                staff_data.get('employment_type'),
                staff_data.get('hire_date'),
                staff_data.get('skill_level'),
                staff_data.get('preferred_hours'),
                staff_data.get('contact'),
                staff_data.get('notes')
            ))
            
            self.connection.commit()
            logging.info(f"スタッフ追加完了: {staff_data.get('name')}")
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"スタッフ追加エラー: {e}")
            return False
    
    def update_staff(self, staff_id: str, staff_data: Dict) -> bool:
        """スタッフ情報更新"""
        try:
            cursor = self.connection.cursor()
            
            # 更新前のデータを取得（監査ログ用）
            old_data = self.get_staff_by_id(staff_id)
            
            # 更新実行
            set_clause = []
            values = []
            
            for key, value in staff_data.items():
                if key != 'staff_id':  # IDは更新しない
                    set_clause.append(f"{key} = ?")
                    values.append(value)
            
            values.append(staff_id)  # WHERE句用
            
            sql = f'''
                UPDATE staff_master 
                SET {', '.join(set_clause)}, updated_at = CURRENT_TIMESTAMP
                WHERE staff_id = ?
            '''
            
            cursor.execute(sql, values)
            
            # 監査ログ
            self.log_action('staff_master', staff_id, 'UPDATE', old_data, staff_data)
            
            self.connection.commit()
            logging.info(f"スタッフ更新完了: {staff_id}")
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"スタッフ更新エラー: {e}")
            return False
    
    def delete_staff(self, staff_id: str) -> bool:
        """スタッフ削除（論理削除）"""
        try:
            cursor = self.connection.cursor()
            
            # 削除前のデータを取得
            old_data = self.get_staff_by_id(staff_id)
            
            # 論理削除（is_active = 0）
            cursor.execute('''
                UPDATE staff_master 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE staff_id = ?
            ''', (staff_id,))
            
            # 監査ログ
            self.log_action('staff_master', staff_id, 'DELETE', old_data, {'is_active': False})
            
            self.connection.commit()
            logging.info(f"スタッフ削除完了: {staff_id}")
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"スタッフ削除エラー: {e}")
            return False
    
    def get_staff_list(self, active_only: bool = True) -> List[Dict]:
        """スタッフ一覧取得"""
        try:
            cursor = self.connection.cursor()
            
            sql = "SELECT * FROM staff_master"
            if active_only:
                sql += " WHERE is_active = 1"
            sql += " ORDER BY name"
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logging.error(f"スタッフ一覧取得エラー: {e}")
            return []
    
    def get_staff_by_id(self, staff_id: str) -> Optional[Dict]:
        """スタッフ情報取得"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM staff_master WHERE staff_id = ?", (staff_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
            
        except Exception as e:
            logging.error(f"スタッフ取得エラー: {e}")
            return None
    
    def search_staff(self, search_term: str, department: str = None) -> List[Dict]:
        """スタッフ検索"""
        try:
            cursor = self.connection.cursor()
            
            sql = '''
                SELECT * FROM staff_master 
                WHERE is_active = 1 
                AND (name LIKE ? OR staff_id LIKE ? OR contact LIKE ?)
            '''
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if department:
                sql += " AND department = ?"
                params.append(department)
            
            sql += " ORDER BY name"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logging.error(f"スタッフ検索エラー: {e}")
            return []
    
    # === シフト管理 ===
    def add_shift(self, shift_data: Dict) -> bool:
        """シフト追加"""
        try:
            cursor = self.connection.cursor()
            
            if 'shift_id' not in shift_data:
                shift_data['shift_id'] = self.generate_shift_id()
            
            cursor.execute('''
                INSERT INTO shift_master 
                (shift_id, staff_id, shift_date, start_time, end_time, break_minutes, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                shift_data.get('shift_id'),
                shift_data.get('staff_id'),
                shift_data.get('shift_date'),
                shift_data.get('start_time'),
                shift_data.get('end_time'),
                shift_data.get('break_minutes', 0),
                shift_data.get('role'),
                shift_data.get('status', 'scheduled')
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"シフト追加エラー: {e}")
            return False
    
    def get_shifts_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """期間指定でシフト取得"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT s.*, st.name as staff_name, st.department
                FROM shift_master s
                LEFT JOIN staff_master st ON s.staff_id = st.staff_id
                WHERE s.shift_date BETWEEN ? AND ?
                ORDER BY s.shift_date, s.start_time
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logging.error(f"シフト取得エラー: {e}")
            return []
    
    # === 勤怠管理 ===
    def clock_in(self, staff_id: str, clock_in_time: datetime = None) -> bool:
        """出勤打刻"""
        try:
            if not clock_in_time:
                clock_in_time = datetime.now()
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO timecard_records (staff_id, work_date, clock_in_time)
                VALUES (?, ?, ?)
            ''', (staff_id, clock_in_time.date(), clock_in_time))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"出勤打刻エラー: {e}")
            return False
    
    def clock_out(self, staff_id: str, work_date: str, clock_out_time: datetime = None) -> bool:
        """退勤打刻"""
        try:
            if not clock_out_time:
                clock_out_time = datetime.now()
            
            cursor = self.connection.cursor()
            
            # 該当日の勤怠記録を更新
            cursor.execute('''
                UPDATE timecard_records 
                SET clock_out_time = ?, 
                    actual_work_minutes = CAST((julianday(?) - julianday(clock_in_time)) * 24 * 60 AS INTEGER) - break_minutes
                WHERE staff_id = ? AND work_date = ? AND clock_out_time IS NULL
            ''', (clock_out_time, clock_out_time, staff_id, work_date))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logging.error(f"退勤打刻エラー: {e}")
            return False
    
    # === ユーティリティ ===
    def generate_staff_id(self) -> str:
        """スタッフID自動生成"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM staff_master")
        count = cursor.fetchone()[0]
        return f"EMP{count + 1:04d}"
    
    def generate_shift_id(self) -> str:
        """シフトID自動生成"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM shift_master")
        count = cursor.fetchone()[0]
        return f"SH{count + 1:06d}"
    
    def log_action(self, table_name: str, record_id: str, action: str, old_values: Dict, new_values: Dict):
        """監査ログ記録"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO audit_log (table_name, record_id, action, old_values, new_values)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                table_name,
                record_id,
                action,
                json.dumps(old_values, ensure_ascii=False) if old_values else None,
                json.dumps(new_values, ensure_ascii=False) if new_values else None
            ))
        except Exception as e:
            logging.error(f"監査ログエラー: {e}")
    
    # === CSV/Excelインポート ===
    def import_from_csv(self, file_path: str, table_type: str) -> Tuple[bool, str]:
        """CSV/Excelからデータインポート"""
        try:
            # ファイル読み込み
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
            
            success_count = 0
            error_count = 0
            
            if table_type == 'staff':
                for _, row in df.iterrows():
                    staff_data = {
                        'name': row.get('氏名'),
                        'department': row.get('部門'),
                        'position': row.get('役職'),
                        'hourly_wage': row.get('時給'),
                        'employment_type': row.get('雇用形態'),
                        'hire_date': row.get('入社日'),
                        'skill_level': row.get('スキルレベル'),
                        'preferred_hours': row.get('希望勤務時間'),
                        'contact': row.get('連絡先'),
                        'notes': row.get('備考')
                    }
                    
                    if self.add_staff(staff_data):
                        success_count += 1
                    else:
                        error_count += 1
            
            return True, f"インポート完了: 成功{success_count}件, エラー{error_count}件"
            
        except Exception as e:
            return False, f"インポートエラー: {str(e)}"
    
    def export_to_csv(self, table_type: str, file_path: str) -> bool:
        """CSV/Excelエクスポート"""
        try:
            if table_type == 'staff':
                data = self.get_staff_list()
                df = pd.DataFrame(data)
                
                # 列名を日本語に変換
                column_mapping = {
                    'staff_id': '従業員ID',
                    'name': '氏名',
                    'department': '部門',
                    'position': '役職',
                    'hourly_wage': '時給',
                    'employment_type': '雇用形態',
                    'hire_date': '入社日',
                    'skill_level': 'スキルレベル',
                    'preferred_hours': '希望勤務時間',
                    'contact': '連絡先',
                    'notes': '備考'
                }
                
                df = df.rename(columns=column_mapping)
                
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False, encoding='utf-8')
            
            return True
            
        except Exception as e:
            logging.error(f"エクスポートエラー: {e}")
            return False
    
    def close(self):
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """デストラクタ"""
        self.close()