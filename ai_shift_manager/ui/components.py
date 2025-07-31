# -*- coding: utf-8 -*-
"""
UIコンポーネントモジュール
再利用可能なUIコンポーネントを提供
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Any
import sys
import os

# パスを追加してcoreモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import app_config

class ModernButton(tk.Button):
    """モダンなボタンコンポーネント（tkinter.Buttonベース）"""
    
    def __init__(self, parent, text: str, command: Callable = None, 
                 style: str = "primary", icon: str = "", **kwargs):
        
        # アイコン付きテキスト
        display_text = f"{icon} {text}" if icon else text
        
        # スタイルに基づく設定を取得
        button_config = self._get_button_config(style)
        
        # tkinter.Buttonで初期化
        super().__init__(parent, text=display_text, command=command, 
                        **button_config, **kwargs)
        
        # ホバー効果を追加
        self._setup_hover_effects(style)
    
    def _get_button_config(self, style: str) -> Dict[str, Any]:
        """スタイルに基づくボタン設定を取得"""
        colors = app_config.get_colors()
        
        if style == "primary":
            return {
                'font': ('Segoe UI', 11, 'bold'),
                'fg': 'white',
                'bg': colors.get("primary", "#2563EB"),
                'activeforeground': 'white',
                'activebackground': colors.get("primary_dark", "#1D4ED8"),
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2',
                'padx': 20,
                'pady': 8
            }
        elif style == "secondary":
            return {
                'font': ('Segoe UI', 10, 'normal'),
                'fg': colors.get("dark", "#1E293B"),
                'bg': colors.get("light", "#F8FAFC"),
                'activeforeground': colors.get("dark", "#1E293B"),
                'activebackground': colors.get("gray_light", "#E2E8F0"),
                'relief': 'solid',
                'borderwidth': 1,
                'cursor': 'hand2',
                'padx': 16,
                'pady': 6
            }
        elif style == "success":
            return {
                'font': ('Segoe UI', 10, 'bold'),
                'fg': 'white',
                'bg': colors.get("secondary", "#10B981"),
                'activeforeground': 'white',
                'activebackground': colors.get("secondary_dark", "#059669"),
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2',
                'padx': 16,
                'pady': 6
            }
        elif style == "danger":
            return {
                'font': ('Segoe UI', 10, 'bold'),
                'fg': 'white',
                'bg': colors.get("danger", "#EF4444"),
                'activeforeground': 'white',
                'activebackground': colors.get("danger_dark", "#DC2626"),
                'relief': 'flat',
                'borderwidth': 0,
                'cursor': 'hand2',
                'padx': 16,
                'pady': 6
            }
        else:
            # デフォルトスタイル
            return {
                'font': ('Segoe UI', 10, 'normal'),
                'fg': colors.get("dark", "#1E293B"),
                'bg': colors.get("white", "#FFFFFF"),
                'activeforeground': colors.get("dark", "#1E293B"),
                'activebackground': colors.get("gray_light", "#F1F5F9"),
                'relief': 'solid',
                'borderwidth': 1,
                'cursor': 'hand2',
                'padx': 16,
                'pady': 6
            }
    
    def _setup_hover_effects(self, style: str):
        """ホバー効果を設定"""
        colors = app_config.get_colors()
        
        # 元の色を保存
        self.original_bg = self['bg']
        self.original_fg = self['fg']
        
        # ホバー時の色を設定
        if style == "primary":
            hover_bg = colors.get("primary_dark", "#1D4ED8")
            hover_fg = 'white'
        elif style == "secondary":
            hover_bg = colors.get("gray_light", "#E2E8F0")
            hover_fg = colors.get("dark", "#1E293B")
        elif style == "success":
            hover_bg = colors.get("secondary_dark", "#059669")
            hover_fg = 'white'
        elif style == "danger":
            hover_bg = colors.get("danger_dark", "#DC2626")
            hover_fg = 'white'
        else:
            hover_bg = colors.get("gray_light", "#F1F5F9")
            hover_fg = colors.get("dark", "#1E293B")
        
        # イベントバインド
        self.bind("<Enter>", lambda e: self.configure(bg=hover_bg, fg=hover_fg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.original_bg, fg=self.original_fg))
    


class Card(ttk.Frame):
    """カードコンポーネント"""
    
    def __init__(self, parent, title: str = "", padding: str = "15", **kwargs):
        super().__init__(parent, **kwargs)
        
        # カードスタイル設定
        self._setup_card_style()
        self.configure(style='Card.TFrame', padding=padding)
        
        # タイトルがある場合は表示
        if title:
            self.title_label = ttk.Label(self, text=title, 
                                        font=app_config.get_fonts()["heading"],
                                        foreground=app_config.get("colors.primary"))
            self.title_label.pack(anchor=tk.W, pady=(0, 10))
    
    def _setup_card_style(self):
        """カードスタイルを設定"""
        style = ttk.Style()
        colors = app_config.get_colors()
        
        style.configure('Card.TFrame',
                       background=colors["white"],
                       relief='solid',
                       borderwidth=1)

class StatusIndicator(ttk.Label):
    """ステータス表示コンポーネント"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_status = "unknown"
    
    def set_status(self, status: str, message: str = ""):
        """ステータスを設定"""
        self.current_status = status
        colors = app_config.get_colors()
        
        status_config = {
            "success": {"icon": "✅", "color": colors["secondary"], "text": message or "正常"},
            "warning": {"icon": "⚠️", "color": colors["accent"], "text": message or "注意"},
            "error": {"icon": "❌", "color": colors["danger"], "text": message or "エラー"},
            "loading": {"icon": "🔄", "color": colors["primary"], "text": message or "処理中"},
            "unknown": {"icon": "⚪", "color": colors["gray"], "text": message or "不明"}
        }
        
        config = status_config.get(status, status_config["unknown"])
        
        self.configure(
            text=f"{config['icon']} {config['text']}",
            foreground=config["color"],
            font=app_config.get_fonts()["body"]
        )

