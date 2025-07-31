# -*- coding: utf-8 -*-
"""
モダンUIコンポーネント
tkinterベースの美しく使いやすいUI要素
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, List, Any, Callable, Optional
import math

class ModernColors:
    """モダンカラーパレット"""
    
    # メインカラー
    PRIMARY = "#2563EB"      # 青
    SECONDARY = "#10B981"    # 緑
    ACCENT = "#F59E0B"       # オレンジ
    DANGER = "#EF4444"       # 赤
    WARNING = "#F59E0B"      # 黄
    SUCCESS = "#10B981"      # 緑
    
    # ニュートラル
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F8FAFC"
    GRAY = "#64748B"
    DARK_GRAY = "#334155"
    BLACK = "#0F172A"
    
    # 背景
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F1F5F9"
    BG_CARD = "#FFFFFF"
    
    # ボーダー
    BORDER_LIGHT = "#E2E8F0"
    BORDER_MEDIUM = "#CBD5E1"
    BORDER_DARK = "#94A3B8"

class ModernButton(tk.Button):
    """モダンなボタンコンポーネント"""
    
    def __init__(self, parent, text="", command=None, style="primary", 
                 icon="", size="medium", **kwargs):
        
        # スタイル設定
        styles = {
            "primary": {
                "bg": ModernColors.PRIMARY,
                "fg": ModernColors.WHITE,
                "activebackground": "#1D4ED8",
                "activeforeground": ModernColors.WHITE
            },
            "secondary": {
                "bg": ModernColors.BG_SECONDARY,
                "fg": ModernColors.DARK_GRAY,
                "activebackground": "#E2E8F0",
                "activeforeground": ModernColors.DARK_GRAY
            },
            "success": {
                "bg": ModernColors.SUCCESS,
                "fg": ModernColors.WHITE,
                "activebackground": "#059669",
                "activeforeground": ModernColors.WHITE
            },
            "danger": {
                "bg": ModernColors.DANGER,
                "fg": ModernColors.WHITE,
                "activebackground": "#DC2626",
                "activeforeground": ModernColors.WHITE
            }
        }
        
        # サイズ設定
        sizes = {
            "small": {"padx": 12, "pady": 6, "font_size": 9},
            "medium": {"padx": 16, "pady": 8, "font_size": 10},
            "large": {"padx": 20, "pady": 12, "font_size": 12}
        }
        
        style_config = styles.get(style, styles["primary"])
        size_config = sizes.get(size, sizes["medium"])
        
        # アイコン付きテキスト
        display_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            command=command,
            font=("Segoe UI", size_config["font_size"], "normal"),
            relief=tk.FLAT,
            bd=0,
            padx=size_config["padx"],
            pady=size_config["pady"],
            cursor="hand2",
            **style_config,
            **kwargs
        )
        
        # ホバー効果
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self.default_bg = style_config["bg"]
        self.hover_bg = self._darken_color(self.default_bg, 0.1)
    
    def _on_enter(self, event):
        """マウスホバー時"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """マウスリーブ時"""
        self.config(bg=self.default_bg)
    
    def _darken_color(self, color, factor):
        """色を暗くする"""
        try:
            # 簡易的な色変換
            if color.startswith("#"):
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                r = max(0, int(r * (1 - factor)))
                g = max(0, int(g * (1 - factor)))
                b = max(0, int(b * (1 - factor)))
                
                return f"#{r:02x}{g:02x}{b:02x}"
        except:
            pass
        return color

class ModernCard(tk.Frame):
    """モダンなカードコンポーネント"""
    
    def __init__(self, parent, title="", padding=20, **kwargs):
        super().__init__(
            parent,
            bg=ModernColors.BG_CARD,
            relief=tk.FLAT,
            bd=1,
            highlightbackground=ModernColors.BORDER_LIGHT,
            highlightthickness=1,
            **kwargs
        )
        
        # 内部フレーム
        self.content_frame = tk.Frame(self, bg=ModernColors.BG_CARD)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        # タイトル
        if title:
            title_label = tk.Label(
                self.content_frame,
                text=title,
                font=("Segoe UI", 14, "bold"),
                fg=ModernColors.DARK_GRAY,
                bg=ModernColors.BG_CARD
            )
            title_label.pack(anchor=tk.W, pady=(0, 15))
    
    def add_content(self, widget):
        """コンテンツ追加"""
        widget.pack(in_=self.content_frame, fill=tk.X, pady=5)

class ModernAlert(tk.Frame):
    """モダンなアラートコンポーネント"""
    
    def __init__(self, parent, message="", alert_type="info", dismissible=True, **kwargs):
        
        # アラートタイプ別設定
        alert_styles = {
            "info": {
                "bg": "#DBEAFE",
                "fg": "#1E40AF",
                "border": "#3B82F6",
                "icon": "ℹ️"
            },
            "success": {
                "bg": "#D1FAE5",
                "fg": "#065F46",
                "border": "#10B981",
                "icon": "✅"
            },
            "warning": {
                "bg": "#FEF3C7",
                "fg": "#92400E",
                "border": "#F59E0B",
                "icon": "⚠️"
            },
            "danger": {
                "bg": "#FEE2E2",
                "fg": "#991B1B",
                "border": "#EF4444",
                "icon": "❌"
            }
        }
        
        style = alert_styles.get(alert_type, alert_styles["info"])
        
        super().__init__(
            parent,
            bg=style["bg"],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=style["border"],
            highlightthickness=1,
            **kwargs
        )
        
        # 内容フレーム
        content_frame = tk.Frame(self, bg=style["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # アイコンとメッセージ
        icon_label = tk.Label(
            content_frame,
            text=style["icon"],
            font=("Segoe UI", 12),
            bg=style["bg"],
            fg=style["fg"]
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        message_label = tk.Label(
            content_frame,
            text=message,
            font=("Segoe UI", 10),
            bg=style["bg"],
            fg=style["fg"],
            wraplength=400,
            justify=tk.LEFT
        )
        message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 閉じるボタン
        if dismissible:
            close_btn = tk.Button(
                content_frame,
                text="×",
                font=("Segoe UI", 12, "bold"),
                bg=style["bg"],
                fg=style["fg"],
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                command=self.destroy
            )
            close_btn.pack(side=tk.RIGHT)

class ModernProgressBar(tk.Frame):
    """モダンなプログレスバー"""
    
    def __init__(self, parent, width=300, height=8, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0
        
        # キャンバス作成
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=ModernColors.BG_SECONDARY,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 背景バー
        self.bg_bar = self.canvas.create_rectangle(
            0, 0, width, height,
            fill=ModernColors.BG_SECONDARY,
            outline=""
        )
        
        # プログレスバー
        self.progress_bar = self.canvas.create_rectangle(
            0, 0, 0, height,
            fill=ModernColors.PRIMARY,
            outline=""
        )
    
    def set_progress(self, value):
        """プログレス設定（0-100）"""
        self.progress = max(0, min(100, value))
        progress_width = (self.progress / 100) * self.width
        
        self.canvas.coords(
            self.progress_bar,
            0, 0, progress_width, self.height
        )

class ModernListBox(tk.Frame):
    """モダンなリストボックス"""
    
    def __init__(self, parent, items=None, on_select=None, **kwargs):
        super().__init__(parent, bg=ModernColors.BG_CARD, **kwargs)
        
        self.items = items or []
        self.on_select = on_select
        self.selected_index = -1
        
        # スクロール可能フレーム
        self.canvas = tk.Canvas(self, bg=ModernColors.BG_CARD, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=ModernColors.BG_CARD)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # アイテム表示
        self.refresh_items()
    
    def refresh_items(self):
        """アイテム再表示"""
        # 既存アイテムクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # アイテム作成
        for i, item in enumerate(self.items):
            item_frame = tk.Frame(
                self.scrollable_frame,
                bg=ModernColors.BG_CARD,
                cursor="hand2"
            )
            item_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # アイテムラベル
            if isinstance(item, dict):
                text = item.get('text', str(item))
                subtitle = item.get('subtitle', '')
            else:
                text = str(item)
                subtitle = ''
            
            main_label = tk.Label(
                item_frame,
                text=text,
                font=("Segoe UI", 10),
                bg=ModernColors.BG_CARD,
                fg=ModernColors.DARK_GRAY,
                anchor=tk.W
            )
            main_label.pack(fill=tk.X, padx=10, pady=(5, 0))
            
            if subtitle:
                sub_label = tk.Label(
                    item_frame,
                    text=subtitle,
                    font=("Segoe UI", 8),
                    bg=ModernColors.BG_CARD,
                    fg=ModernColors.GRAY,
                    anchor=tk.W
                )
                sub_label.pack(fill=tk.X, padx=10, pady=(0, 5))
            
            # クリックイベント
            def on_click(index=i):
                self.select_item(index)
            
            item_frame.bind("<Button-1>", lambda e, idx=i: self.select_item(idx))
            main_label.bind("<Button-1>", lambda e, idx=i: self.select_item(idx))
            if subtitle:
                sub_label.bind("<Button-1>", lambda e, idx=i: self.select_item(idx))
    
    def select_item(self, index):
        """アイテム選択"""
        self.selected_index = index
        
        # 選択状態の視覚的更新
        for i, widget in enumerate(self.scrollable_frame.winfo_children()):
            if i == index:
                widget.config(bg=ModernColors.PRIMARY)
                for child in widget.winfo_children():
                    child.config(bg=ModernColors.PRIMARY, fg=ModernColors.WHITE)
            else:
                widget.config(bg=ModernColors.BG_CARD)
                for child in widget.winfo_children():
                    child.config(bg=ModernColors.BG_CARD, 
                               fg=ModernColors.DARK_GRAY if child.winfo_class() == 'Label' else ModernColors.GRAY)
        
        # コールバック実行
        if self.on_select and 0 <= index < len(self.items):
            self.on_select(self.items[index], index)
    
    def add_item(self, item):
        """アイテム追加"""
        self.items.append(item)
        self.refresh_items()
    
    def clear_items(self):
        """アイテムクリア"""
        self.items.clear()
        self.refresh_items()

class ModernTooltip:
    """モダンなツールチップ"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """ツールチップ表示"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw,
            text=self.text,
            font=("Segoe UI", 9),
            bg="#2D3748",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """ツールチップ非表示"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None