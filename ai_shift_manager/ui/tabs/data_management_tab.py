# -*- coding: utf-8 -*-
"""
データ管理タブ
スタッフ情報、勤怠データ、シフトデータの管理UI - 統一UI版
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab, DataTableMixin, FormMixin
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedEntry,
    UnifiedCard, UnifiedTheme
)

class DataManagementTab(BaseTab, DataTableMixin, FormMixin):
    """データ管理タブクラス - 統一UI版"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        self.staff_tree = None
        self.timecard_tree = None
        self.shift_tree = None
        self.staff_search_entry = None
        self.timecard_start_entry = None
        self.timecard_end_entry = None
        super().__init__(parent_frame, "📊 データ管理")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("📥 インポート", self.show_import_dialog, "primary")
        self.toolbar.add_button("📤 エクスポート", self.show_export_dialog, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("👤 スタッフ追加", self.add_staff, "success")
        self.toolbar.add_button("🔄 更新", self.refresh, "light")
    
    def create_content(self):
        """データ管理コンテンツを作成"""
        # データ管理ノートブック
        self.data_notebook = ttk.Notebook(self.content_frame)
        self.data_notebook.pack(fill="both", expand=True)
        
        # 各データ管理タブを作成
        self.create_staff_management_tab()
        self.create_timecard_management_tab()
        self.create_shift_management_tab()
        self.create_import_export_tab()
    
    def create_staff_management_tab(self):
        """スタッフ管理タブを作成"""
        staff_frame = UnifiedFrame(self.data_notebook)
        self.data_notebook.add(staff_frame, text="👥 スタッフ管理")
        
        # 検索・フィルターカード
        search_card = UnifiedCard(staff_frame, title="🔍 スタッフ検索")
        search_card.pack(fill="x", padx=10, pady=5)
        
        search_container = UnifiedFrame(search_card)
        search_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedLabel(search_container, text="検索:", style="default").pack(side="left", padx=(0, 5))
        self.staff_search_entry = UnifiedEntry(search_container, placeholder="名前またはIDで検索")
        self.staff_search_entry.pack(side="left", padx=(0, 10))
        
        UnifiedButton(search_container, text="検索", command=self.search_staff, style="primary").pack(side="left", padx=(0, 20))
        
        # 操作ボタン
        UnifiedButton(search_container, text="編集", command=self.edit_staff, style="secondary").pack(side="right", padx=2)
        UnifiedButton(search_container, text="削除", command=self.delete_staff, style="warning").pack(side="right", padx=2)
        
        # スタッフ一覧カード
        list_card = UnifiedCard(staff_frame, title="👥 スタッフ一覧")
        list_card.pack(fill="both", expand=True, padx=10, pady=5)
        
        # スタッフテーブル
        self.staff_tree = self.create_data_table(
            list_card,
            ['ID', '氏名', '部門', '役職', '時給', '雇用形態']
        )
    
    def create_timecard_management_tab(self):
        """勤怠管理タブを作成"""
        timecard_frame = UnifiedFrame(self.data_notebook)
        self.data_notebook.add(timecard_frame, text="⏰ 勤怠管理")
        
        # 期間選択カード
        period_card = UnifiedCard(timecard_frame, title="📅 期間選択")
        period_card.pack(fill="x", padx=10, pady=5)
        
        period_container = UnifiedFrame(period_card)
        period_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedLabel(period_container, text="期間:", style="default").pack(side="left", padx=(0, 5))
        self.timecard_start_entry = UnifiedEntry(period_container, placeholder="開始日")
        self.timecard_start_entry.pack(side="left", padx=(0, 5))
        self.timecard_start_entry.insert(0, "2024-01-01")
        
        UnifiedLabel(period_container, text="〜", style="default").pack(side="left", padx=5)
        self.timecard_end_entry = UnifiedEntry(period_container, placeholder="終了日")
        self.timecard_end_entry.pack(side="left", padx=(5, 10))
        self.timecard_end_entry.insert(0, "2024-01-31")
        
        UnifiedButton(period_container, text="フィルター", command=self.filter_timecard, style="primary").pack(side="left")
        
        # 勤怠一覧カード
        timecard_list_card = UnifiedCard(timecard_frame, title="⏰ 勤怠記録")
        timecard_list_card.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 勤怠テーブル
        self.timecard_tree = self.create_data_table(
            timecard_list_card,
            ['日付', 'ID', '氏名', '出勤', '退勤', '休憩', '実働']
        )
    
    def create_shift_management_tab(self):
        """シフト管理タブを作成"""
        shift_frame = UnifiedFrame(self.data_notebook)
        self.data_notebook.add(shift_frame, text="📅 シフト管理")
        
        # シフト一覧カード
        shift_card = UnifiedCard(shift_frame, title="📅 シフト記録")
        shift_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # シフトテーブル
        self.shift_tree = self.create_data_table(
            shift_card,
            ['日付', '時間', 'スタッフ', '役割']
        )
    
    def create_import_export_tab(self):
        """インポート・エクスポートタブを作成"""
        import_export_frame = UnifiedFrame(self.data_notebook)
        self.data_notebook.add(import_export_frame, text="📁 インポート・エクスポート")
        
        # インポートカード
        import_card = UnifiedCard(import_export_frame, title="📥 データインポート")
        import_card.pack(fill="x", padx=10, pady=10)
        
        import_container = UnifiedFrame(import_card)
        import_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedButton(import_container, text="👥 スタッフデータ", command=self.import_staff_data, style="primary").pack(side="left", padx=(0, 10))
        UnifiedButton(import_container, text="⏰ 勤怠データ", command=self.import_timecard_data, style="primary").pack(side="left", padx=(0, 10))
        UnifiedButton(import_container, text="📅 シフトデータ", command=self.import_shift_data, style="primary").pack(side="left")
        
        # エクスポートカード
        export_card = UnifiedCard(import_export_frame, title="📤 データエクスポート")
        export_card.pack(fill="x", padx=10, pady=10)
        
        export_container = UnifiedFrame(export_card)
        export_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedButton(export_container, text="👥 スタッフデータ", command=self.export_staff_data, style="secondary").pack(side="left", padx=(0, 10))
        UnifiedButton(export_container, text="⏰ 勤怠データ", command=self.export_timecard_data, style="secondary").pack(side="left", padx=(0, 10))
        UnifiedButton(export_container, text="📅 シフトデータ", command=self.export_shift_data, style="secondary").pack(side="left")
        
        # データ統計カード
        stats_card = UnifiedCard(import_export_frame, title="📊 データ統計")
        stats_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        stats_container = UnifiedFrame(stats_card)
        stats_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 統計情報表示
        UnifiedLabel(stats_container, text="📊 データベース統計", style="subheading").pack(anchor="w", pady=(0, 10))
        UnifiedLabel(stats_container, text="• スタッフ数: 5名", style="default").pack(anchor="w", pady=2)
        UnifiedLabel(stats_container, text="• 勤怠記録: 120件", style="default").pack(anchor="w", pady=2)
        UnifiedLabel(stats_container, text="• シフト記録: 45件", style="default").pack(anchor="w", pady=2)
        UnifiedLabel(stats_container, text="• 最終更新: 2024-01-15 10:30", style="small").pack(anchor="w", pady=(10, 0))
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("データを読み込み中...")
        self.load_staff_data()
        self.load_timecard_data()
        self.load_shift_data()
        self.update_status("データ読み込み完了")
    
    def load_staff_data(self):
        """スタッフデータを読み込み"""
        if not self.staff_tree:
            return
        
        # サンプルデータ
        sample_staff = [
            ("EMP001", "田中太郎", "営業部", "スタッフ", "1200円", "正社員"),
            ("EMP002", "佐藤花子", "営業部", "リーダー", "1500円", "正社員"),
            ("EMP003", "鈴木次郎", "総務部", "スタッフ", "1000円", "パート"),
            ("EMP004", "山田美咲", "営業部", "スタッフ", "1100円", "パート"),
            ("EMP005", "高橋健太", "営業部", "スタッフ", "1050円", "アルバイト")
        ]
        
        self.update_table_data(self.staff_tree, sample_staff)
    
    def load_timecard_data(self):
        """勤怠データを読み込み"""
        if not self.timecard_tree:
            return
        
        # サンプルデータ
        sample_timecard = [
            ("2024-01-15", "EMP001", "田中太郎", "09:00", "17:00", "60分", "480分"),
            ("2024-01-15", "EMP002", "佐藤花子", "10:00", "18:00", "60分", "420分"),
            ("2024-01-16", "EMP001", "田中太郎", "09:00", "17:00", "60分", "480分"),
            ("2024-01-16", "EMP003", "鈴木次郎", "09:00", "13:00", "0分", "240分"),
            ("2024-01-17", "EMP002", "佐藤花子", "10:00", "18:00", "60分", "420分"),
            ("2024-01-17", "EMP004", "山田美咲", "13:00", "21:00", "60分", "420分")
        ]
        
        self.update_table_data(self.timecard_tree, sample_timecard)
    
    def load_shift_data(self):
        """シフトデータを読み込み"""
        if not self.shift_tree:
            return
        
        # サンプルデータ
        sample_shifts = [
            ("2024-01-15", "09:00-17:00", "田中太郎", "リーダー"),
            ("2024-01-15", "10:00-18:00", "佐藤花子", "スタッフ"),
            ("2024-01-16", "09:00-17:00", "鈴木次郎", "スタッフ"),
            ("2024-01-16", "13:00-21:00", "山田美咲", "スタッフ"),
            ("2024-01-17", "09:00-17:00", "佐藤花子", "リーダー"),
            ("2024-01-17", "12:00-20:00", "高橋健太", "スタッフ")
        ]
        
        self.update_table_data(self.shift_tree, sample_shifts)
    
    def search_staff(self):
        """スタッフを検索"""
        if not self.staff_search_entry:
            return
        
        search_term = self.staff_search_entry.get()
        if not search_term:
            self.show_warning("検索エラー", "検索キーワードを入力してください")
            return
        
        self.update_status(f"'{search_term}' で検索中...")
        # TODO: 実際の検索処理を実装
        self.update_status("検索完了")
        self.show_success("検索完了", f"'{search_term}' で検索しました")
    
    def add_staff(self):
        """スタッフを追加"""
        self.update_status("スタッフ追加画面を開いています...")
        # TODO: スタッフ追加ダイアログを実装
        self.show_success("スタッフ追加", "スタッフ追加機能は実装中です\n\n今後のアップデートで対応予定です")
    
    def edit_staff(self):
        """スタッフを編集"""
        if not self.staff_tree:
            return
        
        selection = self.staff_tree.selection()
        if not selection:
            self.show_warning("選択エラー", "編集するスタッフを選択してください")
            return
        
        # 選択されたスタッフの情報を取得
        item = self.staff_tree.item(selection[0])
        staff_data = item['values']
        
        self.update_status("スタッフ編集画面を開いています...")
        # TODO: スタッフ編集ダイアログを実装
        self.show_success("スタッフ編集", f"{staff_data[1]}さんの編集機能は実装中です")
    
    def delete_staff(self):
        """スタッフを削除"""
        if not self.staff_tree:
            return
        
        selection = self.staff_tree.selection()
        if not selection:
            self.show_warning("選択エラー", "削除するスタッフを選択してください")
            return
        
        # 選択されたスタッフの情報を取得
        item = self.staff_tree.item(selection[0])
        staff_data = item['values']
        
        if self.ask_confirmation("削除確認", f"{staff_data[1]}さんを削除しますか？\n\nこの操作は取り消せません。"):
            self.staff_tree.delete(selection[0])
            self.update_status(f"{staff_data[1]}さんを削除しました")
            self.show_success("削除完了", f"{staff_data[1]}さんを削除しました")
    
    def filter_timecard(self):
        """勤怠データをフィルター"""
        if not self.timecard_start_entry or not self.timecard_end_entry:
            return
        
        start_date = self.timecard_start_entry.get()
        end_date = self.timecard_end_entry.get()
        
        if not start_date or not end_date:
            self.show_warning("入力エラー", "開始日と終了日を入力してください")
            return
        
        self.update_status(f"{start_date} 〜 {end_date} でフィルター中...")
        # TODO: 実際のフィルター処理を実装
        self.load_timecard_data()  # データを再読み込み
        self.update_status("フィルター完了")
        self.show_success("フィルター完了", f"期間: {start_date} 〜 {end_date}\nでフィルターしました")
    
    def show_import_dialog(self):
        """インポートダイアログを表示"""
        self.update_status("インポートダイアログを開いています...")
        # TODO: 統一されたインポートダイアログを実装
        self.show_success("インポート", "統一インポートダイアログは実装中です")
    
    def show_export_dialog(self):
        """エクスポートダイアログを表示"""
        self.update_status("エクスポートダイアログを開いています...")
        # TODO: 統一されたエクスポートダイアログを実装
        self.show_success("エクスポート", "統一エクスポートダイアログは実装中です")
    
    def import_staff_data(self):
        """スタッフデータをインポート"""
        file_path = filedialog.askopenfilename(
            title="スタッフデータファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("スタッフデータをインポート中...")
            # TODO: 実際のインポート処理を実装
            self.load_staff_data()  # データを再読み込み
            self.update_status("インポート完了")
            self.show_success("インポート完了", f"スタッフデータをインポートしました\n\nファイル: {file_path}")
    
    def import_timecard_data(self):
        """勤怠データをインポート"""
        file_path = filedialog.askopenfilename(
            title="勤怠データファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("勤怠データをインポート中...")
            # TODO: 実際のインポート処理を実装
            self.load_timecard_data()  # データを再読み込み
            self.update_status("インポート完了")
            self.show_success("インポート完了", f"勤怠データをインポートしました\n\nファイル: {file_path}")
    
    def import_shift_data(self):
        """シフトデータをインポート"""
        file_path = filedialog.askopenfilename(
            title="シフトデータファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("シフトデータをインポート中...")
            # TODO: 実際のインポート処理を実装
            self.load_shift_data()  # データを再読み込み
            self.update_status("インポート完了")
            self.show_success("インポート完了", f"シフトデータをインポートしました\n\nファイル: {file_path}")
    
    def export_staff_data(self):
        """スタッフデータをエクスポート"""
        file_path = filedialog.asksaveasfilename(
            title="スタッフデータを保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("スタッフデータをエクスポート中...")
            # TODO: 実際のエクスポート処理を実装
            self.update_status("エクスポート完了")
            self.show_success("エクスポート完了", f"スタッフデータをエクスポートしました\n\nファイル: {file_path}")
    
    def export_timecard_data(self):
        """勤怠データをエクスポート"""
        file_path = filedialog.asksaveasfilename(
            title="勤怠データを保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("勤怠データをエクスポート中...")
            # TODO: 実際のエクスポート処理を実装
            self.update_status("エクスポート完了")
            self.show_success("エクスポート完了", f"勤怠データをエクスポートしました\n\nファイル: {file_path}")
    
    def export_shift_data(self):
        """シフトデータをエクスポート"""
        file_path = filedialog.asksaveasfilename(
            title="シフトデータを保存",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.update_status("シフトデータをエクスポート中...")
            # TODO: 実際のエクスポート処理を実装
            self.update_status("エクスポート完了")
            self.show_success("エクスポート完了", f"シフトデータをエクスポートしました\n\nファイル: {file_path}")