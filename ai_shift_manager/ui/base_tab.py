# -*- coding: utf-8 -*-
"""
統一タブベースクラス
全タブで共通の機能とUIを提供
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedEntry,
    UnifiedCard, UnifiedToolbar, UnifiedNotification, UnifiedTheme
)

class BaseTab:
    """タブベースクラス"""
    
    def __init__(self, parent, title="タブ"):
        self.parent = parent
        self.title = title
        self.frame = None
        self.toolbar = None
        self.content_frame = None
        self.status_bar = None
        
        # 初期化
        self.setup_ui()
        self.setup_toolbar()
        self.setup_content()
        self.setup_status_bar()
        self.load_data()
    
    def setup_ui(self):
        """基本UI構造を設定"""
        # メインフレーム
        self.frame = UnifiedFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        
        # タイトル
        title_label = UnifiedLabel(self.frame, text=self.title, style="heading")
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 区切り線
        separator = tk.Frame(self.frame, height=2, bg=UnifiedTheme.COLORS['border'])
        separator.pack(fill="x", padx=10, pady=(0, 10))
    
    def setup_toolbar(self):
        """ツールバーを設定"""
        self.toolbar = UnifiedToolbar(self.frame)
        self.create_toolbar_buttons()
    
    def setup_content(self):
        """コンテンツエリアを設定"""
        self.content_frame = UnifiedFrame(self.frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.create_content()
    
    def setup_status_bar(self):
        """ステータスバーを設定"""
        self.status_bar = UnifiedFrame(self.frame, style="sidebar")
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = UnifiedLabel(
            self.status_bar, 
            text="準備完了", 
            style="small"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成（サブクラスでオーバーライド）"""
        pass
    
    def create_content(self):
        """コンテンツを作成（サブクラスでオーバーライド）"""
        pass
    
    def load_data(self):
        """データを読み込み（サブクラスでオーバーライド）"""
        pass
    
    def refresh(self):
        """データを更新"""
        self.update_status("データを更新中...")
        self.load_data()
        self.update_status("更新完了")
    
    def update_status(self, message):
        """ステータスメッセージを更新"""
        if self.status_label:
            self.status_label.config(text=message)
            self.frame.update_idletasks()
    
    def show_success(self, title, message):
        """成功通知を表示"""
        UnifiedNotification.show_success(self.frame, title, message)
    
    def show_warning(self, title, message):
        """警告通知を表示"""
        UnifiedNotification.show_warning(self.frame, title, message)
    
    def show_error(self, title, message):
        """エラー通知を表示"""
        UnifiedNotification.show_error(self.frame, title, message)
    
    def ask_confirmation(self, title, message):
        """確認ダイアログを表示"""
        return UnifiedNotification.ask_confirmation(self.frame, title, message)

class DataTableMixin:
    """データテーブル機能のミックスイン"""
    
    def create_data_table(self, parent, columns, data=None):
        """データテーブルを作成"""
        # テーブルフレーム
        table_frame = UnifiedFrame(parent, style="card")
        table_frame.pack(fill="both", expand=True, pady=5)
        
        # Treeviewでテーブル作成
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # カラムヘッダー設定
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # スクロールバー
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 配置
        tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # データ挿入
        if data:
            for row in data:
                tree.insert("", "end", values=row)
        
        return tree
    
    def update_table_data(self, tree, data):
        """テーブルデータを更新"""
        # 既存データをクリア
        for item in tree.get_children():
            tree.delete(item)
        
        # 新しいデータを挿入
        for row in data:
            tree.insert("", "end", values=row)

class FormMixin:
    """フォーム機能のミックスイン"""
    
    def create_form_field(self, parent, label_text, field_type="entry", **kwargs):
        """フォームフィールドを作成"""
        field_frame = UnifiedFrame(parent)
        field_frame.pack(fill="x", pady=2)
        
        # ラベル
        label = UnifiedLabel(field_frame, text=label_text, style="default")
        label.pack(side="left", padx=(0, 10))
        
        # フィールド
        if field_type == "entry":
            field = UnifiedEntry(field_frame, **kwargs)
        elif field_type == "text":
            field = tk.Text(field_frame, height=3, **kwargs)
        elif field_type == "combobox":
            field = ttk.Combobox(field_frame, **kwargs)
        else:
            field = UnifiedEntry(field_frame, **kwargs)
        
        field.pack(side="right", fill="x", expand=True)
        
        return field_frame, field
    
    def create_button_group(self, parent, buttons):
        """ボタングループを作成"""
        button_frame = UnifiedFrame(parent)
        button_frame.pack(fill="x", pady=10)
        
        for button_config in buttons:
            btn = UnifiedButton(
                button_frame,
                text=button_config.get("text", "ボタン"),
                command=button_config.get("command"),
                style=button_config.get("style", "primary")
            )
            btn.pack(side="right", padx=2)
        
        return button_frame

# サンプルタブクラス
class SampleTab(BaseTab, DataTableMixin, FormMixin):
    """サンプルタブ実装"""
    
    def __init__(self, parent):
        super().__init__(parent, "サンプルタブ")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("新規作成", self.create_new, "primary")
        self.toolbar.add_button("更新", self.refresh, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("削除", self.delete_selected, "warning")
    
    def create_content(self):
        """コンテンツを作成"""
        # フォームエリア
        form_card = UnifiedCard(self.content_frame, title="データ入力")
        form_card.pack(fill="x", pady=5)
        
        self.name_field = self.create_form_field(form_card, "名前:", "entry", placeholder="名前を入力")[1]
        self.email_field = self.create_form_field(form_card, "メール:", "entry", placeholder="メール@example.com")[1]
        
        # ボタン
        self.create_button_group(form_card, [
            {"text": "保存", "command": self.save_data, "style": "success"},
            {"text": "クリア", "command": self.clear_form, "style": "light"}
        ])
        
        # データテーブル
        table_card = UnifiedCard(self.content_frame, title="データ一覧")
        table_card.pack(fill="both", expand=True, pady=5)
        
        self.data_table = self.create_data_table(
            table_card,
            ["ID", "名前", "メール", "作成日"],
            [
                ["1", "田中太郎", "tanaka@example.com", "2024-01-01"],
                ["2", "佐藤花子", "sato@example.com", "2024-01-02"]
            ]
        )
    
    def create_new(self):
        """新規作成"""
        self.clear_form()
        self.update_status("新規作成モード")
    
    def save_data(self):
        """データ保存"""
        name = self.name_field.get()
        email = self.email_field.get()
        
        if not name or not email:
            self.show_warning("入力エラー", "名前とメールを入力してください")
            return
        
        self.show_success("保存完了", f"{name}のデータを保存しました")
        self.clear_form()
    
    def clear_form(self):
        """フォームクリア"""
        self.name_field.delete(0, tk.END)
        self.email_field.delete(0, tk.END)
    
    def delete_selected(self):
        """選択項目削除"""
        if self.ask_confirmation("削除確認", "選択したデータを削除しますか？"):
            self.show_success("削除完了", "データを削除しました")

# テスト用
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ベースタブ - テスト")
    root.geometry("800x600")
    
    tab = SampleTab(root)
    
    root.mainloop()