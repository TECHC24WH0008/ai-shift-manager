# -*- coding: utf-8 -*-
"""
業界テンプレート管理モジュール
各業界に特化したシフト設定テンプレートを提供
"""

from typing import Dict, List, Any

class ShiftTemplates:
    """業界別テンプレート管理クラス"""
    
    @staticmethod
    def get_templates() -> Dict[str, Any]:
        """利用可能なテンプレート一覧を取得"""
        return {
            "restaurant": {
                "name": "🍽️ 飲食店",
                "description": "レストラン・カフェ・居酒屋向け",
                "time_slots": [
                    {"name": "モーニング", "start": "07:00", "end": "11:00"},
                    {"name": "ランチ", "start": "11:00", "end": "15:00"},
                    {"name": "ディナー", "start": "17:00", "end": "22:00"},
                    {"name": "深夜", "start": "22:00", "end": "02:00"}
                ],
                "roles": [
                    {"name": "ホールスタッフ", "priority": 1},
                    {"name": "キッチンスタッフ", "priority": 1},
                    {"name": "店長・副店長", "priority": 2}
                ],
                "min_staff": {"平日": 2, "土日": 3},
                "special_rules": [
                    "深夜割増対応",
                    "アルコール販売資格確認",
                    "ピーク時間帯の増員",
                    "食品衛生管理者配置"
                ],
                "industry_knowledge": {
                    "peak_hours": ["11:30-14:00", "18:00-21:00"],
                    "critical_skills": ["接客", "POS操作", "食品衛生"],
                    "legal_requirements": ["アルコール販売", "深夜営業許可"]
                }
            },
            
            "retail": {
                "name": "🛍️ 小売店",
                "description": "コンビニ・スーパー・アパレル向け",
                "time_slots": [
                    {"name": "開店準備", "start": "08:30", "end": "10:00"},
                    {"name": "午前", "start": "10:00", "end": "13:00"},
                    {"name": "午後", "start": "13:00", "end": "17:00"},
                    {"name": "夕方", "start": "17:00", "end": "20:00"}
                ],
                "roles": [
                    {"name": "レジ担当", "priority": 1},
                    {"name": "売場担当", "priority": 1},
                    {"name": "責任者", "priority": 2}
                ],
                "min_staff": {"平日": 2, "土日": 4},
                "special_rules": [
                    "棚卸し対応",
                    "セール時増員",
                    "発注業務対応",
                    "防犯対策"
                ],
                "industry_knowledge": {
                    "peak_hours": ["12:00-13:00", "17:00-19:00"],
                    "critical_skills": ["レジ操作", "商品知識", "接客"],
                    "legal_requirements": ["労働基準法遵守", "商品管理"]
                }
            },
            
            "office": {
                "name": "🏢 事務所",
                "description": "オフィス・受付・コールセンター向け",
                "time_slots": [
                    {"name": "午前", "start": "09:00", "end": "12:00"},
                    {"name": "午後", "start": "13:00", "end": "17:00"},
                    {"name": "残業", "start": "17:00", "end": "20:00"}
                ],
                "roles": [
                    {"name": "受付スタッフ", "priority": 1},
                    {"name": "事務スタッフ", "priority": 1},
                    {"name": "管理者", "priority": 2}
                ],
                "min_staff": {"平日": 1, "土日": 1},
                "special_rules": [
                    "電話対応必須",
                    "来客対応",
                    "残業時間管理",
                    "セキュリティ管理"
                ],
                "industry_knowledge": {
                    "peak_hours": ["09:00-10:00", "14:00-16:00"],
                    "critical_skills": ["PC操作", "電話対応", "文書作成"],
                    "legal_requirements": ["労働時間管理", "個人情報保護"]
                }
            },
            
            "healthcare": {
                "name": "🏥 医療・介護",
                "description": "病院・クリニック・介護施設向け",
                "time_slots": [
                    {"name": "早番", "start": "07:00", "end": "15:00"},
                    {"name": "日勤", "start": "09:00", "end": "17:00"},
                    {"name": "遅番", "start": "13:00", "end": "21:00"},
                    {"name": "夜勤", "start": "21:00", "end": "07:00"}
                ],
                "roles": [
                    {"name": "看護師", "priority": 3},
                    {"name": "介護士", "priority": 2},
                    {"name": "事務スタッフ", "priority": 1}
                ],
                "min_staff": {"平日": 3, "土日": 2},
                "special_rules": [
                    "24時間体制",
                    "資格者必須配置",
                    "夜勤明け休み",
                    "緊急時対応体制"
                ],
                "industry_knowledge": {
                    "peak_hours": ["08:00-10:00", "16:00-18:00"],
                    "critical_skills": ["医療知識", "緊急対応", "コミュニケーション"],
                    "legal_requirements": ["医療法遵守", "労働基準法特例"]
                }
            },
            
            "education": {
                "name": "🎓 教育機関",
                "description": "学校・塾・保育園向け",
                "time_slots": [
                    {"name": "早朝", "start": "07:30", "end": "09:00"},
                    {"name": "午前授業", "start": "09:00", "end": "12:00"},
                    {"name": "午後授業", "start": "13:00", "end": "16:00"},
                    {"name": "放課後", "start": "16:00", "end": "18:00"}
                ],
                "roles": [
                    {"name": "教員", "priority": 3},
                    {"name": "事務スタッフ", "priority": 2},
                    {"name": "サポートスタッフ", "priority": 1}
                ],
                "min_staff": {"平日": 2, "土日": 1},
                "special_rules": [
                    "授業時間厳守",
                    "安全管理体制",
                    "保護者対応",
                    "行事対応"
                ],
                "industry_knowledge": {
                    "peak_hours": ["08:00-09:00", "15:00-16:00"],
                    "critical_skills": ["教育スキル", "安全管理", "コミュニケーション"],
                    "legal_requirements": ["教育法遵守", "児童保護"]
                }
            },
            
            "custom": {
                "name": "⚙️ カスタム設定",
                "description": "独自の設定で開始",
                "time_slots": [
                    {"name": "午前", "start": "09:00", "end": "12:00"},
                    {"name": "午後", "start": "13:00", "end": "17:00"}
                ],
                "roles": [
                    {"name": "スタッフ", "priority": 1},
                    {"name": "責任者", "priority": 2}
                ],
                "min_staff": {"平日": 1, "土日": 1},
                "special_rules": [],
                "industry_knowledge": {
                    "peak_hours": [],
                    "critical_skills": [],
                    "legal_requirements": []
                }
            }
        }
    
    @staticmethod
    def get_template(template_id: str) -> Dict[str, Any]:
        """指定されたテンプレートを取得"""
        templates = ShiftTemplates.get_templates()
        return templates.get(template_id, templates["custom"])
    
    @staticmethod
    def get_all_templates() -> Dict[str, Any]:
        """全テンプレート一覧を取得（get_templatesのエイリアス）"""
        return ShiftTemplates.get_templates()
    
    @staticmethod
    def get_template_names() -> List[str]:
        """テンプレート名一覧を取得"""
        templates = ShiftTemplates.get_templates()
        return [template["name"] for template in templates.values()]
    
    @staticmethod
    def create_custom_template(name: str, time_slots: List[Dict], 
                             roles: List[Dict], min_staff: Dict,
                             special_rules: List[str] = None) -> Dict[str, Any]:
        """カスタムテンプレートを作成"""
        return {
            "name": name,
            "description": "カスタム設定",
            "time_slots": time_slots,
            "roles": roles,
            "min_staff": min_staff,
            "special_rules": special_rules or [],
            "industry_knowledge": {
                "peak_hours": [],
                "critical_skills": [],
                "legal_requirements": []
            }
        }
    
    @staticmethod
    def validate_template(template: Dict[str, Any]) -> tuple[bool, str]:
        """テンプレートの妥当性を検証"""
        required_keys = ["name", "time_slots", "roles", "min_staff"]
        
        for key in required_keys:
            if key not in template:
                return False, f"必須キー '{key}' が不足しています"
        
        # 時間帯の検証
        if not template["time_slots"]:
            return False, "時間帯が設定されていません"
        
        for slot in template["time_slots"]:
            if not all(k in slot for k in ["name", "start", "end"]):
                return False, "時間帯の設定が不完全です"
        
        # 役職の検証
        if not template["roles"]:
            return False, "役職が設定されていません"
        
        # 最小人数の検証
        if not isinstance(template["min_staff"], dict):
            return False, "最小人数の設定が不正です"
        
        return True, "テンプレートは有効です"