# -*- coding: utf-8 -*-
"""
タイムカードデータ処理
CSV/Excelからの高速データ処理と分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import os

class TimecardProcessor:
    """タイムカードデータ処理クラス"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.timecard_cache = {}
        self.last_update = None
    
    def load_timecard_csv(self, file_path: str) -> Tuple[bool, str, pd.DataFrame]:
        """
        🔥 CSVタイムカードデータの高速読み込み
        
        Returns:
            (成功フラグ, メッセージ, データフレーム)
        """
        try:
            # ファイル存在チェック
            if not os.path.exists(file_path):
                return False, f"ファイルが見つかりません: {file_path}", pd.DataFrame()
            
            # CSV読み込み（複数エンコーディング対応）
            encodings = ['utf-8', 'shift_jis', 'cp932']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return False, "ファイルの文字エンコーディングが不正です", pd.DataFrame()
            
            # データ検証・正規化
            df_normalized = self.normalize_timecard_data(df)
            
            # キャッシュ更新
            self.timecard_cache = df_normalized.to_dict('records')
            self.last_update = datetime.now()
            
            return True, f"読み込み完了: {len(df_normalized)}件", df_normalized
            
        except Exception as e:
            logging.error(f"タイムカード読み込みエラー: {e}")
            return False, f"読み込みエラー: {str(e)}", pd.DataFrame()
    
    def normalize_timecard_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """タイムカードデータの正規化"""
        try:
            # 列名の正規化（よくある列名パターンに対応）
            column_mapping = {
                # 日付関連
                '日付': 'work_date', '勤務日': 'work_date', '出勤日': 'work_date',
                'Date': 'work_date', '年月日': 'work_date',
                
                # スタッフ関連
                '従業員ID': 'staff_id', '社員ID': 'staff_id', 'ID': 'staff_id',
                '氏名': 'staff_name', '名前': 'staff_name', '従業員名': 'staff_name',
                
                # 時間関連
                '出勤時間': 'clock_in', '開始時間': 'clock_in', '出社時間': 'clock_in',
                '退勤時間': 'clock_out', '終了時間': 'clock_out', '退社時間': 'clock_out',
                '休憩時間': 'break_minutes', '休憩': 'break_minutes',
                '実働時間': 'work_minutes', '労働時間': 'work_minutes',
                
                # 部門関連
                '部門': 'department', '所属': 'department', '部署': 'department',
                
                # その他
                '業務内容': 'work_content', '備考': 'notes'
            }
            
            # 列名変換
            df_renamed = df.rename(columns=column_mapping)
            
            # 必須列の存在チェック
            required_columns = ['work_date', 'staff_id', 'staff_name']
            missing_columns = [col for col in required_columns if col not in df_renamed.columns]
            
            if missing_columns:
                logging.warning(f"必須列が不足: {missing_columns}")
            
            # データ型変換
            if 'work_date' in df_renamed.columns:
                df_renamed['work_date'] = pd.to_datetime(df_renamed['work_date'], errors='coerce')
            
            # 時間データの正規化
            time_columns = ['clock_in', 'clock_out']
            for col in time_columns:
                if col in df_renamed.columns:
                    df_renamed[col] = self.normalize_time_format(df_renamed[col])
            
            # 数値データの正規化
            numeric_columns = ['break_minutes', 'work_minutes']
            for col in numeric_columns:
                if col in df_renamed.columns:
                    df_renamed[col] = pd.to_numeric(df_renamed[col], errors='coerce').fillna(0)
            
            # 実働時間の自動計算（未入力の場合）
            if 'work_minutes' not in df_renamed.columns or df_renamed['work_minutes'].isna().all():
                df_renamed['work_minutes'] = self.calculate_work_minutes(df_renamed)
            
            return df_renamed
            
        except Exception as e:
            logging.error(f"データ正規化エラー: {e}")
            return df
    
    def normalize_time_format(self, time_series: pd.Series) -> pd.Series:
        """時間フォーマットの正規化"""
        try:
            # 様々な時間フォーマットに対応
            normalized_times = []
            
            for time_value in time_series:
                if pd.isna(time_value):
                    normalized_times.append(None)
                    continue
                
                time_str = str(time_value).strip()
                
                # HH:MM形式に正規化
                if ':' in time_str:
                    normalized_times.append(time_str)
                elif len(time_str) == 4 and time_str.isdigit():
                    # HHMM形式 → HH:MM形式
                    normalized_times.append(f"{time_str[:2]}:{time_str[2:]}")
                elif len(time_str) == 3 and time_str.isdigit():
                    # HMM形式 → H:MM形式
                    normalized_times.append(f"{time_str[0]}:{time_str[1:]}")
                else:
                    normalized_times.append(time_str)
            
            return pd.Series(normalized_times)
            
        except Exception as e:
            logging.error(f"時間正規化エラー: {e}")
            return time_series
    
    def calculate_work_minutes(self, df: pd.DataFrame) -> pd.Series:
        """実働時間の自動計算"""
        try:
            work_minutes = []
            
            for _, row in df.iterrows():
                clock_in = row.get('clock_in')
                clock_out = row.get('clock_out')
                break_minutes = row.get('break_minutes', 0)
                
                if pd.isna(clock_in) or pd.isna(clock_out):
                    work_minutes.append(0)
                    continue
                
                try:
                    # 時間差計算
                    in_time = datetime.strptime(str(clock_in), '%H:%M')
                    out_time = datetime.strptime(str(clock_out), '%H:%M')
                    
                    # 日をまたぐ場合の処理
                    if out_time < in_time:
                        out_time += timedelta(days=1)
                    
                    total_minutes = (out_time - in_time).total_seconds() / 60
                    actual_work_minutes = total_minutes - break_minutes
                    
                    work_minutes.append(max(actual_work_minutes, 0))
                    
                except ValueError:
                    work_minutes.append(0)
            
            return pd.Series(work_minutes)
            
        except Exception as e:
            logging.error(f"実働時間計算エラー: {e}")
            return pd.Series([0] * len(df))
    
    def get_recent_work_history(self, staff_id: str, days: int = 14) -> List[Dict]:
        """直近の勤務履歴取得"""
        try:
            if not self.timecard_cache:
                return []
            
            # 対象期間
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # フィルタリング
            recent_records = []
            for record in self.timecard_cache:
                if record.get('staff_id') == staff_id:
                    work_date = record.get('work_date')
                    if isinstance(work_date, str):
                        work_date = datetime.strptime(work_date, '%Y-%m-%d')
                    
                    if start_date <= work_date <= end_date:
                        recent_records.append(record)
            
            return sorted(recent_records, key=lambda x: x.get('work_date', ''), reverse=True)
            
        except Exception as e:
            logging.error(f"勤務履歴取得エラー: {e}")
            return []
    
    def calculate_staff_reliability(self, staff_id: str, days: int = 30) -> Dict:
        """スタッフの信頼性指標計算"""
        try:
            records = self.get_recent_work_history(staff_id, days)
            
            if not records:
                return {
                    'attendance_rate': 0.0,
                    'punctuality_rate': 0.0,
                    'consistency_score': 0.0,
                    'total_work_days': 0
                }
            
            # 出勤率計算（予定日数との比較が必要だが、簡易版として実働日数を使用）
            total_work_days = len(records)
            
            # 遅刻率計算（9:00基準の簡易版）
            on_time_count = 0
            for record in records:
                clock_in = record.get('clock_in', '')
                if clock_in and self.is_on_time(clock_in, '09:00'):
                    on_time_count += 1
            
            punctuality_rate = on_time_count / total_work_days if total_work_days > 0 else 0
            
            # 勤務時間の一貫性
            work_minutes_list = [record.get('work_minutes', 0) for record in records]
            if work_minutes_list:
                avg_work_minutes = np.mean(work_minutes_list)
                std_work_minutes = np.std(work_minutes_list)
                consistency_score = max(0, 1 - (std_work_minutes / avg_work_minutes)) if avg_work_minutes > 0 else 0
            else:
                consistency_score = 0
            
            return {
                'attendance_rate': 1.0,  # 実働日ベースなので100%
                'punctuality_rate': punctuality_rate,
                'consistency_score': consistency_score,
                'total_work_days': total_work_days,
                'avg_work_hours': np.mean(work_minutes_list) / 60 if work_minutes_list else 0
            }
            
        except Exception as e:
            logging.error(f"信頼性計算エラー: {e}")
            return {'attendance_rate': 0, 'punctuality_rate': 0, 'consistency_score': 0, 'total_work_days': 0}
    
    def is_on_time(self, actual_time: str, scheduled_time: str, tolerance_minutes: int = 10) -> bool:
        """時間通りかチェック"""
        try:
            actual = datetime.strptime(actual_time, '%H:%M')
            scheduled = datetime.strptime(scheduled_time, '%H:%M')
            
            diff_minutes = (actual - scheduled).total_seconds() / 60
            return abs(diff_minutes) <= tolerance_minutes
            
        except ValueError:
            return False
    
    def get_department_experience(self, staff_id: str, department: str, days: int = 90) -> Dict:
        """部門経験度計算"""
        try:
            records = self.get_recent_work_history(staff_id, days)
            
            if not records:
                return {'experience_days': 0, 'familiarity_rate': 0.0, 'last_worked': None}
            
            # 該当部門での勤務記録
            dept_records = [r for r in records if r.get('department') == department]
            
            experience_days = len(dept_records)
            familiarity_rate = experience_days / len(records) if records else 0
            
            last_worked = None
            if dept_records:
                latest_record = max(dept_records, key=lambda x: x.get('work_date', ''))
                last_worked = latest_record.get('work_date')
            
            return {
                'experience_days': experience_days,
                'familiarity_rate': familiarity_rate,
                'last_worked': last_worked,
                'total_records': len(records)
            }
            
        except Exception as e:
            logging.error(f"部門経験度計算エラー: {e}")
            return {'experience_days': 0, 'familiarity_rate': 0.0, 'last_worked': None}
    
    def detect_staffing_gaps(self, target_date: str = None) -> List[Dict]:
        """🔥 人員不足の自動検出"""
        try:
            if not target_date:
                target_date = datetime.now().strftime('%Y-%m-%d')
            
            # 当日の勤務予定と実績を比較
            scheduled_staff = self.get_scheduled_staff(target_date)
            actual_staff = self.get_actual_staff(target_date)
            
            gaps = []
            
            # 部門別の人員不足チェック
            departments = set([s.get('department') for s in scheduled_staff if s.get('department')])
            
            for dept in departments:
                scheduled_count = len([s for s in scheduled_staff if s.get('department') == dept])
                actual_count = len([s for s in actual_staff if s.get('department') == dept])
                
                if actual_count < scheduled_count:
                    gap_info = {
                        'date': target_date,
                        'department': dept,
                        'scheduled_count': scheduled_count,
                        'actual_count': actual_count,
                        'shortage': scheduled_count - actual_count,
                        'severity': self.get_shortage_severity(scheduled_count - actual_count, scheduled_count)
                    }
                    gaps.append(gap_info)
            
            return gaps
            
        except Exception as e:
            logging.error(f"人員不足検出エラー: {e}")
            return []
    
    def get_shortage_severity(self, shortage: int, total_scheduled: int) -> str:
        """人員不足の深刻度"""
        if total_scheduled == 0:
            return "🟢 正常"
        
        shortage_rate = shortage / total_scheduled
        
        if shortage_rate >= 0.5:
            return "🔴 深刻"
        elif shortage_rate >= 0.3:
            return "🟠 注意"
        elif shortage_rate > 0:
            return "🟡 軽微"
        else:
            return "🟢 正常"
    
    def get_scheduled_staff(self, date: str) -> List[Dict]:
        """予定スタッフ取得（実装は shift_manager に依存）"""
        # 実際の実装では shift_manager から取得
        return []
    
    def get_actual_staff(self, date: str) -> List[Dict]:
        """実際の出勤スタッフ取得"""
        if not self.timecard_cache:
            return []
        
        return [record for record in self.timecard_cache 
                if record.get('work_date') == date]