# -*- coding: utf-8 -*-
"""
統一UIコンポーネントシステム
全タブで一貫したUIを提供
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.font_manager import font_manager
except ImportError:
    font_manager = None

class UnifiedTheme:
    """統一テーマ設定"""
    
    # カラーパレット
    COLORS = {
        'primary': '#2E86AB',      # メインブルー
        'secondary': '#A23B72',    # アクセントピンク
        'success': '#F18F01',      # 成功オレンジ
        'warning': '#C73E1D',      # 警告レッド
        'info': '#4A90E2',         # 情報ブルー
        'light': '#F8F9FA',        # ライトグレー
        'dark': '#343A40',         # ダークグレー
        'white': '#FFFFFF',        # ホワイト
        'border': '#DEE2E6',       # ボーダーグレー
        'hover': '#E9ECEF',        # ホバーグレー
        'selected': '#CCE5FF',     # 選択ブルー
        'disabled': '#6C757D'      # 無効グレー
    }
    
    # フォント設定
    FONTS = {
        'default': ('Arial', 9),
        'heading': ('Arial', 12, 'bold'),
        'subheading': ('Arial', 10, 'bold'),
        'small': ('Arial', 8),
        'button': ('Arial', 9, 'bold'),
        'monospace': ('Courier New', 9)
    }
    
    @classmethod
    def get_font(cls, font_type='default'):
        """フォントを取得"""
        if font_manager and hasattr(font_manager, 'get_font_family'):
            family = font_manager.get_font_family()
            if font_type in cls.FONTS:
                font_config = list(cls.FONTS[font_type])
                font_config[0] = family
                return tuple(font_config)
        
        return cls.FONTS.get(font_type, cls.FONTS['default'])

class UnifiedButton(tk.Button):
    """統一ボタンコンポーネント"""
    
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # スタイル設定
        styles = {
            'primary': {
                'bg': UnifiedTheme.COLORS['primary'],
                'fg': UnifiedTheme.COLORS['white'],
                'activebackground': '#1E5F7A',
                'activeforeground': UnifiedTheme.COLORS['white']
            },
            'secondary': {
                'bg': UnifiedTheme.COLORS['secondary'],
                'fg': UnifiedTheme.COLORS['white'],
                'activebackground': '#7A2B52',
                'activeforeground': UnifiedTheme.COLORS['white']
            },
            'success': {
                'bg': UnifiedTheme.COLORS['success'],
                'fg': UnifiedTheme.COLORS['white'],
                'activebackground': '#D17A01',
                'activeforeground': UnifiedTheme.COLORS['white']
            },
            'warning': {
                'bg': UnifiedTheme.COLORS['warning'],
                'fg': UnifiedTheme.COLORS['white'],
                'activebackground': '#A02E1D',
                'activeforeground': UnifiedTheme.COLORS['white']
            },
            'light': {
                'bg': UnifiedTheme.COLORS['light'],
                'fg': UnifiedTheme.COLORS['dark'],
                'activebackground': UnifiedTheme.COLORS['hover'],
                'activeforeground': UnifiedTheme.COLORS['dark']
            }
        }
        
        style_config = styles.get(style, styles['primary'])
        
        # デフォルト設定
        default_config = {
            'font': UnifiedTheme.get_font('button'),
            'relief': 'flat',
            'bd': 0,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }
        
        # 設定をマージ
        config = {**default_config, **style_config, **kwargs}
        
        super().__init__(parent, text=text, command=command, **config)
        
        # ホバー効果
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self.original_bg = config['bg']
        self.hover_bg = config['activebackground']
    
    def _on_enter(self, event):
        """マウスホバー時"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """マウスリーブ時"""
        self.config(bg=self.original_bg)

class UnifiedFrame(tk.Frame):
    """統一フレームコンポーネント"""
    
    def __init__(self, parent, style="default", **kwargs):
        styles = {
            'default': {
                'bg': UnifiedTheme.COLORS['white'],
                'relief': 'flat'
            },
            'card': {
                'bg': UnifiedTheme.COLORS['white'],
                'relief': 'solid',
                'bd': 1,
                'highlightbackground': UnifiedTheme.COLORS['border'],
                'highlightthickness': 1
            },
            'sidebar': {
                'bg': UnifiedTheme.COLORS['light'],
                'relief': 'flat'
            }
        }
        
        style_config = styles.get(style, styles['default'])
        config = {**style_config, **kwargs}
        
        super().__init__(parent, **config)

class UnifiedLabel(tk.Label):
    """統一ラベルコンポーネント"""
    
    def __init__(self, parent, text="", style="default", **kwargs):
        styles = {
            'default': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['dark'],
                'font': UnifiedTheme.get_font('default')
            },
            'heading': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['dark'],
                'font': UnifiedTheme.get_font('heading')
            },
            'subheading': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['dark'],
                'font': UnifiedTheme.get_font('subheading')
            },
            'small': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['disabled'],
                'font': UnifiedTheme.get_font('small')
            },
            'success': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['success'],
                'font': UnifiedTheme.get_font('default')
            },
            'warning': {
                'bg': UnifiedTheme.COLORS['white'],
                'fg': UnifiedTheme.COLORS['warning'],
                'font': UnifiedTheme.get_font('default')
            }
        }
        
        style_config = styles.get(style, styles['default'])
        config = {**style_config, **kwargs}
        
        super().__init__(parent, text=text, **config)

class UnifiedEntry(tk.Entry):
    """統一入力フィールドコンポーネント"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        default_config = {
            'font': UnifiedTheme.get_font('default'),
            'relief': 'solid',
            'bd': 1,
            'highlightthickness': 1,
            'highlightcolor': UnifiedTheme.COLORS['primary'],
            'highlightbackground': UnifiedTheme.COLORS['border']
        }
        
        config = {**default_config, **kwargs}
        super().__init__(parent, **config)
        
        # プレースホルダー機能
        if placeholder:
            self.placeholder = placeholder
            self.placeholder_color = UnifiedTheme.COLORS['disabled']
            self.default_color = UnifiedTheme.COLORS['dark']
            
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """フォーカス取得時"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)
    
    def _on_focus_out(self, event):
        """フォーカス喪失時"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