class DataTable(ttk.Treeview):
    """データテーブルコンポーネント"""
    
    def __init__(self, parent, columns: List[Dict], **kwargs):
        
        # 列名を抽出
        column_names = [col["name"] for col in columns]
        
        super().__init__(parent, columns=column_names, show='headings', **kwargs)
        
        # 列設定
        for col in columns:
            self.heading(col["name"], text=col.get("display_name", col["name"]))
            self.column(col["name"], 
                       width=col.get("width", 100),
                       anchor=col.get("anchor", tk.W))
        
        # スタイル適用
        self._apply_table_style()
    
    def _apply_table_style(self):
        """テーブルスタイルを適用"""
        style = ttk.Style()
        colors = app_config.get_colors()
        
        style.configure('Custom.Treeview',
                       background=colors["white"],
                       foreground=colors["dark"],
                       fieldbackground=colors["white"],
                       font=app_config.get_fonts()["body"])
        
        style.configure('Custom.Treeview.Heading',
                       background=colors["primary"],
                       foreground=colors["white"],
                       font=app_config.get_fonts()["heading"])
        
        self.configure(style='Custom.Treeview')
    
    def load_data(self, data: List[Dict]):
        """データを読み込み"""
        # 既存データをクリア
        for item in self.get_children():
            self.delete(item)
        
        # 新しいデータを挿入
        for row in data:
            values = [row.get(col, "") for col in self['columns']]
            self.insert('', tk.END, values=values)

class TabContainer(ttk.Notebook):
    """タブコンテナ"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # スタイル適用
        self._apply_tab_style()
    
    def _apply_tab_style(self):
        """タブスタイルを適用"""
        style = ttk.Style()
        colors = app_config.get_colors()
        
        style.configure('Custom.TNotebook',
                       background=colors["light"],
                       borderwidth=0)
        
        style.configure('Custom.TNotebook.Tab',
                       background=colors["white"],
                       foreground=colors["dark"],
                       padding=[20, 10],
                       font=app_config.get_fonts()["body"])
        
        self.configure(style='Custom.TNotebook')
    
    def add_tab(self, frame, title: str, icon: str = ""):
        """タブを追加"""
        display_title = f"{icon} {title}" if icon else title
        self.add(frame, text=display_title)

class SearchBox(ttk.Frame):
    """検索ボックスコンポーネント"""
    
    def __init__(self, parent, placeholder: str = "検索...", 
                 on_search: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_search = on_search
        
        # 検索入力
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # プレースホルダー設定
        self._setup_placeholder(placeholder)
        
        # 検索ボタン
        self.search_button = ModernButton(self, text="検索", icon="🔍",
                                        command=self._perform_search,
                                        style="primary")
        self.search_button.pack(side=tk.LEFT)
        
        # Enterキーでも検索
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
    
    def _setup_placeholder(self, placeholder: str):
        """プレースホルダーを設定"""
        self.placeholder = placeholder
        self.search_entry.insert(0, placeholder)
        self.search_entry.configure(foreground=app_config.get("colors.gray"))
        
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        """フォーカス取得時"""
        if self.search_var.get() == self.placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground=app_config.get("colors.dark"))
    
    def _on_focus_out(self, event):
        """フォーカス喪失時"""
        if not self.search_var.get():
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.configure(foreground=app_config.get("colors.gray"))
    
    def _perform_search(self):
        """検索実行"""
        query = self.search_var.get()
        if query and query != self.placeholder and self.on_search:
            self.on_search(query)
    
    def get_query(self) -> str:
        """検索クエリを取得"""
        query = self.search_var.get()
        return query if query != self.placeholder else ""

# ユーティリティ関数
def create_separator(parent, orient='horizontal'):
    """セパレーターを作成"""
    separator = ttk.Separator(parent, orient=orient)
    return separator

def create_spacer(parent, height: int = 10):
    """スペーサーを作成"""
    spacer = ttk.Frame(parent, height=height)
    spacer.pack_propagate(False)
    return spacer