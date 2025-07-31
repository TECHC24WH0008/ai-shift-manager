# -*- coding: utf-8 -*-
"""
カレンダータブ
月間カレンダー表示とシフト管理 - 統一UI版
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedCard, 
    UnifiedListbox, UnifiedTheme
)

class CalendarTab(BaseTab):
    """カレンダータブクラス - 統一UI版"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        self.current_date = datetime.now()
        self.selected_date = None
        
        # カレンダーウィジェット
        self.calendar_frame = None
        self.month_label = None
        self.calendar_grid = None
        self.day_buttons = {}
        
        # シフト表示エリア
        self.shift_listbox = None
        self.selected_date_label = None
        
        super().__init__(parent_frame, "📅 カレンダー")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("◀ 前月", self.prev_month, "secondary")
        self.toolbar.add_button("今月", self.goto_current_month, "primary")
        self.toolbar.add_button("次月 ▶", self.next_month, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("➕ シフト追加", self.add_shift, "success")
        self.toolbar.add_button("✏️ 編集", self.edit_shift, "light")
        self.toolbar.add_button("🗑️ 削除", self.delete_shift, "warning")
    
    def create_content(self):
        """カレンダーコンテンツを作成"""
        # メインコンテナ
        main_container = UnifiedFrame(self.content_frame)
        main_container.pack(fill="both", expand=True)
        
        # 左側: カレンダーカード
        calendar_card = UnifiedCard(main_container, title="📅 月間カレンダー")
        calendar_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # 月移動コントロール
        nav_container = UnifiedFrame(calendar_card)
        nav_container.pack(fill="x", padx=10, pady=10)
        
        UnifiedButton(nav_container, text="◀", command=self.prev_month, style="light").pack(side="left")
        
        self.month_label = UnifiedLabel(nav_container, text="", style="heading")
        self.month_label.pack(side="left", expand=True)
        
        UnifiedButton(nav_container, text="▶", command=self.next_month, style="light").pack(side="right")
        
        # カレンダーグリッド
        self.calendar_frame = UnifiedFrame(calendar_card)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 右側: シフト詳細カード
        shift_card = UnifiedCard(main_container, title="🕐 シフト詳細")
        shift_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # 選択日表示
        self.selected_date_label = UnifiedLabel(
            shift_card, 
            text="📅 日付を選択してください", 
            style="subheading"
        )
        self.selected_date_label.pack(padx=10, pady=(10, 5))
        
        # シフト一覧
        self.shift_listbox = UnifiedListbox(shift_card, height=15)
        self.shift_listbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # シフト操作ボタン
        button_container = UnifiedFrame(shift_card)
        button_container.pack(fill="x", padx=10, pady=(0, 10))
        
        UnifiedButton(button_container, text="➕ 追加", command=self.add_shift, style="success").pack(side="left", padx=(0, 5))
        UnifiedButton(button_container, text="✏️ 編集", command=self.edit_shift, style="secondary").pack(side="left", padx=5)
        UnifiedButton(button_container, text="🗑️ 削除", command=self.delete_shift, style="warning").pack(side="left", padx=5)
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("カレンダーを読み込み中...")
        self.update_calendar()
        self.update_status("カレンダー読み込み完了")
    
    def update_calendar(self):
        """カレンダーを更新"""
        # 月ラベル更新
        month_text = f"{self.current_date.year}年 {self.current_date.month}月"
        if self.month_label:
            self.month_label.config(text=month_text)
        
        # 既存のカレンダーをクリア
        if self.calendar_frame:
            for widget in self.calendar_frame.winfo_children():
                widget.destroy()
        
        self.day_buttons = {}
        
        # 曜日ヘッダー
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        weekday_colors = ['#424242', '#424242', '#424242', '#424242', '#424242', '#7B1FA2', '#C62828']
        
        for i, (day, color) in enumerate(zip(weekdays, weekday_colors)):
            label = UnifiedLabel(self.calendar_frame, text=day, style="subheading")
            label.config(fg=color)
            label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # カレンダーの日付を取得
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # 日付ボタンを配置
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                
                # 日付ボタン作成
                date_obj = datetime(self.current_date.year, self.current_date.month, day)
                
                btn = tk.Button(
                    self.calendar_frame,
                    text=str(day),
                    width=4,
                    height=2,
                    command=lambda d=date_obj: self.select_date(d),
                    relief=tk.RAISED,
                    bd=1,
                    font=('Arial', 9)
                )
                
                # 今日の日付をハイライト
                if date_obj.date() == datetime.now().date():
                    btn.config(bg=UnifiedTheme.COLORS['info'], fg=UnifiedTheme.COLORS['white'], font=('Arial', 9, 'bold'))
                # 土日の色分け
                elif date_obj.weekday() == 5:  # 土曜日
                    btn.config(bg="#F3E5F5", fg="#7B1FA2")
                elif date_obj.weekday() == 6:  # 日曜日
                    btn.config(bg="#FFEBEE", fg="#C62828")
                else:
                    btn.config(bg=UnifiedTheme.COLORS['light'], fg=UnifiedTheme.COLORS['dark'])
                
                # ホバー効果
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=UnifiedTheme.COLORS['hover']))
                btn.bind("<Leave>", lambda e, b=btn, d=date_obj: self._restore_button_color(b, d))
                
                btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                self.day_buttons[day] = btn
        
        # グリッドの重み設定
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def _restore_button_color(self, btn, date_obj):
        """ボタンの色を元に戻す"""
        if date_obj.date() == datetime.now().date():
            btn.config(bg=UnifiedTheme.COLORS['info'])
        elif date_obj.weekday() == 5:
            btn.config(bg="#F3E5F5")
        elif date_obj.weekday() == 6:
            btn.config(bg="#FFEBEE")
        else:
            btn.config(bg=UnifiedTheme.COLORS['light'])
    
    def prev_month(self):
        """前月に移動"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
        self.update_status(f"{self.current_date.year}年{self.current_date.month}月に移動")
    
    def next_month(self):
        """次月に移動"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
        self.update_status(f"{self.current_date.year}年{self.current_date.month}月に移動")
    
    def goto_current_month(self):
        """今月に移動"""
        self.current_date = datetime.now()
        self.update_calendar()
        self.update_status("今月に移動しました")
    
    def select_date(self, date_obj):
        """日付を選択"""
        self.selected_date = date_obj
        
        # 選択日をハイライト
        for day, btn in self.day_buttons.items():
            if day == date_obj.day:
                btn.config(relief=tk.SUNKEN, bg=UnifiedTheme.COLORS['selected'])
            else:
                # 元の色に戻す
                date_check = datetime(self.current_date.year, self.current_date.month, day)
                if date_check.date() == datetime.now().date():
                    btn.config(relief=tk.RAISED, bg=UnifiedTheme.COLORS['info'])
                elif date_check.weekday() == 5:
                    btn.config(relief=tk.RAISED, bg="#F3E5F5")
                elif date_check.weekday() == 6:
                    btn.config(relief=tk.RAISED, bg="#FFEBEE")
                else:
                    btn.config(relief=tk.RAISED, bg=UnifiedTheme.COLORS['light'])
        
        # 選択日のシフト情報を表示
        self.update_shift_display()
        
        date_str = date_obj.strftime("%Y年%m月%d日")
        self.update_status(f"{date_str}を選択しました")
    
    def update_shift_display(self):
        """選択日のシフト表示を更新"""
        if not self.selected_date or not self.shift_listbox:
            return
        
        # 選択日ラベル更新
        weekdays_jp = ['月', '火', '水', '木', '金', '土', '日']
        weekday_jp = weekdays_jp[self.selected_date.weekday()]
        date_str = f"{self.selected_date.strftime('%Y年%m月%d日')} ({weekday_jp})"
        self.selected_date_label.config(text=f"📅 {date_str}")
        
        # シフト一覧をクリア
        self.shift_listbox.delete(0, tk.END)
        
        # サンプルシフトデータ（実際はdata_managerから取得）
        sample_shifts = [
            "09:00-17:00 田中太郎 (営業部・リーダー)",
            "10:00-18:00 佐藤花子 (営業部・スタッフ)",
            "13:00-21:00 山田美咲 (営業部・スタッフ)",
            "17:00-21:00 高橋健太 (営業部・スタッフ)"
        ]
        
        # 土日は異なるシフトパターン
        if self.selected_date.weekday() >= 5:  # 土日
            sample_shifts = [
                "10:00-18:00 佐藤花子 (営業部・リーダー)",
                "12:00-20:00 山田美咲 (営業部・スタッフ)",
                "14:00-18:00 鈴木次郎 (営業部・パート)"
            ]
        
        for shift in sample_shifts:
            self.shift_listbox.insert(tk.END, shift)
        
        if not sample_shifts:
            self.shift_listbox.insert(tk.END, "📭 この日のシフトはありません")
    
    def add_shift(self):
        """シフトを追加"""
        if not self.selected_date:
            self.show_warning("日付選択", "シフトを追加する日付を選択してください")
            return
        
        date_str = self.selected_date.strftime("%Y年%m月%d日")
        self.update_status(f"{date_str}にシフト追加中...")
        
        # TODO: シフト追加ダイアログを実装
        self.show_success("シフト追加", f"{date_str}のシフト追加機能は実装中です\n\n今後のアップデートで対応予定です")
    
    def edit_shift(self):
        """シフトを編集"""
        if not self.shift_listbox:
            return
        
        selection = self.shift_listbox.curselection()
        if not selection:
            self.show_warning("選択エラー", "編集するシフトを選択してください")
            return
        
        selected_shift = self.shift_listbox.get(selection[0])
        if "この日のシフトはありません" in selected_shift:
            self.show_warning("編集エラー", "編集可能なシフトがありません")
            return
        
        self.update_status("シフト編集中...")
        # TODO: シフト編集ダイアログを実装
        self.show_success("シフト編集", f"選択したシフトの編集機能は実装中です\n\nシフト: {selected_shift}")
    
    def delete_shift(self):
        """シフトを削除"""
        if not self.shift_listbox:
            return
        
        selection = self.shift_listbox.curselection()
        if not selection:
            self.show_warning("選択エラー", "削除するシフトを選択してください")
            return
        
        selected_shift = self.shift_listbox.get(selection[0])
        if "この日のシフトはありません" in selected_shift:
            self.show_warning("削除エラー", "削除可能なシフトがありません")
            return
        
        if self.ask_confirmation("シフト削除", f"以下のシフトを削除しますか？\n\n{selected_shift}"):
            self.shift_listbox.delete(selection[0])
            self.update_status("シフトを削除しました")
            self.show_success("削除完了", "シフトを削除しました")

# テスト用
if __name__ == "__main__":
    root = tk.Tk()
    root.title("カレンダータブ - テスト")
    root.geometry("1000x700")
    
    tab = CalendarTab(root)
    
    root.mainloop()