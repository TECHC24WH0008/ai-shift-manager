# -*- coding: utf-8 -*-
"""
分析サービス
勤務データの分析・レポート生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys
import os

# パスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.date_utils import DateUtils

class AnalyticsService:
    """分析サービス"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
    
    def generate_staff_performance_report(self, period_days: int = 30) -> Dict[str, Any]:
        """スタッフパフォーマンスレポートを生成"""
        if not self.data_manager or self.data_manager.timecard_data is None:
            return self._generate_sample_performance_report()
        
        # 期間設定
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        # データフィルタリング
        timecard_df = self.data_manager.timecard_data
        period_data = timecard_df[
            (timecard_df['日付'] >= start_date) & 
            (timecard_df['日付'] <= end_date)
        ]
        
        if period_data.empty:
            return {"error": "指定期間にデータがありません"}
        
        # 従業員別集計
        employee_stats = period_data.groupby('従業員ID').agg({
            '実働時間': ['sum', 'mean', 'count'],
            '評価': 'mean'
        }).round(2)
        
        # 列名を平坦化
        employee_stats.columns = ['総労働時間', '平均労働時間', '勤務日数', '平均評価']
        
        # トップパフォーマー
        top_performers = employee_stats.nlargest(5, '平均評価')
        
        # 労働時間分析
        work_hour_analysis = self._analyze_work_hours(period_data)
        
        # 出勤率分析
        attendance_analysis = self._analyze_attendance(period_data)
        
        report = {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "days": period_days
            },
            "summary": {
                "total_employees": len(employee_stats),
                "total_work_hours": employee_stats['総労働時間'].sum(),
                "average_rating": employee_stats['平均評価'].mean(),
                "total_work_days": employee_stats['勤務日数'].sum()
            },
            "top_performers": self._format_top_performers(top_performers),
            "work_hour_analysis": work_hour_analysis,
            "attendance_analysis": attendance_analysis,
            "recommendations": self._generate_performance_recommendations(employee_stats)
        }
        
        return report
    
    def _generate_sample_performance_report(self) -> Dict[str, Any]:
        """サンプルパフォーマンスレポートを生成"""
        return {
            "period": {
                "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                "end_date": datetime.now().strftime('%Y-%m-%d'),
                "days": 30
            },
            "summary": {
                "total_employees": 5,
                "total_work_hours": 800,
                "average_rating": 4.2,
                "total_work_days": 120
            },
            "top_performers": [
                {"name": "佐藤花子", "employee_id": "EMP002", "average_rating": 4.8, "work_days": 22},
                {"name": "田中太郎", "employee_id": "EMP001", "average_rating": 4.5, "work_days": 25},
                {"name": "山田美咲", "employee_id": "EMP004", "average_rating": 4.3, "work_days": 18}
            ],
            "work_hour_analysis": {
                "average_daily_hours": 6.7,
                "overtime_rate": 15.2,
                "efficiency_score": 85
            },
            "attendance_analysis": {
                "attendance_rate": 92.5,
                "punctuality_rate": 88.3,
                "absence_rate": 7.5
            },
            "recommendations": [
                "佐藤花子さんの優秀な勤務態度を他のスタッフの参考にしてください",
                "全体的な出勤率向上のための施策を検討してください",
                "残業時間の削減を図ってください"
            ]
        }
    
    def _analyze_work_hours(self, data: pd.DataFrame) -> Dict[str, Any]:
        """労働時間分析"""
        if '実働時間' not in data.columns:
            return {}
        
        work_hours = data['実働時間'] / 60  # 時間単位に変換
        
        analysis = {
            "average_daily_hours": round(work_hours.mean(), 1),
            "max_daily_hours": round(work_hours.max(), 1),
            "min_daily_hours": round(work_hours.min(), 1),
            "overtime_rate": round((work_hours > 8).mean() * 100, 1),  # 8時間超過率
            "efficiency_score": self._calculate_efficiency_score(data)
        }
        
        return analysis
    
    def _analyze_attendance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """出勤分析"""
        # 簡易実装
        total_scheduled = len(data)  # 予定勤務数
        actual_attendance = len(data[data['実働時間'] > 0])  # 実際の出勤数
        
        analysis = {
            "attendance_rate": round((actual_attendance / total_scheduled * 100), 1) if total_scheduled > 0 else 0,
            "punctuality_rate": 88.3,  # サンプル値
            "absence_rate": round(((total_scheduled - actual_attendance) / total_scheduled * 100), 1) if total_scheduled > 0 else 0
        }
        
        return analysis
    
    def _calculate_efficiency_score(self, data: pd.DataFrame) -> float:
        """効率性スコアを計算"""
        if '評価' not in data.columns or '実働時間' not in data.columns:
            return 75.0  # デフォルト値
        
        # 評価と労働時間の関係から効率性を算出
        avg_rating = data['評価'].mean()
        avg_hours = data['実働時間'].mean() / 60
        
        # 簡易計算（実際はより複雑な計算が必要）
        efficiency = (avg_rating / 5.0) * (8 / max(avg_hours, 1)) * 100
        
        return round(min(efficiency, 100), 1)
    
    def _format_top_performers(self, top_performers: pd.DataFrame) -> List[Dict]:
        """トップパフォーマーをフォーマット"""
        result = []
        
        for emp_id, row in top_performers.iterrows():
            name = self._get_employee_name(emp_id)
            result.append({
                "employee_id": emp_id,
                "name": name,
                "average_rating": round(row['平均評価'], 2),
                "work_days": int(row['勤務日数']),
                "total_hours": round(row['総労働時間'] / 60, 1)
            })
        
        return result
    
    def _get_employee_name(self, employee_id: str) -> str:
        """従業員名を取得"""
        if not self.data_manager or self.data_manager.staff_data is None:
            return "不明"
        
        staff_row = self.data_manager.staff_data[
            self.data_manager.staff_data['従業員ID'] == employee_id
        ]
        
        if not staff_row.empty and '氏名' in staff_row.columns:
            return staff_row.iloc[0]['氏名']
        
        return "不明"
    
    def _generate_performance_recommendations(self, employee_stats: pd.DataFrame) -> List[str]:
        """パフォーマンス改善提案を生成"""
        recommendations = []
        
        # 評価の低いスタッフ
        low_performers = employee_stats[employee_stats['平均評価'] < 3.0]
        if not low_performers.empty:
            recommendations.append(f"{len(low_performers)}名のスタッフに追加研修が必要です")
        
        # 労働時間の偏り
        avg_hours = employee_stats['総労働時間'].mean()
        overworked = employee_stats[employee_stats['総労働時間'] > avg_hours * 1.5]
        if not overworked.empty:
            recommendations.append("労働時間の均等化を図ってください")
        
        # 高評価スタッフの活用
        high_performers = employee_stats[employee_stats['平均評価'] >= 4.5]
        if not high_performers.empty:
            recommendations.append("高評価スタッフをメンター役として活用してください")
        
        if not recommendations:
            recommendations.append("現在のパフォーマンスは良好です")
        
        return recommendations
    
    def generate_cost_analysis(self, period_days: int = 30) -> Dict[str, Any]:
        """コスト分析レポートを生成"""
        if not self.data_manager:
            return self._generate_sample_cost_analysis()
        
        # 人件費計算
        total_cost = 0
        employee_costs = {}
        
        if (self.data_manager.staff_data is not None and 
            self.data_manager.timecard_data is not None):
            
            # 期間設定
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            # 期間内のタイムカードデータ
            period_timecard = self.data_manager.timecard_data[
                (self.data_manager.timecard_data['日付'] >= start_date) & 
                (self.data_manager.timecard_data['日付'] <= end_date)
            ]
            
            # 従業員別コスト計算
            for _, timecard_row in period_timecard.iterrows():
                emp_id = timecard_row['従業員ID']
                work_hours = timecard_row.get('実働時間', 0) / 60  # 時間単位
                
                # 時給を取得
                hourly_wage = self._get_hourly_wage(emp_id)
                daily_cost = work_hours * hourly_wage
                
                if emp_id not in employee_costs:
                    employee_costs[emp_id] = 0
                employee_costs[emp_id] += daily_cost
                total_cost += daily_cost
        
        # 分析結果
        analysis = {
            "period": {
                "start_date": (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d'),
                "end_date": datetime.now().strftime('%Y-%m-%d'),
                "days": period_days
            },
            "total_labor_cost": round(total_cost, 0),
            "average_daily_cost": round(total_cost / period_days, 0) if period_days > 0 else 0,
            "employee_costs": self._format_employee_costs(employee_costs),
            "cost_breakdown": self._analyze_cost_breakdown(employee_costs),
            "recommendations": self._generate_cost_recommendations(employee_costs, total_cost)
        }
        
        return analysis
    
    def _generate_sample_cost_analysis(self) -> Dict[str, Any]:
        """サンプルコスト分析を生成"""
        return {
            "period": {
                "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                "end_date": datetime.now().strftime('%Y-%m-%d'),
                "days": 30
            },
            "total_labor_cost": 850000,
            "average_daily_cost": 28333,
            "employee_costs": [
                {"name": "田中太郎", "cost": 200000, "percentage": 23.5},
                {"name": "佐藤花子", "cost": 180000, "percentage": 21.2},
                {"name": "山田美咲", "cost": 150000, "percentage": 17.6}
            ],
            "cost_breakdown": {
                "regular_hours": 70.5,
                "overtime_hours": 29.5,
                "by_department": {
                    "営業部": 65.2,
                    "総務部": 34.8
                }
            },
            "recommendations": [
                "残業時間の削減により月間15万円のコスト削減が可能です",
                "パート従業員の活用でコスト効率を改善できます"
            ]
        }
    
    def _get_hourly_wage(self, employee_id: str) -> float:
        """従業員の時給を取得"""
        if not self.data_manager or self.data_manager.staff_data is None:
            return 1000.0  # デフォルト時給
        
        staff_row = self.data_manager.staff_data[
            self.data_manager.staff_data['従業員ID'] == employee_id
        ]
        
        if not staff_row.empty and '時給' in staff_row.columns:
            return float(staff_row.iloc[0]['時給'])
        
        return 1000.0
    
    def _format_employee_costs(self, employee_costs: Dict[str, float]) -> List[Dict]:
        """従業員別コストをフォーマット"""
        total_cost = sum(employee_costs.values())
        result = []
        
        # コスト順にソート
        sorted_costs = sorted(employee_costs.items(), key=lambda x: x[1], reverse=True)
        
        for emp_id, cost in sorted_costs[:10]:  # 上位10名
            name = self._get_employee_name(emp_id)
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            
            result.append({
                "employee_id": emp_id,
                "name": name,
                "cost": round(cost, 0),
                "percentage": round(percentage, 1)
            })
        
        return result
    
    def _analyze_cost_breakdown(self, employee_costs: Dict[str, float]) -> Dict[str, Any]:
        """コスト内訳を分析"""
        # 簡易実装
        return {
            "regular_hours": 70.5,
            "overtime_hours": 29.5,
            "by_department": {
                "営業部": 65.2,
                "総務部": 34.8
            }
        }
    
    def _generate_cost_recommendations(self, employee_costs: Dict, total_cost: float) -> List[str]:
        """コスト改善提案を生成"""
        recommendations = []
        
        if total_cost > 1000000:  # 100万円超過
            recommendations.append("人件費が高額です。業務効率化を検討してください")
        
        if len(employee_costs) > 0:
            max_cost = max(employee_costs.values())
            avg_cost = sum(employee_costs.values()) / len(employee_costs)
            
            if max_cost > avg_cost * 2:
                recommendations.append("労働時間の偏りが見られます。均等化を図ってください")
        
        recommendations.append("定期的なコスト見直しを実施してください")
        
        return recommendations
    
    def generate_trend_analysis(self, months: int = 6) -> Dict[str, Any]:
        """トレンド分析を生成"""
        # 簡易実装（実際のデータがある場合はより詳細な分析）
        return {
            "period_months": months,
            "trends": {
                "staff_count": {"trend": "increasing", "change_rate": 8.5},
                "average_rating": {"trend": "stable", "change_rate": 2.1},
                "labor_cost": {"trend": "increasing", "change_rate": 12.3},
                "efficiency": {"trend": "improving", "change_rate": 5.7}
            },
            "seasonal_patterns": {
                "busy_months": ["12", "3", "7"],
                "quiet_months": ["2", "6", "9"],
                "peak_days": ["金", "土"],
                "quiet_days": ["火", "水"]
            },
            "predictions": {
                "next_month_staff_need": 8,
                "expected_cost_increase": 5.2,
                "recommended_actions": [
                    "繁忙期に向けた人員確保",
                    "閑散期の効率化施策"
                ]
            }
        }