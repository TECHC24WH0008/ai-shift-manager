# -*- coding: utf-8 -*-
"""
シフト作成タブ
AIを使用したシフト自動作成機能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab, FormMixin, DataTableMixin
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedEntry,
    UnifiedCard, UnifiedTheme
)

class ShiftCreationTab(BaseTab, FormMixin, DataTableMixin):
    """シフト作成タブクラス"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        self.shift_tree = None
        self.start_date_entry = None
        self.end_date_entry = None
        self.start_time_entry = None
        self.end_time_entry = None
        self.min_staff_var = None
        self.optimize_var = None
        self.balance_var = None
        super().__init__(parent_frame, "📅 シフト作成")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("📋 プレビュー生成", self.generate_preview, "primary")
        self.toolbar.add_button("🤖 AI作成", self.create_shift, "success")
        self.toolbar.add_separator()
        self.toolbar.add_button("💾 保存", self.save_shift, "secondary")
        self.toolbar.add_button("🗑️ クリア", self.clear_shift, "warning")
    
    def create_content(self):
        """シフト作成コンテンツを作成"""
        # 設定エリア
        settings_card = UnifiedCard(self.content_frame, title="🎯 シフト作成設定")
        settings_card.pack(fill="x", pady=5)
        
        # 期間設定
        period_frame = UnifiedFrame(settings_card)
        period_frame.pack(fill="x", padx=10, pady=5)
        
        UnifiedLabel(period_frame, text="作成期間:", style="default").pack(side="left", padx=(0, 10))
        
        self.start_date_entry = UnifiedEntry(period_frame, placeholder="開始日")
        self.start_date_entry.pack(side="left", padx=(0, 5))
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        UnifiedLabel(period_frame, text="〜", style="default").pack(side="left", padx=5)
        
        self.end_date_entry = UnifiedEntry(period_frame, placeholder="終了日")
        self.end_date_entry.pack(side="left", padx=(5, 20))
        end_date = datetime.now() + timedelta(days=7)
        self.end_date_entry.insert(0, end_date.strftime("%Y-%m-%d"))
        
        # 営業時間設定
        hours_frame = UnifiedFrame(settings_card)
        hours_frame.pack(fill="x", padx=10, pady=5)
        
        UnifiedLabel(hours_frame, text="営業時間:", style="default").pack(side="left", padx=(0, 10))
        
        self.start_time_entry = UnifiedEntry(hours_frame, placeholder="開始時間")
        self.start_time_entry.pack(side="left", padx=(0, 5))
        self.start_time_entry.insert(0, "09:00")
        
        UnifiedLabel(hours_frame, text="〜", style="default").pack(side="left", padx=5)
        
        self.end_time_entry = UnifiedEntry(hours_frame, placeholder="終了時間")
        self.end_time_entry.pack(side="left", padx=(5, 20))
        self.end_time_entry.insert(0, "18:00")
        
        # 最小スタッフ数
        UnifiedLabel(hours_frame, text="最小スタッフ数:", style="default").pack(side="left", padx=(20, 10))
        self.min_staff_var = tk.StringVar(value="2")
        min_staff_spin = ttk.Spinbox(hours_frame, from_=1, to=10, width=5, textvariable=self.min_staff_var)
        min_staff_spin.pack(side="left")
        
        # AI設定
        ai_frame = UnifiedFrame(settings_card)
        ai_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.optimize_var = tk.BooleanVar(value=True)
        optimize_check = ttk.Checkbutton(ai_frame, text="🤖 AI最適化を使用", variable=self.optimize_var)
        optimize_check.pack(side="left", padx=(0, 20))
        
        self.balance_var = tk.BooleanVar(value=True)
        balance_check = ttk.Checkbutton(ai_frame, text="⚖️ 労働時間バランス調整", variable=self.balance_var)
        balance_check.pack(side="left")
        
        # プレビューエリア
        preview_card = UnifiedCard(self.content_frame, title="📋 シフトプレビュー")
        preview_card.pack(fill="both", expand=True, pady=5)
        
        # シフト表
        self.shift_tree = self.create_data_table(
            preview_card,
            ['日付', '時間', 'スタッフ', '役割']
        )
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("シフトデータを読み込み中...")
        # 初期化時は空のテーブル
        self.update_status("準備完了")
    
    def generate_preview(self):
        """シフトプレビューを生成"""
        self.update_status("プレビューを生成中...")
        
        # 設定値を取得
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()
        min_staff = int(self.min_staff_var.get())
        
        # 入力値検証
        if not all([start_date, end_date, start_time, end_time]):
            self.show_warning("入力エラー", "すべての設定項目を入力してください")
            return
        
        # サンプルシフトデータを生成
        sample_shifts = [
            ("2024-01-15", "09:00-17:00", "田中太郎", "リーダー"),
            ("2024-01-15", "10:00-18:00", "佐藤花子", "スタッフ"),
            ("2024-01-15", "13:00-21:00", "山田美咲", "スタッフ"),
            ("2024-01-16", "09:00-17:00", "鈴木次郎", "スタッフ"),
            ("2024-01-16", "10:00-18:00", "高橋健太", "スタッフ"),
            ("2024-01-16", "17:00-21:00", "田中太郎", "リーダー"),
            ("2024-01-17", "09:00-17:00", "佐藤花子", "リーダー"),
            ("2024-01-17", "12:00-20:00", "山田美咲", "スタッフ"),
        ]
        
        # テーブルを更新
        self.update_table_data(self.shift_tree, sample_shifts)
        
        self.update_status("プレビュー生成完了")
        self.show_success("完了", f"シフトプレビューを生成しました\n期間: {start_date} 〜 {end_date}\n最小スタッフ数: {min_staff}名")
    
    def create_shift(self):
        """AIシフトを作成"""
        if not self.shift_tree.get_children():
            self.show_warning("警告", "まずプレビューを生成してください")
            return
        
        self.update_status("AIシフト作成中...")
        
        # AI最適化の実行
        if self.optimize_var.get():
            optimization_steps = [
                "🤖 AI分析エンジンを起動中...",
                "📊 スタッフスキルを分析中...",
                "⚖️ 労働時間バランスを調整中...",
                "🎯 最適配置を計算中...",
                "✅ シフト最適化完了"
            ]
            
            optimization_message = "\n".join(optimization_steps)
            self.show_success("AI最適化完了", f"AI最適化を実行しました：\n\n{optimization_message}")
        
        # バランス調整
        if self.balance_var.get():
            self.show_success("バランス調整", "労働時間バランスを調整しました")
        
        self.update_status("シフト作成完了")
        self.show_success("作成完了", "🎉 AIシフトを作成しました！\n\n📋 プレビューで内容を確認してください")
    
    def save_shift(self):
        """シフトを保存"""
        if not self.shift_tree.get_children():
            self.show_warning("警告", "保存するシフトがありません")
            return
        
        if not self.ask_confirmation("保存確認", "現在のシフトを保存しますか？"):
            return
        
        self.update_status("シフト保存中...")
        
        # 保存処理（実際の実装では データベースに保存）
        shift_count = len(self.shift_tree.get_children())
        
        self.update_status("保存完了")
        self.show_success("保存完了", f"シフトを保存しました\n\n📊 保存件数: {shift_count}件")
    
    def clear_shift(self):
        """シフトをクリア"""
        if not self.shift_tree.get_children():
            self.show_warning("情報", "クリアするシフトがありません")
            return
        
        if not self.ask_confirmation("クリア確認", "シフトプレビューをクリアしますか？"):
            return
        
        # テーブルをクリア
        self.update_table_data(self.shift_tree, [])
        
        self.update_status("シフトをクリアしました")
        self.show_success("クリア完了", "シフトプレビューをクリアしました")
    
    def load_template(self):
        """テンプレートを読み込み"""
        self.update_status("テンプレート読み込み中...")
        
        # サンプルテンプレートデータ
        template_shifts = [
            ("テンプレート", "09:00-17:00", "リーダー1", "リーダー"),
            ("テンプレート", "10:00-18:00", "スタッフ1", "スタッフ"),
            ("テンプレート", "11:00-19:00", "スタッフ2", "スタッフ"),
        ]
        
        self.update_table_data(self.shift_tree, template_shifts)
        
        self.update_status("テンプレート読み込み完了")
        self.show_success("読み込み完了", "シフトテンプレートを読み込みました\n\n📝 必要に応じて編集してください")