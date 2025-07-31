# -*- coding: utf-8 -*-
"""
ダッシュボードタブ
メインダッシュボード表示とサマリー情報
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedCard, 
    UnifiedListbox, UnifiedTheme
)

class DashboardTab(BaseTab):
    """ダッシュボードタブクラス"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        self.activity_listbox = None
        self.stat_cards = {}
        super().__init__(parent_frame, "📊 ダッシュボード")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("🔄 更新", self.refresh, "primary")
        self.toolbar.add_button("📊 詳細分析", self.view_analytics, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("💾 バックアップ", self.backup_data, "light")
    
    def create_content(self):
        """ダッシュボードコンテンツを作成"""
        # 統計カードエリア
        stats_card = UnifiedCard(self.content_frame, title="📈 統計サマリー")
        stats_card.pack(fill="x", pady=5)
        
        # 統計カードグリッド
        stats_grid = UnifiedFrame(stats_card)
        stats_grid.pack(fill="x", padx=10, pady=10)
        
        # 4列のグリッド設定
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # 統計カード作成
        self.create_stat_card(stats_grid, "👥 スタッフ", "5名", "登録済み", 0, 0)
        self.create_stat_card(stats_grid, "📅 シフト", "12件", "今月作成", 0, 1)
        self.create_stat_card(stats_grid, "⚠️ 欠勤", "2件", "未対応", 0, 2)
        self.create_stat_card(stats_grid, "⚡ 効率", "87%", "平均スコア", 0, 3)
        
        # メインコンテンツエリア
        main_content = UnifiedFrame(self.content_frame)
        main_content.pack(fill="both", expand=True, pady=5)
        
        # 左側: アクティビティ
        activity_card = UnifiedCard(main_content, title="📈 最近のアクティビティ")
        activity_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.activity_listbox = UnifiedListbox(activity_card, height=15)
        self.activity_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 右側: クイックアクション
        quick_card = UnifiedCard(main_content, title="🚀 クイックアクション")
        quick_card.pack(side="right", fill="y", padx=(5, 0))
        
        self.create_quick_actions(quick_card)
    
    def create_stat_card(self, parent, title, value, subtitle, row, col):
        """統計カードを作成"""
        card_frame = UnifiedFrame(parent, style="card")
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # タイトル
        title_label = UnifiedLabel(card_frame, text=title, style="subheading")
        title_label.pack(pady=(15, 5))
        
        # 値
        value_label = UnifiedLabel(card_frame, text=value, style="heading")
        value_label.pack()
        
        # サブタイトル
        subtitle_label = UnifiedLabel(card_frame, text=subtitle, style="small")
        subtitle_label.pack(pady=(5, 15))
        
        # カードを辞書に保存（後で更新用）
        self.stat_cards[title] = {
            'value_label': value_label,
            'subtitle_label': subtitle_label
        }
    
    def create_quick_actions(self, parent):
        """クイックアクションボタンを作成"""
        actions = [
            ("📅 新規シフト作成", self.create_new_shift, "primary"),
            ("👤 スタッフ追加", self.add_staff, "secondary"),
            ("⚠️ 欠勤登録", self.register_absence, "warning"),
            ("📊 分析レポート", self.view_analytics, "success"),
            ("⚙️ 設定", self.open_settings, "light"),
            ("💾 データバックアップ", self.backup_data, "light")
        ]
        
        button_container = UnifiedFrame(parent)
        button_container.pack(fill="x", padx=10, pady=10)
        
        for text, command, style in actions:
            btn = UnifiedButton(button_container, text=text, command=command, style=style)
            btn.pack(fill="x", pady=3)
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("データを読み込み中...")
        
        # 統計データを更新
        self.update_statistics()
        
        # アクティビティデータを読み込み
        self.load_activities()
        
        self.update_status("データ読み込み完了")
    
    def update_statistics(self):
        """統計データを更新"""
        # 実際のデータマネージャーからデータを取得する場合の例
        if self.data_manager:
            # TODO: データマネージャーから実際のデータを取得
            pass
        
        # 現在はサンプルデータ
        stats = {
            "👥 スタッフ": ("5名", "登録済み"),
            "📅 シフト": ("12件", "今月作成"),
            "⚠️ 欠勤": ("2件", "未対応"),
            "⚡ 効率": ("87%", "平均スコア")
        }
        
        # 統計カードを更新
        for title, (value, subtitle) in stats.items():
            if title in self.stat_cards:
                self.stat_cards[title]['value_label'].config(text=value)
                self.stat_cards[title]['subtitle_label'].config(text=subtitle)
    
    def load_activities(self):
        """アクティビティを読み込み"""
        if not self.activity_listbox:
            return
        
        # 既存のアクティビティをクリア
        self.activity_listbox.delete(0, tk.END)
        
        # サンプルアクティビティ
        activities = [
            f"[{datetime.now().strftime('%H:%M')}] アプリケーションが起動しました",
            f"[{datetime.now().strftime('%H:%M')}] ダッシュボードを表示しました",
            "[09:30] 田中太郎さんのシフトを作成しました",
            "[09:15] 佐藤花子さんが出勤しました",
            "[08:45] 新しいスタッフ情報を登録しました",
            "[08:30] システムバックアップが完了しました",
            "[08:15] 週次レポートを生成しました"
        ]
        
        for activity in activities:
            self.activity_listbox.insert(tk.END, activity)
    
    def add_activity(self, message: str):
        """アクティビティを追加"""
        timestamp = datetime.now().strftime("%H:%M")
        activity_text = f"[{timestamp}] {message}"
        self.activity_listbox.insert(0, activity_text)
        
        # 最大50件まで保持
        if self.activity_listbox.size() > 50:
            self.activity_listbox.delete(tk.END)
    
    # クイックアクション関数
    def create_new_shift(self):
        """新規シフト作成"""
        self.add_activity("シフト作成画面を開きました")
        self.show_success("シフト作成", "シフト作成画面を開きました")
    
    def add_staff(self):
        """スタッフ追加"""
        self.add_activity("スタッフ追加画面を開きました")
        self.show_success("スタッフ管理", "スタッフ追加画面を開きました")
    
    def register_absence(self):
        """欠勤登録"""
        self.add_activity("欠勤登録画面を開きました")
        self.show_success("欠勤管理", "欠勤登録画面を開きました")
    
    def view_analytics(self):
        """分析レポート表示"""
        self.add_activity("分析レポートを表示しました")
        self.show_success("分析", "詳細分析レポートを表示しました")
    
    def open_settings(self):
        """設定画面を開く"""
        self.add_activity("設定画面を開きました")
        self.show_success("設定", "設定画面を開きました")
    
    def backup_data(self):
        """データバックアップ"""
        if self.ask_confirmation("バックアップ確認", "データをバックアップしますか？"):
            self.update_status("バックアップ実行中...")
            self.add_activity("データバックアップを実行しました")
            self.update_status("バックアップ完了")
            self.show_success("バックアップ", "データバックアップが完了しました")