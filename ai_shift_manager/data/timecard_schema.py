# -*- coding: utf-8 -*-
"""
タイムカードスキーマ定義
様々なタイムカード形式に対応するためのデータ構造
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, Dict, List, Any
from enum import Enum

class TimecardImportance(Enum):
    """データの重要度"""
    CRITICAL = "必須"      # AI分析に絶対必要
    HIGH = "重要"         # 分析精度向上に重要
    MEDIUM = "有用"       # あると便利
    LOW = "参考"          # 参考程度

@dataclass
class TimecardField:
    """タイムカードフィールド定義"""
    field_name: str
    japanese_name: str
    data_type: type
    importance: TimecardImportance
    description: str
    example_values: List[str]
    ai_usage: str  # AI分析での使用目的

class TimecardSchema:
    """タイムカードスキーマ定義クラス"""
    
    def __init__(self):
        self.fields = self._define_fields()
    
    def _define_fields(self) -> Dict[str, TimecardField]:
        """フィールド定義"""
        return {
            # === 🔥 CRITICAL: AI分析に絶対必要 ===
            'work_date': TimecardField(
                field_name='work_date',
                japanese_name='勤務日',
                data_type=datetime,
                importance=TimecardImportance.CRITICAL,
                description='勤務した日付',
                example_values=['2024-01-15', '2024/01/15', '1/15'],
                ai_usage='代替要員の勤務パターン分析、直近経験の計算'
            ),
            
            'staff_id': TimecardField(
                field_name='staff_id',
                japanese_name='従業員ID',
                data_type=str,
                importance=TimecardImportance.CRITICAL,
                description='従業員を一意に識別するID',
                example_values=['EMP001', '001', 'T001'],
                ai_usage='個人の勤務履歴追跡、代替候補特定'
            ),
            
            'staff_name': TimecardField(
                field_name='staff_name',
                japanese_name='氏名',
                data_type=str,
                importance=TimecardImportance.CRITICAL,
                description='従業員の氏名',
                example_values=['田中太郎', '佐藤花子'],
                ai_usage='ユーザーへの表示、確認用'
            ),
            
            'department': TimecardField(
                field_name='department',
                japanese_name='部門',
                data_type=str,
                importance=TimecardImportance.CRITICAL,
                description='勤務部門・セクション',
                example_values=['営業部', 'レジ', 'キッチン', '事務'],
                ai_usage='部門経験度計算、同部門代替要員の優先選出'
            ),
            
            # === ⚡ HIGH: 分析精度向上に重要 ===
            'clock_in_time': TimecardField(
                field_name='clock_in_time',
                japanese_name='出勤時間',
                data_type=time,
                importance=TimecardImportance.HIGH,
                description='実際の出勤時刻',
                example_values=['09:00', '9:00', '0900'],
                ai_usage='遅刻率計算、信頼性スコア算出'
            ),
            
            'clock_out_time': TimecardField(
                field_name='clock_out_time',
                japanese_name='退勤時間',
                data_type=time,
                importance=TimecardImportance.HIGH,
                description='実際の退勤時刻',
                example_values=['17:00', '18:30', '1800'],
                ai_usage='勤務時間パターン分析、疲労度推定'
            ),
            
            'scheduled_start': TimecardField(
                field_name='scheduled_start',
                japanese_name='予定開始時間',
                data_type=time,
                importance=TimecardImportance.HIGH,
                description='シフト予定の開始時刻',
                example_values=['09:00', '10:00'],
                ai_usage='遅刻率計算、時間厳守度評価'
            ),
            
            'work_minutes': TimecardField(
                field_name='work_minutes',
                japanese_name='実働時間',
                data_type=int,
                importance=TimecardImportance.HIGH,
                description='実際の労働時間（分）',
                example_values=['480', '420', '360'],
                ai_usage='労働負荷分析、疲労度推定'
            ),
            
            'position': TimecardField(
                field_name='position',
                japanese_name='役職・ポジション',
                data_type=str,
                importance=TimecardImportance.HIGH,
                description='その日の役職・担当ポジション',
                example_values=['リーダー', 'スタッフ', '新人'],
                ai_usage='責任レベル評価、代替可能性判定'
            ),
            
            # === 📊 MEDIUM: あると便利 ===
            'break_minutes': TimecardField(
                field_name='break_minutes',
                japanese_name='休憩時間',
                data_type=int,
                importance=TimecardImportance.MEDIUM,
                description='休憩時間（分）',
                example_values=['60', '45', '30'],
                ai_usage='実働時間の正確な計算'
            ),
            
            'overtime_minutes': TimecardField(
                field_name='overtime_minutes',
                japanese_name='残業時間',
                data_type=int,
                importance=TimecardImportance.MEDIUM,
                description='残業時間（分）',
                example_values=['60', '120', '0'],
                ai_usage='労働負荷分析、疲労度推定'
            ),
            
            'work_content': TimecardField(
                field_name='work_content',
                japanese_name='業務内容',
                data_type=str,
                importance=TimecardImportance.MEDIUM,
                description='その日の主な業務内容',
                example_values=['接客', 'レジ', '調理', '清掃'],
                ai_usage='業務経験度評価、スキルマッチング'
            ),
            
            'performance_rating': TimecardField(
                field_name='performance_rating',
                japanese_name='評価・パフォーマンス',
                data_type=float,
                importance=TimecardImportance.MEDIUM,
                description='その日のパフォーマンス評価',
                example_values=['4.5', '3.8', '5.0'],
                ai_usage='信頼性スコア、代替要員優先度'
            ),
            
            'location': TimecardField(
                field_name='location',
                japanese_name='勤務場所',
                data_type=str,
                importance=TimecardImportance.MEDIUM,
                description='勤務した場所・店舗',
                example_values=['本店', '支店A', '2階フロア'],
                ai_usage='場所慣れ度評価、地理的制約考慮'
            ),
            
            # === 📝 LOW: 参考程度 ===
            'attendance_status': TimecardField(
                field_name='attendance_status',
                japanese_name='出勤状況',
                data_type=str,
                importance=TimecardImportance.LOW,
                description='出勤・欠勤・遅刻等の状況',
                example_values=['出勤', '遅刻', '早退', '欠勤'],
                ai_usage='出勤パターン分析'
            ),
            
            'notes': TimecardField(
                field_name='notes',
                japanese_name='備考',
                data_type=str,
                importance=TimecardImportance.LOW,
                description='特記事項・メモ',
                example_values=['体調不良', '研修参加', ''],
                ai_usage='特殊事情の考慮'
            ),
            
            'approver': TimecardField(
                field_name='approver',
                japanese_name='承認者',
                data_type=str,
                importance=TimecardImportance.LOW,
                description='タイムカード承認者',
                example_values=['山田課長', '佐藤主任'],
                ai_usage='承認パターン分析（将来的）'
            ),
            
            'created_at': TimecardField(
                field_name='created_at',
                japanese_name='記録日時',
                data_type=datetime,
                importance=TimecardImportance.LOW,
                description='タイムカード記録日時',
                example_values=['2024-01-15 17:05:00'],
                ai_usage='記録タイミング分析'
            )
        }
    
    def get_critical_fields(self) -> List[str]:
        """必須フィールド一覧"""
        return [name for name, field in self.fields.items() 
                if field.importance == TimecardImportance.CRITICAL]
    
    def get_ai_essential_fields(self) -> List[str]:
        """AI分析に重要なフィールド一覧"""
        return [name for name, field in self.fields.items() 
                if field.importance in [TimecardImportance.CRITICAL, TimecardImportance.HIGH]]
    
    def get_field_mapping_suggestions(self) -> Dict[str, List[str]]:
        """よくある列名のマッピング候補"""
        return {
            'work_date': [
                '日付', '勤務日', '出勤日', '年月日', 'Date', '日', 
                'work_date', 'date', '勤務年月日'
            ],
            'staff_id': [
                '従業員ID', '社員ID', 'ID', '従業員番号', '社員番号',
                'staff_id', 'employee_id', 'emp_id', '番号'
            ],
            'staff_name': [
                '氏名', '名前', '従業員名', '社員名', 'Name',
                'staff_name', 'employee_name', '姓名'
            ],
            'department': [
                '部門', '部署', '所属', 'Department', 'Dept',
                'section', 'セクション', '課', '係'
            ],
            'clock_in_time': [
                '出勤時間', '開始時間', '出社時間', 'Clock In',
                'start_time', '始業時間', '出勤'
            ],
            'clock_out_time': [
                '退勤時間', '終了時間', '退社時間', 'Clock Out',
                'end_time', '終業時間', '退勤'
            ],
            'work_minutes': [
                '実働時間', '労働時間', '勤務時間', 'Work Hours',
                'actual_hours', '実労働時間'
            ],
            'break_minutes': [
                '休憩時間', '休憩', 'Break Time', 'break',
                '休憩分', '昼休み'
            ]
        }
    
    def validate_timecard_data(self, df_columns: List[str]) -> Dict[str, Any]:
        """タイムカードデータの妥当性チェック"""
        critical_fields = self.get_critical_fields()
        mapping_suggestions = self.get_field_mapping_suggestions()
        
        # 必須フィールドの存在チェック
        missing_critical = []
        found_mappings = {}
        
        for critical_field in critical_fields:
            found = False
            for col in df_columns:
                if col in mapping_suggestions.get(critical_field, []):
                    found_mappings[critical_field] = col
                    found = True
                    break
            
            if not found:
                missing_critical.append(critical_field)
        
        # データ品質評価
        quality_score = len(found_mappings) / len(critical_fields) * 100
        
        return {
            'is_valid': len(missing_critical) == 0,
            'quality_score': quality_score,
            'missing_critical_fields': missing_critical,
            'found_mappings': found_mappings,
            'suggestions': self._generate_improvement_suggestions(missing_critical, df_columns)
        }
    
    def _generate_improvement_suggestions(self, missing_fields: List[str], 
                                        available_columns: List[str]) -> List[str]:
        """改善提案生成"""
        suggestions = []
        
        if 'department' in missing_fields:
            suggestions.append("🏢 部門情報があると代替要員の精度が大幅に向上します")
        
        if 'clock_in_time' in missing_fields:
            suggestions.append("⏰ 出勤時間があると信頼性スコアを計算できます")
        
        if len(missing_fields) > 2:
            suggestions.append("📊 より多くの情報があると、AI分析の精度が向上します")
        
        return suggestions

# 使用例とサンプルデータ
class TimecardSamples:
    """タイムカードサンプルデータ"""
    
    @staticmethod
    def get_minimal_sample() -> str:
        """最小限のサンプル"""
        return """日付,従業員ID,氏名,部門
