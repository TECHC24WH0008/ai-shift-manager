# -*- coding: utf-8 -*-
"""
緊急代替要員システム
欠勤発生時の即座の代替候補提案に特化
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

class EmergencySubstituteSystem:
    """緊急代替要員システム - 最優先機能"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        
        # 信頼スコア重み設定
        self.weights = {
            'recent_experience': 0.4,    # 直近勤務経験
            'department_familiarity': 0.3, # 部門慣れ度
            'reliability_score': 0.2,     # 信頼性スコア
            'availability': 0.1           # 勤務可能性
        }
    
    def find_emergency_substitute(self, absent_staff_id: str, absence_date: str, 
                                shift_time: str) -> List[Dict]:
        """
        🔥 緊急代替要員を即座に提案
        
        Args:
            absent_staff_id: 欠勤者ID
            absence_date: 欠勤日
            shift_time: シフト時間
            
        Returns:
            代替候補リスト（優先順）
        """
        try:
            # 1. 欠勤者の情報取得
            absent_staff = self.get_staff_info(absent_staff_id)
            if not absent_staff:
                return []
            
            # 2. 利用可能スタッフ取得
            available_staff = self.get_available_staff(absence_date, shift_time)
            
            # 3. 各候補の緊急対応スコア計算
            candidates = []
            for staff in available_staff:
                if staff['staff_id'] != absent_staff_id:
                    score_data = self.calculate_emergency_score(
                        absent_staff, staff, absence_date, shift_time
                    )
                    
                    candidates.append({
                        'staff_id': staff['staff_id'],
                        'name': staff['name'],
                        'total_score': score_data['total_score'],
                        'confidence_level': self.get_confidence_level(score_data['total_score']),
                        'quick_reason': self.generate_quick_reason(absent_staff, staff, score_data),
                        'detailed_scores': score_data,
                        'can_start_immediately': self.can_start_immediately(staff, absence_date),
                        'contact_info': staff.get('contact', ''),
                        'last_worked_this_role': self.get_last_worked_date(staff['staff_id'], absent_staff['department'])
                    })
            
            # 4. スコア順にソート
            candidates.sort(key=lambda x: x['total_score'], reverse=True)
            
            # 5. 上位3名を返す（緊急時は選択肢を絞る）
            return candidates[:3]
            
        except Exception as e:
            logging.error(f"緊急代替要員検索エラー: {e}")
            return []
    
    def calculate_emergency_score(self, absent_staff: Dict, candidate: Dict, 
                                absence_date: str, shift_time: str) -> Dict:
        """緊急時特化のスコア計算"""
        
        # 1. 直近勤務経験（過去2週間）
        recent_exp_score = self.calculate_recent_experience(
            candidate['staff_id'], absent_staff['department'], absence_date
        )
        
        # 2. 部門慣れ度
        dept_familiarity_score = self.calculate_department_familiarity(
            candidate['staff_id'], absent_staff['department']
        )
        
        # 3. 信頼性スコア（過去の勤務実績）
        reliability_score = self.calculate_reliability_score(candidate['staff_id'])
        
        # 4. 即座の勤務可能性
        availability_score = self.calculate_immediate_availability(
            candidate, absence_date, shift_time
        )
        
        # 重み付き合計
        total_score = (
            recent_exp_score * self.weights['recent_experience'] +
            dept_familiarity_score * self.weights['department_familiarity'] +
            reliability_score * self.weights['reliability_score'] +
            availability_score * self.weights['availability']
        ) * 100
        
        return {
            'total_score': min(total_score, 100),
            'recent_experience': recent_exp_score,
            'department_familiarity': dept_familiarity_score,
            'reliability_score': reliability_score,
            'availability': availability_score
        }
    
    def calculate_recent_experience(self, staff_id: str, department: str, 
                                  absence_date: str) -> float:
        """直近2週間の勤務経験"""
        try:
            end_date = datetime.strptime(absence_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=14)
            
            # 実際のタイムカードデータから取得
            recent_records = self.get_timecard_records(
                staff_id, start_date.strftime('%Y-%m-%d'), absence_date
            )
            
            # 同部門での勤務日数
            dept_days = sum(1 for record in recent_records 
                          if record.get('department') == department)
            
            # 最大14日で正規化
            return min(dept_days / 14.0, 1.0)
            
        except Exception as e:
            logging.error(f"直近経験計算エラー: {e}")
            return 0.0
    
    def calculate_department_familiarity(self, staff_id: str, department: str) -> float:
        """部門慣れ度（過去3ヶ月）"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            # 過去3ヶ月の勤務記録
            records = self.get_timecard_records(
                staff_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            )
            
            if not records:
                return 0.0
            
            # 該当部門での勤務割合
            dept_records = [r for r in records if r.get('department') == department]
            familiarity = len(dept_records) / len(records)
            
            return familiarity
            
        except Exception as e:
            logging.error(f"部門慣れ度計算エラー: {e}")
            return 0.0
    
    def calculate_reliability_score(self, staff_id: str) -> float:
        """信頼性スコア（出勤率・遅刻率など）"""
        try:
            # 過去1ヶ月の勤務実績
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            records = self.get_timecard_records(
                staff_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            )
            
            if not records:
                return 0.5  # デフォルト値
            
            # 出勤率計算
            scheduled_days = self.get_scheduled_days(staff_id, start_date, end_date)
            attendance_rate = len(records) / max(scheduled_days, 1)
            
            # 遅刻率計算（簡易版）
            on_time_count = sum(1 for record in records 
                              if self.is_on_time(record))
            punctuality_rate = on_time_count / len(records)
            
            # 総合信頼性スコア
            reliability = (attendance_rate * 0.7 + punctuality_rate * 0.3)
            return min(reliability, 1.0)
            
        except Exception as e:
            logging.error(f"信頼性スコア計算エラー: {e}")
            return 0.5
    
    def calculate_immediate_availability(self, candidate: Dict, absence_date: str, 
                                      shift_time: str) -> float:
        """即座の勤務可能性"""
        try:
            # 雇用形態による基本可能性
            employment_type = candidate.get('employment_type', '')
            if employment_type == '正社員':
                base_score = 0.9
            elif employment_type == 'パート':
                base_score = 0.7
            else:
                base_score = 0.5
            
            # 希望勤務時間との適合度
            preferred_hours = candidate.get('preferred_hours', '')
            time_match = self.check_time_compatibility(preferred_hours, shift_time)
            
            # 当日の他シフトとの重複チェック
            has_conflict = self.check_schedule_conflict(
                candidate['staff_id'], absence_date, shift_time
            )
            
            conflict_penalty = 0.3 if has_conflict else 0.0
            
            return max((base_score * time_match) - conflict_penalty, 0.0)
            
        except Exception as e:
            logging.error(f"即座可能性計算エラー: {e}")
            return 0.0
    
    def get_confidence_level(self, score: float) -> str:
        """信頼度レベル"""
        if score >= 90:
            return "🟢 最適"
        elif score >= 75:
            return "🟡 適合"
        elif score >= 60:
            return "🟠 可能"
        else:
            return "🔴 要検討"
    
    def generate_quick_reason(self, absent_staff: Dict, candidate: Dict, 
                            score_data: Dict) -> str:
        """簡潔な推薦理由"""
        reasons = []
        
        # 最も高いスコア要素を特定
        scores = {
            'recent_experience': score_data['recent_experience'],
            'department_familiarity': score_data['department_familiarity'],
            'reliability_score': score_data['reliability_score'],
            'availability': score_data['availability']
        }
        
        max_factor = max(scores, key=scores.get)
        
        if max_factor == 'recent_experience' and scores[max_factor] > 0.7:
            reasons.append("直近2週間で同部門勤務")
        
        if max_factor == 'department_familiarity' and scores[max_factor] > 0.8:
            reasons.append("部門に慣れている")
        
        if max_factor == 'reliability_score' and scores[max_factor] > 0.8:
            reasons.append("出勤率・信頼性が高い")
        
        if scores['availability'] > 0.8:
            reasons.append("即座に対応可能")
        
        if not reasons:
            reasons.append("対応可能な候補")
        
        return " / ".join(reasons)
    
    def can_start_immediately(self, staff: Dict, absence_date: str) -> bool:
        """即座に開始可能かチェック"""
        # 当日の他シフトとの重複がないかチェック
        return not self.check_schedule_conflict(
            staff['staff_id'], absence_date, None
        )
    
    def get_last_worked_date(self, staff_id: str, department: str) -> Optional[str]:
        """最後に該当部門で働いた日"""
        try:
            records = self.get_timecard_records(staff_id, None, None, department)
            if records:
                latest_record = max(records, key=lambda x: x.get('work_date', ''))
                return latest_record.get('work_date')
            return None
        except:
            return None
    
    # データ取得メソッド（実装は data_manager に依存）
    def get_staff_info(self, staff_id: str) -> Optional[Dict]:
        """スタッフ情報取得"""
        if self.data_manager:
            return self.data_manager.get_staff_by_id(staff_id)
        return None
    
    def get_available_staff(self, date: str, shift_time: str) -> List[Dict]:
        """利用可能スタッフ取得"""
        if self.data_manager:
            return self.data_manager.get_staff_list()
        return []
    
    def get_timecard_records(self, staff_id: str, start_date: str = None, 
                           end_date: str = None, department: str = None) -> List[Dict]:
        """タイムカード記録取得"""
        # 実際の実装では data_manager から取得
        return []
    
    def get_scheduled_days(self, staff_id: str, start_date: datetime, 
                         end_date: datetime) -> int:
        """予定勤務日数取得"""
        return 20  # サンプル値
    
    def is_on_time(self, record: Dict) -> bool:
        """時間通りの出勤かチェック"""
        return True  # サンプル値
    
    def check_time_compatibility(self, preferred_hours: str, shift_time: str) -> float:
        """時間適合度チェック"""
        if 'フルタイム' in preferred_hours:
            return 1.0
        return 0.7  # サンプル値
    
    def check_schedule_conflict(self, staff_id: str, date: str, 
                              shift_time: str) -> bool:
        """スケジュール重複チェック"""
        return False  # サンプル値