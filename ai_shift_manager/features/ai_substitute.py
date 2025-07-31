# -*- coding: utf-8 -*-
"""
AI代替要員機能
機械学習を使用した最適な代替要員の提案
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

class AISubstitute:
    """AI代替要員分析クラス"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        
        # 分析パラメータ
        self.skill_weight = 0.3
        self.availability_weight = 0.4
        self.experience_weight = 0.2
        self.preference_weight = 0.1
        
        # スキルマッピング
        self.skill_mapping = {
            "接客": ["接客", "販売", "レジ"],
            "調理": ["調理", "キッチン", "食品"],
            "事務": ["事務", "PC", "データ入力"],
            "管理": ["管理", "リーダー", "監督"]
        }
    
    def analyze_substitute_candidates(self, absent_staff_id: str, absence_date: str, 
                                   shift_time: str) -> List[Dict]:
        """代替候補を分析して推薦リストを生成"""
        try:
            # 欠勤者の情報を取得
            absent_staff = self.get_staff_info(absent_staff_id)
            if not absent_staff:
                return []
            
            # 利用可能なスタッフを取得
            available_staff = self.get_available_staff(absence_date, shift_time)
            
            # 各候補者のスコアを計算
            candidates = []
            for staff in available_staff:
                if staff['従業員ID'] != absent_staff_id:
                    score = self.calculate_substitute_score(absent_staff, staff, absence_date, shift_time)
                    candidates.append({
                        'staff_id': staff['従業員ID'],
                        'name': staff['氏名'],
                        'score': score,
                        'details': self.get_score_details(absent_staff, staff),
                        'recommendation_reason': self.generate_recommendation_reason(absent_staff, staff, score)
                    })
            
            # スコア順にソート
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            return candidates[:5]  # 上位5名を返す
            
        except Exception as e:
            logging.error(f"代替候補分析エラー: {e}")
            return []
    
    def calculate_substitute_score(self, absent_staff: Dict, candidate_staff: Dict, 
                                 absence_date: str, shift_time: str) -> float:
        """代替候補のスコアを計算"""
        try:
            # スキル適合度
            skill_score = self.calculate_skill_compatibility(absent_staff, candidate_staff)
            
            # 勤務可能性
            availability_score = self.calculate_availability_score(candidate_staff, absence_date, shift_time)
            
            # 経験値
            experience_score = self.calculate_experience_score(candidate_staff)
            
            # 希望適合度
            preference_score = self.calculate_preference_score(candidate_staff, absence_date, shift_time)
            
            # 重み付き合計スコア
            total_score = (
                skill_score * self.skill_weight +
                availability_score * self.availability_weight +
                experience_score * self.experience_weight +
                preference_score * self.preference_weight
            )
            
            return min(total_score * 100, 100)  # 0-100の範囲に正規化
            
        except Exception as e:
            logging.error(f"スコア計算エラー: {e}")
            return 0.0
    
    def calculate_skill_compatibility(self, absent_staff: Dict, candidate_staff: Dict) -> float:
        """スキル適合度を計算"""
        try:
            absent_dept = absent_staff.get('部門', '')
            candidate_dept = candidate_staff.get('部門', '')
            
            absent_role = absent_staff.get('役職', '')
            candidate_role = candidate_staff.get('役職', '')
            
            absent_skill = int(absent_staff.get('スキルレベル', 1))
            candidate_skill = int(candidate_staff.get('スキルレベル', 1))
            
            # 部門一致度
            dept_match = 1.0 if absent_dept == candidate_dept else 0.5
            
            # 役職一致度
            role_match = 1.0 if absent_role == candidate_role else 0.7
            
            # スキルレベル適合度
            skill_diff = abs(absent_skill - candidate_skill)
            skill_match = max(0, 1.0 - (skill_diff * 0.2))
            
            return (dept_match * 0.4 + role_match * 0.3 + skill_match * 0.3)
            
        except Exception as e:
            logging.error(f"スキル適合度計算エラー: {e}")
            return 0.0
    
    def calculate_availability_score(self, candidate_staff: Dict, absence_date: str, shift_time: str) -> float:
        """勤務可能性スコアを計算"""
        try:
            # 雇用形態による基本スコア
            employment_type = candidate_staff.get('雇用形態', '')
            if employment_type == '正社員':
                base_score = 0.9
            elif employment_type == 'パート':
                base_score = 0.7
            else:  # アルバイト
                base_score = 0.5
            
            # 希望勤務時間との適合度
            preferred_hours = candidate_staff.get('希望勤務時間', '')
            if 'フルタイム' in preferred_hours:
                time_match = 1.0
            elif self.is_time_compatible(preferred_hours, shift_time):
                time_match = 0.8
            else:
                time_match = 0.3
            
            return base_score * time_match
            
        except Exception as e:
            logging.error(f"勤務可能性計算エラー: {e}")
            return 0.0
    
    def calculate_experience_score(self, candidate_staff: Dict) -> float:
        """経験値スコアを計算"""
        try:
            # 入社日から勤務期間を計算
            hire_date_str = candidate_staff.get('入社日', '')
            if hire_date_str:
                hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')
                work_days = (datetime.now() - hire_date).days
                
                # 勤務期間による経験値（最大1年で満点）
                experience_score = min(work_days / 365, 1.0)
            else:
                experience_score = 0.5
            
            # スキルレベルも考慮
            skill_level = int(candidate_staff.get('スキルレベル', 1))
            skill_score = skill_level / 5.0
            
            return (experience_score * 0.6 + skill_score * 0.4)
            
        except Exception as e:
            logging.error(f"経験値計算エラー: {e}")
            return 0.0
    
    def calculate_preference_score(self, candidate_staff: Dict, absence_date: str, shift_time: str) -> float:
        """希望適合度スコアを計算"""
        try:
            # 基本的な希望勤務時間との適合度
            preferred_hours = candidate_staff.get('希望勤務時間', '')
            
            if self.is_time_compatible(preferred_hours, shift_time):
                return 1.0
            else:
                return 0.3
                
        except Exception as e:
            logging.error(f"希望適合度計算エラー: {e}")
            return 0.0
    
    def is_time_compatible(self, preferred_hours: str, shift_time: str) -> bool:
        """時間帯の適合性をチェック"""
        try:
            if 'フルタイム' in preferred_hours:
                return True
            elif '午前' in preferred_hours and '09:00' in shift_time:
                return True
            elif '午後' in preferred_hours and ('13:00' in shift_time or '17:00' in shift_time):
                return True
            elif '夕方' in preferred_hours and '17:00' in shift_time:
                return True
            elif '土日' in preferred_hours:
                # 実際の日付チェックが必要
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"時間適合性チェックエラー: {e}")
            return False
    
    def get_staff_info(self, staff_id: str) -> Optional[Dict]:
        """スタッフ情報を取得"""
        if self.data_manager:
            return self.data_manager.get_staff_by_id(staff_id)
        else:
            # サンプルデータ
            sample_staff = {
                'EMP001': {'従業員ID': 'EMP001', '氏名': '田中太郎', '部門': '営業部', '役職': 'スタッフ', 'スキルレベル': 3, '雇用形態': '正社員', '入社日': '2023-04-01', '希望勤務時間': 'フルタイム'},
                'EMP002': {'従業員ID': 'EMP002', '氏名': '佐藤花子', '部門': '営業部', '役職': 'リーダー', 'スキルレベル': 5, '雇用形態': '正社員', '入社日': '2022-01-15', '希望勤務時間': 'フルタイム'},
            }
            return sample_staff.get(staff_id)
    
    def get_available_staff(self, absence_date: str, shift_time: str) -> List[Dict]:
        """利用可能なスタッフリストを取得"""
        if self.data_manager:
            return self.data_manager.get_staff_list()
        else:
            # サンプルデータ
            return [
                {'従業員ID': 'EMP001', '氏名': '田中太郎', '部門': '営業部', '役職': 'スタッフ', 'スキルレベル': 3, '雇用形態': '正社員', '入社日': '2023-04-01', '希望勤務時間': 'フルタイム'},
                {'従業員ID': 'EMP002', '氏名': '佐藤花子', '部門': '営業部', '役職': 'リーダー', 'スキルレベル': 5, '雇用形態': '正社員', '入社日': '2022-01-15', '希望勤務時間': 'フルタイム'},
                {'従業員ID': 'EMP003', '氏名': '鈴木次郎', '部門': '総務部', '役職': 'スタッフ', 'スキルレベル': 2, '雇用形態': 'パート', '入社日': '2023-06-01', '希望勤務時間': '午前のみ'},
                {'従業員ID': 'EMP004', '氏名': '山田美咲', '部門': '営業部', '役職': 'スタッフ', 'スキルレベル': 4, '雇用形態': 'パート', '入社日': '2023-03-01', '希望勤務時間': '夕方以降'},
                {'従業員ID': 'EMP005', '氏名': '高橋健太', '部門': '営業部', '役職': 'スタッフ', 'スキルレベル': 1, '雇用形態': 'アルバイト', '入社日': '2023-07-01', '希望勤務時間': '土日のみ'}
            ]
    
    def get_score_details(self, absent_staff: Dict, candidate_staff: Dict) -> Dict:
        """スコア詳細を取得"""
        return {
            'skill_compatibility': self.calculate_skill_compatibility(absent_staff, candidate_staff),
            'availability': self.calculate_availability_score(candidate_staff, '', ''),
            'experience': self.calculate_experience_score(candidate_staff),
            'preference': self.calculate_preference_score(candidate_staff, '', '')
        }
    
    def generate_recommendation_reason(self, absent_staff: Dict, candidate_staff: Dict, score: float) -> str:
        """推薦理由を生成"""
        reasons = []
        
        # 部門一致
        if absent_staff.get('部門') == candidate_staff.get('部門'):
            reasons.append("同部門")
        
        # スキルレベル
        candidate_skill = int(candidate_staff.get('スキルレベル', 1))
        if candidate_skill >= 4:
            reasons.append("高スキル")
        elif candidate_skill >= 3:
            reasons.append("標準スキル")
        
        # 雇用形態
        if candidate_staff.get('雇用形態') == '正社員':
            reasons.append("正社員")
        
        # 勤務可能性
        if 'フルタイム' in candidate_staff.get('希望勤務時間', ''):
            reasons.append("フルタイム対応可")
        
        if score >= 90:
            reasons.append("最適候補")
        elif score >= 80:
            reasons.append("適合候補")
        elif score >= 70:
            reasons.append("対応可能")
        else:
            reasons.append("要調整")
        
        return "・".join(reasons)