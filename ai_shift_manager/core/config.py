# -*- coding: utf-8 -*-
"""
設定管理モジュール
アプリケーション全体の設定を管理
"""

import json
import os
from typing import Dict, Any

class Config:
    """アプリケーション設定管理"""
    
    def __init__(self, config_file="app_config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        self.config = self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "app": {
                "name": "AI Shift Manager",
                "version": "2.0",
                "window_size": "900x700",
                "theme": "modern"
            },
            "colors": {
                "primary": "#2563EB",
                "primary_dark": "#1D4ED8",
                "primary_darker": "#1E40AF",
                "secondary": "#10B981",
                "secondary_dark": "#059669",
                "secondary_darker": "#047857",
                "accent": "#F59E0B",
                "danger": "#EF4444",
                "danger_dark": "#DC2626",
                "danger_darker": "#B91C1C",
                "light": "#F8FAFC",
                "white": "#FFFFFF",
                "dark": "#1E293B",
                "gray": "#64748B",
                "gray_light": "#E2E8F0",
                "gray_lighter": "#F1F5F9"
            },
            "fonts": {
                "title": ("Segoe UI", 20, "bold"),
                "heading": ("Segoe UI", 14, "bold"),
                "body": ("Segoe UI", 10),
                "small": ("Segoe UI", 9)
            },
            "display_settings": {
                "staff_info": {
                    "show_salary": True,
                    "show_contact": False,
                    "show_personal_info": True,
                    "show_evaluation": True,
                    "show_skill_level": True,
                    "show_employment_type": True
                },
                "timecard": {
                    "show_detailed_time": True,
                    "show_break_time": True,
                    "show_evaluation": True,
                    "show_business_content": True,
                    "show_overtime": True
                },
                "shift_calendar": {
                    "show_staff_count": True,
                    "show_staff_names": True,
                    "show_time_slots": True,
                    "show_roles": True,
                    "show_workload": True
                }
            },
            "feature_settings": {
                "ai_features": {
                    "natural_language_generation": True,
                    "substitute_recommendation": True,
                    "workload_analysis": True,
                    "performance_prediction": True,
                    "auto_optimization": True
                },
                "privacy_features": {
                    "anonymize_names": False,
                    "hide_salary_info": False,
                    "mask_contact_info": True,
                    "encrypt_personal_data": True
                },
                "advanced_features": {
                    "voice_commands": False,
                    "ocr_processing": False,
                    "face_recognition": False,
                    "multi_language": False,
                    "mobile_sync": False
                }
            },
            "export_settings": {
                "include_personal_info": True,
                "include_salary_info": False,
                "include_evaluation": True,
                "export_format": "xlsx",
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M"
            },
            "business_hours": {
                "default_open": "09:00",
                "default_close": "18:00",
                "default_break_start": "12:00",
                "default_break_end": "13:00"
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """設定を読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    return self._merge_configs(self.default_config, loaded_config)
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """設定を保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定保存エラー: {e}")
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """設定をマージ"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, path: str, default=None):
        """ドット記法で設定値を取得"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any):
        """ドット記法で設定値を変更"""
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_colors(self) -> Dict[str, str]:
        """カラーパレットを取得"""
        return self.config.get("colors", {})
    
    def get_fonts(self) -> Dict[str, tuple]:
        """フォント設定を取得"""
        return self.config.get("fonts", {})
    
    def is_feature_enabled(self, category: str, feature: str) -> bool:
        """機能が有効かチェック"""
        return self.config.get("feature_settings", {}).get(category, {}).get(feature, False)
    
    def is_display_enabled(self, category: str, setting: str) -> bool:
        """表示設定が有効かチェック"""
        return self.config.get("display_settings", {}).get(category, {}).get(setting, True)

# グローバル設定インスタンス
app_config = Config()