2024-01-15,EMP001,田中太郎,営業部
2024-01-15,EMP002,佐藤花子,総務部
2024-01-16,EMP001,田中太郎,営業部"""
    
    @staticmethod
    def get_standard_sample() -> str:
        """標準的なサンプル"""
        return """日付,従業員ID,氏名,部門,出勤時間,退勤時間,休憩時間,実働時間
2024-01-15,EMP001,田中太郎,営業部,09:00,17:00,60,480
2024-01-15,EMP002,佐藤花子,総務部,10:00,18:00,60,420
2024-01-16,EMP001,田中太郎,営業部,09:05,17:00,60,475"""
    
    @staticmethod
    def get_detailed_sample() -> str:
        """詳細なサンプル"""
        return """日付,従業員ID,氏名,部門,役職,出勤時間,退勤時間,休憩時間,実働時間,業務内容,評価,勤務場所
2024-01-15,EMP001,田中太郎,営業部,スタッフ,09:00,17:00,60,480,接客・レジ,4.5,本店
2024-01-15,EMP002,佐藤花子,総務部,リーダー,10:00,18:00,60,420,事務・指導,5.0,本社
2024-01-16,EMP001,田中太郎,営業部,スタッフ,09:05,17:00,60,475,接客・清掃,4.2,本店"""