# -*- coding: utf-8 -*-
"""
永続化ストレージ管理
スタッフ情報、希望シフト、設定の自動保存・復元
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

class PersistentStorage:
    """データの永続化管理クラス"""
    
    def __init__(self):
        self.data_dir = "persistent_data"
        self.ensure_data_directory()
        
        # ファイルパス
        self.staff_file = os.path.join(self.data_dir, "staff_master.json")
        self.shift_preferences_file = os.path.join(self.data_dir, "shift_preferences.json")
        self.templates_file = os.path.join(self.data_dir, "input_templates.json")
        self.settings_file = os.path.join(self.data_dir, "user_settings.json")
        
    def ensure_data_directory(self):
        """データディレクトリの作成"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    # スタッフ情報の永続化
    def save_staff_data(self, staff_data: List[Dict]) -> bool:
        """スタッフ情報を保存"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "staff_count": len(staff_data),
                "staff_list": staff_data
            }
            with open(self.staff_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"スタッフデータ保存エラー: {e}")
            return False
    
    def load_staff_data(self) -> List[Dict]:
        """スタッフ情報を読み込み"""
        try:
            if os.path.exists(self.staff_file):
                with open(self.staff_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("staff_list", [])
            return []
        except Exception as e:
            logging.error(f"スタッフデータ読み込みエラー: {e}")
            return []
    
    # 希望シフトの永続化
    def save_shift_preferences(self, preferences: Dict[str, Any]) -> bool:
        """希望シフトを保存"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "preferences": preferences
            }
            with open(self.shift_preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"希望シフト保存エラー: {e}")
            return False
    
    def load_shift_preferences(self) -> Dict[str, Any]:
        """希望シフトを読み込み"""
        try:
            if os.path.exists(self.shift_preferences_file):
                with open(self.shift_preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("preferences", {})
            return {}
        except Exception as e:
            logging.error(f"希望シフト読み込みエラー: {e}")
            return {}
    
    # 入力テンプレートの管理
    def save_input_template(self, template_name: str, template_data: Dict) -> bool:
        """入力テンプレートを保存"""
        try:
            templates = self.load_input_templates()
            templates[template_name] = {
                "created": datetime.now().isoformat(),
                "data": template_data
            }
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"テンプレート保存エラー: {e}")
            return False
    
    def load_input_templates(self) -> Dict[str, Any]:
        """入力テンプレートを読み込み"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"テンプレート読み込みエラー: {e}")
            return {}
    
    # 自動バックアップ
    def create_backup(self) -> bool:
        """データの自動バックアップ"""
        try:
            backup_dir = os.path.join(self.data_dir, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
            
            backup_data = {
                "backup_time": datetime.now().isoformat(),
                "staff_data": self.load_staff_data(),
                "shift_preferences": self.load_shift_preferences(),
                "templates": self.load_input_templates()
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # 古いバックアップを削除（30日以上前）
            self.cleanup_old_backups(backup_dir)
            return True
            
        except Exception as e:
            logging.error(f"バックアップエラー: {e}")
            return False
    
    def cleanup_old_backups(self, backup_dir: str, days: int = 30):
        """古いバックアップファイルを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for filename in os.listdir(backup_dir):
                if filename.startswith("backup_") and filename.endswith(".json"):
                    file_path = os.path.join(backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        
        except Exception as e:
            logging.error(f"バックアップクリーンアップエラー: {e}")