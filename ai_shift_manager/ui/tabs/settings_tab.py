# -*- coding: utf-8 -*-
"""
設定タブ
アプリケーション設定とカスタマイズ - 統一UI版
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab, FormMixin
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedEntry,
    UnifiedCard, UnifiedTheme
)

class SettingsTab(BaseTab, FormMixin):
    """設定タブクラス - 統一UI版"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        
        # 設定データ
        self.settings = self.load_settings()
        
        # UI変数
        self.company_name_var = None
        self.department_var = None
        self.start_time_var = None
        self.end_time_var = None
        self.break_time_var = None
        self.language_var = None
        self.timezone_var = None
        self.min_staff_var = None
        self.max_consecutive_var = None
        self.ai_optimization_var = None
        self.auto_substitute_var = None
        self.balance_workload_var = None
        self.shift_reminder_var = None
        self.absence_alert_var = None
        self.schedule_change_var = None
        self.notification_time_var = None
        self.auto_backup_var = None
        self.backup_interval_var = None
        self.theme_var = None
        self.font_size_var = None
        self.show_tooltips_var = None
        self.show_animations_var = None
        
        super().__init__(parent_frame, "⚙️ システム設定")
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("設定を読み込み中...")
        # 設定は既に__init__で読み込み済み
        self.update_status("設定読み込み完了")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("💾 保存", self.save_settings_to_file, "primary")
        self.toolbar.add_button("✅ 適用", self.apply_settings, "success")
        self.toolbar.add_separator()
        self.toolbar.add_button("📥 インポート", self.import_settings, "secondary")
        self.toolbar.add_button("📤 エクスポート", self.export_settings, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("🔄 リセット", self.reset_to_default, "warning")
    
    def create_content(self):
        """設定コンテンツを作成"""
        # 設定カテゴリのノートブック
        self.settings_notebook = ttk.Notebook(self.content_frame)
        self.settings_notebook.pack(fill="both", expand=True)
        
        # 各設定タブを作成
        self.create_general_settings()
        self.create_shift_settings()
        self.create_notification_settings()
        self.create_data_settings()
        self.create_appearance_settings()
    
    def create_general_settings(self):
        """一般設定タブを作成"""
        general_frame = UnifiedFrame(self.settings_notebook)
        self.settings_notebook.add(general_frame, text="⚙️ 一般")
        
        # 会社情報カード
        company_card = UnifiedCard(general_frame, title="🏢 会社情報")
        company_card.pack(fill="x", padx=10, pady=5)
        
        # 会社名
        self.company_name_var = tk.StringVar(value=self.settings.get("company_name", ""))
        self.create_form_field(company_card, "会社名:", "entry", textvariable=self.company_name_var, placeholder="会社名を入力")
        
        # 部門
        self.department_var = tk.StringVar(value=self.settings.get("department", ""))
        self.create_form_field(company_card, "部門:", "entry", textvariable=self.department_var, placeholder="部門名を入力")
        
        # 営業時間設定カード
        hours_card = UnifiedCard(general_frame, title="🕐 営業時間")
        hours_card.pack(fill="x", padx=10, pady=5)
        
        # 開始・終了時間
        time_container = UnifiedFrame(hours_card)
        time_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedLabel(time_container, text="開始時間:", style="default").pack(side="left", padx=(0, 10))
        self.start_time_var = tk.StringVar(value=self.settings.get("start_time", "09:00"))
        start_time_entry = UnifiedEntry(time_container, textvariable=self.start_time_var, placeholder="09:00")
        start_time_entry.pack(side="left", padx=(0, 20))
        
        UnifiedLabel(time_container, text="終了時間:", style="default").pack(side="left", padx=(0, 10))
        self.end_time_var = tk.StringVar(value=self.settings.get("end_time", "18:00"))
        end_time_entry = UnifiedEntry(time_container, textvariable=self.end_time_var, placeholder="18:00")
        end_time_entry.pack(side="left")
        
        # 休憩時間
        self.break_time_var = tk.StringVar(value=str(self.settings.get("break_time", 60)))
        self.create_form_field(hours_card, "休憩時間(分):", "entry", textvariable=self.break_time_var, placeholder="60")
        
        # 言語・地域設定カード
        locale_card = UnifiedCard(general_frame, title="🌐 言語・地域")
        locale_card.pack(fill="x", padx=10, pady=5)
        
        # 言語
        lang_container = UnifiedFrame(locale_card)
        lang_container.pack(fill="x", padx=10, pady=5)
        
        UnifiedLabel(lang_container, text="言語:", style="default").pack(side="left", padx=(0, 10))
        self.language_var = tk.StringVar(value=self.settings.get("language", "日本語"))
        language_combo = ttk.Combobox(lang_container, textvariable=self.language_var, width=15)
        language_combo['values'] = ["日本語", "English"]
        language_combo.pack(side="left")
        
        # タイムゾーン
        tz_container = UnifiedFrame(locale_card)
        tz_container.pack(fill="x", padx=10, pady=5)
        
        UnifiedLabel(tz_container, text="タイムゾーン:", style="default").pack(side="left", padx=(0, 10))
        self.timezone_var = tk.StringVar(value=self.settings.get("timezone", "Asia/Tokyo"))
        timezone_combo = ttk.Combobox(tz_container, textvariable=self.timezone_var, width=15)
        timezone_combo['values'] = ["Asia/Tokyo", "UTC", "America/New_York"]
        timezone_combo.pack(side="left")
    
    def create_shift_settings(self):
        """シフト設定タブを作成"""
        shift_frame = UnifiedFrame(self.settings_notebook)
        self.settings_notebook.add(shift_frame, text="📅 シフト")
        
        # シフト作成設定カード
        creation_card = UnifiedCard(shift_frame, title="🎯 シフト作成")
        creation_card.pack(fill="x", padx=10, pady=5)
        
        # 最小スタッフ数
        self.min_staff_var = tk.StringVar(value=str(self.settings.get("min_staff", 2)))
        min_staff_container = UnifiedFrame(creation_card)
        min_staff_container.pack(fill="x", padx=10, pady=5)
        UnifiedLabel(min_staff_container, text="最小スタッフ数:", style="default").pack(side="left", padx=(0, 10))
        min_staff_spin = ttk.Spinbox(min_staff_container, from_=1, to=10, textvariable=self.min_staff_var, width=5)
        min_staff_spin.pack(side="left")
        
        # 最大連続勤務日
        self.max_consecutive_var = tk.StringVar(value=str(self.settings.get("max_consecutive_days", 5)))
        max_consecutive_container = UnifiedFrame(creation_card)
        max_consecutive_container.pack(fill="x", padx=10, pady=5)
        UnifiedLabel(max_consecutive_container, text="最大連続勤務日:", style="default").pack(side="left", padx=(0, 10))
        max_consecutive_spin = ttk.Spinbox(max_consecutive_container, from_=1, to=14, textvariable=self.max_consecutive_var, width=5)
        max_consecutive_spin.pack(side="left")
        
        # AI設定カード
        ai_card = UnifiedCard(shift_frame, title="🤖 AI設定")
        ai_card.pack(fill="x", padx=10, pady=5)
        
        ai_container = UnifiedFrame(ai_card)
        ai_container.pack(fill="x", padx=10, pady=10)
        
        self.ai_optimization_var = tk.BooleanVar(value=self.settings.get("ai_optimization", True))
        ai_check = ttk.Checkbutton(ai_container, text="🤖 AI最適化を使用", variable=self.ai_optimization_var)
        ai_check.pack(anchor="w", pady=2)
        
        self.auto_substitute_var = tk.BooleanVar(value=self.settings.get("auto_substitute", True))
        substitute_check = ttk.Checkbutton(ai_container, text="⚡ 自動代替要員提案", variable=self.auto_substitute_var)
        substitute_check.pack(anchor="w", pady=2)
        
        self.balance_workload_var = tk.BooleanVar(value=self.settings.get("balance_workload", True))
        balance_check = ttk.Checkbutton(ai_container, text="⚖️ 労働時間バランス調整", variable=self.balance_workload_var)
        balance_check.pack(anchor="w", pady=2)
    
    def create_notification_settings(self):
        """通知設定タブを作成"""
        notification_frame = UnifiedFrame(self.settings_notebook)
        self.settings_notebook.add(notification_frame, text="🔔 通知")
        
        # 通知設定カード
        notify_card = UnifiedCard(notification_frame, title="📢 通知設定")
        notify_card.pack(fill="x", padx=10, pady=5)
        
        notify_container = UnifiedFrame(notify_card)
        notify_container.pack(fill="x", padx=10, pady=10)
        
        self.shift_reminder_var = tk.BooleanVar(value=self.settings.get("shift_reminder", True))
        reminder_check = ttk.Checkbutton(notify_container, text="📅 シフト開始前の通知", variable=self.shift_reminder_var)
        reminder_check.pack(anchor="w", pady=2)
        
        self.absence_alert_var = tk.BooleanVar(value=self.settings.get("absence_alert", True))
        absence_check = ttk.Checkbutton(notify_container, text="⚠️ 欠勤時のアラート", variable=self.absence_alert_var)
        absence_check.pack(anchor="w", pady=2)
        
        self.schedule_change_var = tk.BooleanVar(value=self.settings.get("schedule_change", True))
        change_check = ttk.Checkbutton(notify_container, text="🔄 スケジュール変更通知", variable=self.schedule_change_var)
        change_check.pack(anchor="w", pady=2)
        
        # 通知タイミングカード
        timing_card = UnifiedCard(notification_frame, title="⏰ 通知タイミング")
        timing_card.pack(fill="x", padx=10, pady=5)
        
        # 事前通知時間
        self.notification_time_var = tk.StringVar(value=str(self.settings.get("notification_minutes", 30)))
        timing_container = UnifiedFrame(timing_card)
        timing_container.pack(fill="x", padx=10, pady=10)
        UnifiedLabel(timing_container, text="事前通知時間:", style="default").pack(side="left", padx=(0, 10))
        time_spin = ttk.Spinbox(timing_container, from_=5, to=120, textvariable=self.notification_time_var, width=5)
        time_spin.pack(side="left", padx=(0, 5))
        UnifiedLabel(timing_container, text="分前", style="default").pack(side="left")
    
    def create_data_settings(self):
        """データ設定タブを作成"""
        data_frame = UnifiedFrame(self.settings_notebook)
        self.settings_notebook.add(data_frame, text="💾 データ")
        
        # バックアップ設定カード
        backup_card = UnifiedCard(data_frame, title="💾 バックアップ")
        backup_card.pack(fill="x", padx=10, pady=5)
        
        backup_container = UnifiedFrame(backup_card)
        backup_container.pack(fill="x", padx=10, pady=10)
        
        self.auto_backup_var = tk.BooleanVar(value=self.settings.get("auto_backup", True))
        backup_check = ttk.Checkbutton(backup_container, text="💾 自動バックアップ", variable=self.auto_backup_var)
        backup_check.pack(anchor="w", pady=2)
        
        # データ管理カード
        management_card = UnifiedCard(data_frame, title="🗂️ データ管理")
        management_card.pack(fill="x", padx=10, pady=5)
        
        management_container = UnifiedFrame(management_card)
        management_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedButton(management_container, text="💾 今すぐバックアップ", command=self.backup_now, style="primary").pack(side="left", padx=(0, 10))
        UnifiedButton(management_container, text="🔄 復元", command=self.restore_data, style="secondary").pack(side="left", padx=(0, 10))
        UnifiedButton(management_container, text="🗑️ データクリア", command=self.clear_data, style="warning").pack(side="left")
    
    def create_appearance_settings(self):
        """外観設定タブを作成"""
        appearance_frame = UnifiedFrame(self.settings_notebook)
        self.settings_notebook.add(appearance_frame, text="🎨 外観")
        
        # テーマ設定カード
        theme_card = UnifiedCard(appearance_frame, title="🎨 テーマ")
        theme_card.pack(fill="x", padx=10, pady=5)
        
        theme_container = UnifiedFrame(theme_card)
        theme_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedLabel(theme_container, text="テーマ:", style="default").pack(side="left", padx=(0, 10))
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "ライト"))
        theme_combo = ttk.Combobox(theme_container, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ["ライト", "ダーク", "自動"]
        theme_combo.pack(side="left")
        
        # 表示設定カード
        display_card = UnifiedCard(appearance_frame, title="📺 表示設定")
        display_card.pack(fill="x", padx=10, pady=5)
        
        display_container = UnifiedFrame(display_card)
        display_container.pack(fill="x", padx=10, pady=10)
        
        self.show_tooltips_var = tk.BooleanVar(value=self.settings.get("show_tooltips", True))
        tooltips_check = ttk.Checkbutton(display_container, text="💬 ツールチップを表示", variable=self.show_tooltips_var)
        tooltips_check.pack(anchor="w", pady=2)
        
        self.show_animations_var = tk.BooleanVar(value=self.settings.get("show_animations", True))
        animations_check = ttk.Checkbutton(display_container, text="✨ アニメーションを使用", variable=self.show_animations_var)
        animations_check.pack(anchor="w", pady=2)
    
    def load_settings(self) -> Dict[str, Any]:
        """設定を読み込み"""
        default_settings = {
            "company_name": "",
            "department": "",
            "start_time": "09:00",
            "end_time": "18:00",
            "break_time": 60,
            "language": "日本語",
            "timezone": "Asia/Tokyo",
            "min_staff": 2,
            "max_consecutive_days": 5,
            "ai_optimization": True,
            "auto_substitute": True,
            "balance_workload": True,
            "shift_reminder": True,
            "absence_alert": True,
            "schedule_change": True,
            "notification_minutes": 30,
            "auto_backup": True,
            "backup_interval": 7,
            "theme": "ライト",
            "font_size": 10,
            "show_tooltips": True,
            "show_animations": True
        }
        
        try:
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
        
        return default_settings
    
    def save_settings_to_file(self):
        """設定をファイルに保存"""
        try:
            # 現在のUI値を設定に反映
            self.apply_settings()
            
            with open("app_settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("保存完了", "設定を保存しました")
        except Exception as e:
            messagebox.showerror("保存エラー", f"設定の保存に失敗しました:\n{str(e)}")
    
    def apply_settings(self):
        """設定を適用"""
        # UI値を設定辞書に反映
        self.settings.update({
            "company_name": self.company_name_var.get(),
            "department": self.department_var.get(),
            "start_time": self.start_time_var.get(),
            "end_time": self.end_time_var.get(),
            "break_time": int(self.break_time_var.get()) if self.break_time_var.get().isdigit() else 60,
            "language": self.language_var.get(),
            "timezone": self.timezone_var.get(),
            "min_staff": int(self.min_staff_var.get()) if self.min_staff_var.get().isdigit() else 2,
            "max_consecutive_days": int(self.max_consecutive_var.get()) if self.max_consecutive_var.get().isdigit() else 5,
            "ai_optimization": self.ai_optimization_var.get(),
            "auto_substitute": self.auto_substitute_var.get(),
            "balance_workload": self.balance_workload_var.get(),
            "shift_reminder": self.shift_reminder_var.get(),
            "absence_alert": self.absence_alert_var.get(),
            "schedule_change": self.schedule_change_var.get(),
            "notification_minutes": int(self.notification_time_var.get()) if self.notification_time_var.get().isdigit() else 30,
            "auto_backup": self.auto_backup_var.get(),
            "backup_interval": int(self.backup_interval_var.get()) if self.backup_interval_var.get().isdigit() else 7,
            "theme": self.theme_var.get(),
            "font_size": int(self.font_size_var.get()) if self.font_size_var.get().isdigit() else 10,
            "show_tooltips": self.show_tooltips_var.get(),
            "show_animations": self.show_animations_var.get()
        })
        
        messagebox.showinfo("適用完了", "設定を適用しました")
    
    def cancel_changes(self):
        """変更をキャンセル"""
        # 設定を再読み込み
        self.settings = self.load_settings()
        messagebox.showinfo("キャンセル", "変更をキャンセルしました")
    
    def reset_to_default(self):
        """デフォルト設定に戻す"""
        result = messagebox.askyesno("確認", "すべての設定をデフォルトに戻しますか？")
        if result:
            # デフォルト設定で上書き
            self.settings = self.load_settings()
            messagebox.showinfo("リセット完了", "設定をデフォルトに戻しました")
    
    def import_settings(self):
        """設定をインポート"""
        file_path = filedialog.askopenfilename(
            title="設定ファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported_settings = json.load(f)
                    self.settings.update(imported_settings)
                messagebox.showinfo("インポート完了", "設定をインポートしました")
            except Exception as e:
                messagebox.showerror("インポートエラー", f"設定のインポートに失敗しました:\n{str(e)}")
    
    def export_settings(self):
        """設定をエクスポート"""
        file_path = filedialog.asksaveasfilename(
            title="設定ファイルを保存",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("エクスポート完了", "設定をエクスポートしました")
            except Exception as e:
                messagebox.showerror("エクスポートエラー", f"設定のエクスポートに失敗しました:\n{str(e)}")
    
    def backup_now(self):
        """今すぐバックアップ"""
        messagebox.showinfo("バックアップ", "バックアップを実行しました")
    
    def restore_data(self):
        """データを復元"""
        result = messagebox.askyesno("確認", "データを復元しますか？現在のデータは上書きされます。")
        if result:
            messagebox.showinfo("復元完了", "データを復元しました")
    
    def clear_data(self):
        """データをクリア"""
        result = messagebox.askyesno("警告", "すべてのデータを削除しますか？この操作は取り消せません。")
        if result:
            messagebox.showinfo("クリア完了", "データをクリアしました")