class UnifiedListbox(tk.Listbox):
    """統一リストボックスコンポーネント"""
    
    def __init__(self, parent, **kwargs):
        default_config = {
            'font': UnifiedTheme.get_font('default'),
            'relief': 'solid',
            'bd': 1,
            'highlightthickness': 0,
            'selectbackground': UnifiedTheme.COLORS['selected'],
            'selectforeground': UnifiedTheme.COLORS['dark'],
            'activestyle': 'none'
        }
        
        config = {**default_config, **kwargs}
        super().__init__(parent, **config)

class UnifiedText(tk.Text):
    """統一テキストエリアコンポーネント"""
    
    def __init__(self, parent, **kwargs):
        default_config = {
            'font': UnifiedTheme.get_font('default'),
            'relief': 'solid',
            'bd': 1,
            'highlightthickness': 1,
            'highlightcolor': UnifiedTheme.COLORS['primary'],
            'highlightbackground': UnifiedTheme.COLORS['border'],
            'wrap': tk.WORD,
            'padx': 5,
            'pady': 5
        }
        
        config = {**default_config, **kwargs}
        super().__init__(parent, **config)

class UnifiedScrollbar(ttk.Scrollbar):
    """統一スクロールバーコンポーネント"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class UnifiedNotification:
    """統一通知システム"""
    
    @staticmethod
    def show_success(parent, title, message):
        """成功通知"""
        messagebox.showinfo(title, message, parent=parent)
    
    @staticmethod
    def show_warning(parent, title, message):
        """警告通知"""
        messagebox.showwarning(title, message, parent=parent)
    
    @staticmethod
    def show_error(parent, title, message):
        """エラー通知"""
        messagebox.showerror(title, message, parent=parent)
    
    @staticmethod
    def ask_confirmation(parent, title, message):
        """確認ダイアログ"""
        return messagebox.askyesno(title, message, parent=parent)

class UnifiedCard(UnifiedFrame):
    """カード型コンポーネント"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, style="card", **kwargs)
        
        if title:
            title_label = UnifiedLabel(self, text=title, style="subheading")
            title_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # 区切り線
            separator = tk.Frame(self, height=1, bg=UnifiedTheme.COLORS['border'])
            separator.pack(fill="x", padx=10, pady=(0, 10))

class UnifiedToolbar(UnifiedFrame):
    """ツールバーコンポーネント"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="sidebar", **kwargs)
        self.pack(fill="x", padx=5, pady=5)
    
    def add_button(self, text, command, style="light"):
        """ボタンを追加"""
        btn = UnifiedButton(self, text=text, command=command, style=style)
        btn.pack(side="left", padx=2)
        return btn
    
    def add_separator(self):
        """区切り線を追加"""
        separator = tk.Frame(self, width=1, bg=UnifiedTheme.COLORS['border'])
        separator.pack(side="left", fill="y", padx=5)

# 使用例とテスト用のサンプル
if __name__ == "__main__":
    root = tk.Tk()
    root.title("統一UIコンポーネント - テスト")
    root.geometry("600x400")
    
    # メインフレーム
    main_frame = UnifiedFrame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ヘッダー
    header = UnifiedLabel(main_frame, text="統一UIコンポーネント テスト", style="heading")
    header.pack(anchor="w", pady=(0, 10))
    
    # カード
    card = UnifiedCard(main_frame, title="サンプルカード")
    card.pack(fill="x", pady=5)
    
    # ボタン群
    button_frame = UnifiedFrame(card)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    UnifiedButton(button_frame, text="Primary", style="primary").pack(side="left", padx=2)
    UnifiedButton(button_frame, text="Secondary", style="secondary").pack(side="left", padx=2)
    UnifiedButton(button_frame, text="Success", style="success").pack(side="left", padx=2)
    UnifiedButton(button_frame, text="Warning", style="warning").pack(side="left", padx=2)
    
    # 入力フィールド
    entry = UnifiedEntry(card, placeholder="プレースホルダーテキスト")
    entry.pack(fill="x", padx=10, pady=5)
    
    root.mainloop()