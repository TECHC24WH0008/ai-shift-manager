# -*- coding: utf-8 -*-
"""
完全オフライン対応モダンUI
外部依存なしのtkinterベース高品質インターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

class OfflineModernUI:
    """完全オフライン対応のモダンUI"""
    
    def __init__(self, root):
        self.root = root
        
        # カラーパレット（外部CSS不要）
        self.colors = {
            'primary': '#2563EB',      # ブルー
            'secondary': '#10B981',    # グリーン  
            'accent': '#F59E0B',       # オレンジ
            'danger': '#EF4444',       # レッド
            'warning': '#F59E0B',      # イエロー
            'success': '#10B981',      # グリーン
            'light': '#F8FAFC',        # ライトグレー
            'dark': '#1E293B',         # ダークグレー
            'white': '#FFFFFF',
            'gray': '#6B7280'
        }
        
        # フォント設定
        self.fonts = {
            'title': ('Segoe UI', 18, 'bold'),
            'heading': ('Segoe UI', 14, 'bold'),
            'body': ('Segoe UI', 10),
            'small': ('Segoe UI', 9),
            'button': ('Segoe UI', 10, 'bold')
        }
        
        # テーマ設定を最後に実行
        self.setup_modern_theme()
    
    def setup_modern_theme(self):
        """モダンテーマ設定（完全オフライン）"""
        style = ttk.Style()
        
        # 利用可能なテーマから最適なものを選択
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # カスタムスタイル定義
        self._configure_custom_styles(style)
    
    def _configure_custom_styles(self, style):
        """カスタムスタイル設定"""
        # ボタンスタイル
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['button'])
        
        style.map('Primary.TButton',
                 background=[('active', '#1D4ED8')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
        # ラベルスタイル
        style.configure('Title.TLabel',
                       font=self.fonts['title'],
                       foreground=self.colors['dark'])
        
        style.configure('Heading.TLabel',
                       font=self.fonts['heading'],
                       foreground=self.colors['dark'])
        
        # フレームスタイル
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='solid',
                       borderwidth=1)
    
    def create_modern_card(self, parent, title: str = None, padding: int = 15) -> ttk.Frame:
        """モダンカード作成"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=padding)
        
        if title:
            title_label = ttk.Label(card, text=title, style='Heading.TLabel')
            title_label.pack(anchor=tk.W, pady=(0, 10))
        
        return card
    
    def create_icon_button(self, parent, text: str, icon: str, command=None, 
                          style: str = 'primary') -> tk.Button:
        """アイコン付きボタン作成（完全オフライン）"""
        
        # スタイル別色設定
        style_colors = {
            'primary': (self.colors['primary'], 'white'),
            'success': (self.colors['success'], 'white'),
            'danger': (self.colors['danger'], 'white'),
            'secondary': (self.colors['light'], self.colors['dark'])
        }
        
        bg_color, fg_color = style_colors.get(style, style_colors['primary'])
        
        # tkinter.Buttonを使用（完全制御可能）
        button = tk.Button(
            parent,
            text=f"{icon} {text}",
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=self.fonts['button'],
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        
        # ホバー効果
        def on_enter(e):
            button.config(bg=self._darken_color(bg_color))
        
        def on_leave(e):
            button.config(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_status_indicator(self, parent, status: str, message: str) -> ttk.Frame:
        """ステータスインジケーター作成"""
        frame = ttk.Frame(parent)
        
        # ステータス別設定
        status_config = {
            'success': ('🟢', self.colors['success']),
            'warning': ('🟡', self.colors['warning']),
            'error': ('🔴', self.colors['danger']),
            'info': ('🔵', self.colors['primary'])
        }
        
        icon, color = status_config.get(status, status_config['info'])
        
        # アイコンラベル
        icon_label = tk.Label(frame, text=icon, font=('Segoe UI', 12))
        icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # メッセージラベル
        msg_label = tk.Label(frame, text=message, font=self.fonts['body'], fg=color)
        msg_label.pack(side=tk.LEFT)
        
        return frame
    
    def create_progress_card(self, parent, title: str, current: int, total: int) -> ttk.Frame:
        """プログレスカード作成"""
        card = self.create_modern_card(parent, title)
        
        # プログレスバー
        progress_frame = ttk.Frame(card)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        progress_bar.pack(fill=tk.X)
        progress_bar['value'] = (current / total * 100) if total > 0 else 0
        
        # 数値表示
        value_label = ttk.Label(card, text=f"{current} / {total}", font=self.fonts['heading'])
        value_label.pack()
        
        return card
    
    def create_data_table(self, parent, columns: List[str], data: List[List]) -> ttk.Treeview:
        """データテーブル作成"""
        # フレーム作成
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview作成
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # 列設定
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        # データ挿入
        for row in data:
            tree.insert('', tk.END, values=row)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return tree
    
    def create_notification_popup(self, title: str, message: str, 
                                notification_type: str = 'info', duration: int = 3000):
        """通知ポップアップ作成（完全オフライン）"""
        
        # 通知ウィンドウ作成
        notification = tk.Toplevel(self.root)
        notification.title(title)
        notification.geometry("400x150")
        notification.resizable(False, False)
        
        # 画面右下に配置
        notification.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() - 420,
            self.root.winfo_screenheight() - 200
        ))
        
        # 常に最前面
        notification.attributes('-topmost', True)
        
        # 背景色設定
        type_colors = {
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['danger'],
            'info': self.colors['primary']
        }
        
        bg_color = type_colors.get(notification_type, type_colors['info'])
        notification.configure(bg=bg_color)
        
        # アイコン
        icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        }
        
        icon = icons.get(notification_type, icons['info'])
        
        # コンテンツ
        content_frame = tk.Frame(notification, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # アイコンとタイトル
        header_frame = tk.Frame(content_frame, bg=bg_color)
        header_frame.pack(fill=tk.X)
        
        icon_label = tk.Label(header_frame, text=icon, font=('Segoe UI', 16), 
                             bg=bg_color, fg='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(header_frame, text=title, font=self.fonts['heading'],
                              bg=bg_color, fg='white')
        title_label.pack(side=tk.LEFT)
        
        # メッセージ
        msg_label = tk.Label(content_frame, text=message, font=self.fonts['body'],
                            bg=bg_color, fg='white', wraplength=350)
        msg_label.pack(pady=(10, 0))
        
        # 自動閉じる
        def auto_close():
            try:
                notification.destroy()
            except:
                pass
        
        notification.after(duration, auto_close)
        
        # クリックで閉じる
        def close_on_click(event):
            notification.destroy()
        
        notification.bind("<Button-1>", close_on_click)
        content_frame.bind("<Button-1>", close_on_click)
        
        return notification
    
    def _darken_color(self, color: str) -> str:
        """色を暗くする（ホバー効果用）"""
        # 簡易的な色変換
        color_map = {
            self.colors['primary']: '#1D4ED8',
            self.colors['success']: '#059669',
            self.colors['danger']: '#DC2626',
            self.colors['warning']: '#D97706'
        }
        return color_map.get(color, color)
    
    def show_loading_dialog(self, title: str = "処理中...", message: str = "しばらくお待ちください"):
        """ローディングダイアログ表示"""
        loading = tk.Toplevel(self.root)
        loading.title(title)
        loading.geometry("300x150")
        loading.resizable(False, False)
        
        # 中央配置
        loading.geometry("+%d+%d" % (
            (self.root.winfo_screenwidth() // 2) - 150,
            (self.root.winfo_screenheight() // 2) - 75
        ))
        
        loading.transient(self.root)
        loading.grab_set()
        
        # コンテンツ
        content_frame = ttk.Frame(loading, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # ローディングアニメーション（テキストベース）
        self.loading_text = tk.StringVar(value="⏳ 処理中")
        loading_label = ttk.Label(content_frame, textvariable=self.loading_text, 
                                 font=self.fonts['heading'])
        loading_label.pack(pady=(0, 10))
        
        # メッセージ
        msg_label = ttk.Label(content_frame, text=message, font=self.fonts['body'])
        msg_label.pack()
        
        # アニメーション
        self.loading_animation_active = True
        self._animate_loading()
        
        return loading
    
    def _animate_loading(self):
        """ローディングアニメーション"""
        if hasattr(self, 'loading_animation_active') and self.loading_animation_active:
            current = self.loading_text.get()
            if current.endswith("..."):
                self.loading_text.set("⏳ 処理中")
            elif current.endswith(".."):
                self.loading_text.set("⏳ 処理中...")
            elif current.endswith("."):
                self.loading_text.set("⏳ 処理中..")
            else:
                self.loading_text.set("⏳ 処理中.")
            
            self.root.after(500, self._animate_loading)
    
    def hide_loading_dialog(self, loading_dialog):
        """ローディングダイアログを閉じる"""
        self.loading_animation_active = False
        loading_dialog.destroy()


# 使用例
def demo_modern_ui():
    """モダンUI デモ"""
    root = tk.Tk()
    root.title("🚀 完全オフライン モダンUI デモ")
    root.geometry("800x600")
    
    # モダンUI初期化
    modern_ui = OfflineModernUI(root)
    
    # メインフレーム
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # タイトル
    title_label = ttk.Label(main_frame, text="🚀 完全オフライン AI Shift Manager", 
                           style='Title.TLabel')
    title_label.pack(pady=(0, 20))
    
    # カード例
    card1 = modern_ui.create_modern_card(main_frame, "📊 システム状況")
    card1.pack(fill=tk.X, pady=(0, 10))
    
    # ステータス表示
    status1 = modern_ui.create_status_indicator(card1, 'success', 'データベース接続済み')
    status1.pack(anchor=tk.W, pady=2)
    
    status2 = modern_ui.create_status_indicator(card1, 'info', 'タイムカードデータ読み込み完了')
    status2.pack(anchor=tk.W, pady=2)
    
    # ボタン例
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=20)
    
    btn1 = modern_ui.create_icon_button(button_frame, "緊急代替検索", "🔥", 
                                       command=lambda: modern_ui.create_notification_popup(
                                           "検索完了", "代替候補3名が見つかりました", "success"))
    btn1.pack(side=tk.LEFT, padx=(0, 10))
    
    btn2 = modern_ui.create_icon_button(button_frame, "データ読み込み", "📊", style='secondary')
    btn2.pack(side=tk.LEFT, padx=(0, 10))
    
    btn3 = modern_ui.create_icon_button(button_frame, "設定", "⚙️", style='secondary')
    btn3.pack(side=tk.LEFT)
    
    root.mainloop()

if __name__ == "__main__":
    demo_modern_ui()