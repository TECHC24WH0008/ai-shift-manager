# -*- coding: utf-8 -*-
"""
カレンダー管理機能
月間カレンダー表示とシフト管理
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class CalendarManager:
    """カレンダー管理クラス"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.current_date = datetime.now()
        self.selected_date = None
        
        # カレンダーウィジェット
        self.calendar_frame = None
        self.month_label = None
        self.calendar_grid = None
        self.day_buttons = {}
        
        # シフト表示エリア
        self.shift_frame = None
        self.shift_listbox = None
        
        self.create_calendar_ui()
    
    def create_calendar_ui(self):
        """カレンダーUIを作成"""
        # メインコンテナ
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左側: カレンダー
        calendar_container = ttk.LabelFrame(main_container, text="📅 カレンダー", padding=10)
        calendar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 月移動コントロール
        nav_frame = ttk.Frame(calendar_container)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        prev_btn = ttk.Button(nav_frame, text="◀", command=self.prev_month)
        prev_btn.pack(side=tk.LEFT)
        
        self.month_label = ttk.Label(nav_frame, text="", font=("Segoe UI", 14, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        next_btn = ttk.Button(nav_frame, text="▶", command=self.next_month)
        next_btn.pack(side=tk.RIGHT)
        
        # カレンダーグリッド
        self.calendar_frame = ttk.Frame(calendar_container)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # 右側: 選択日のシフト詳細
        shift_container = ttk.LabelFrame(main_container, text="🕐 シフト詳細", padding=10)
        shift_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 選択日表示
        self.selected_date_label = ttk.Label(shift_container, text="日付を選択してください", 
                                           font=("Segoe UI", 12, "bold"))
        self.selected_date_label.pack(pady=(0, 10))
        
        # シフト一覧
        self.shift_listbox = tk.Listbox(shift_container, height=15)
        self.shift_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ボタンフレーム
        button_frame = ttk.Frame(shift_container)
        button_frame.pack(fill=tk.X)
        
        add_shift_btn = ttk.Button(button_frame, text="シフト追加", command=self.add_shift)
        add_shift_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_shift_btn = ttk.Button(button_frame, text="編集", command=self.edit_shift)
        edit_shift_btn.pack(side=tk.LEFT, padx=5)
        
        delete_shift_btn = ttk.Button(button_frame, text="削除", command=self.delete_shift)
        delete_shift_btn.pack(side=tk.LEFT, padx=5)
        
        # 初期表示
        self.update_calendar()
    
    def update_calendar(self):
        """カレンダーを更新"""
        # 月ラベル更新
        month_text = f"{self.current_date.year}年 {self.current_date.month}月"
        self.month_label.config(text=month_text)
        
        # 既存のカレンダーをクリア
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        self.day_buttons = {}
        
        # 曜日ヘッダー
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        for i, day in enumerate(weekdays):
            label = ttk.Label(self.calendar_frame, text=day, font=("Segoe UI", 10, "bold"))
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
                    bd=1
                )
                
                # 今日の日付をハイライト
                if date_obj.date() == datetime.now().date():
                    btn.config(bg="#E3F2FD", fg="#1976D2", font=("Segoe UI", 9, "bold"))
                
                # 土日の色分け
                elif date_obj.weekday() == 5:  # 土曜日
                    btn.config(bg="#F3E5F5", fg="#7B1FA2")
                elif date_obj.weekday() == 6:  # 日曜日
                    btn.config(bg="#FFEBEE", fg="#C62828")
                else:
                    btn.config(bg="#FAFAFA", fg="#424242")
                
                btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                self.day_buttons[day] = btn
        
        # グリッドの重み設定
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def prev_month(self):
        """前月に移動"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """次月に移動"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def select_date(self, date_obj):
        """日付を選択"""
        self.selected_date = date_obj
        
        # 選択日をハイライト
        for day, btn in self.day_buttons.items():
            if day == date_obj.day:
                btn.config(relief=tk.SUNKEN, bg="#BBDEFB")
            else:
                # 元の色に戻す
                date_check = datetime(self.current_date.year, self.current_date.month, day)
                if date_check.date() == datetime.now().date():
                    btn.config(relief=tk.RAISED, bg="#E3F2FD")
                elif date_check.weekday() == 5:
                    btn.config(relief=tk.RAISED, bg="#F3E5F5")
                elif date_check.weekday() == 6:
                    btn.config(relief=tk.RAISED, bg="#FFEBEE")
                else:
                    btn.config(relief=tk.RAISED, bg="#FAFAFA")
        
        # 選択日のシフト情報を表示
        self.update_shift_display()
    
    def update_shift_display(self):
        """選択日のシフト表示を更新"""
        if not self.selected_date:
            return
        
        # 選択日ラベル更新
        date_str = self.selected_date.strftime("%Y年%m月%d日 (%a)")
        self.selected_date_label.config(text=f"📅 {date_str}")
        
        # シフト一覧をクリア
        self.shift_listbox.delete(0, tk.END)
        
        # サンプルシフトデータ（実際はdata_managerから取得）
        sample_shifts = [
            "09:00-17:00 田中太郎 (営業部)",
            "10:00-18:00 佐藤花子 (営業部)",
            "13:00-21:00 山田美咲 (営業部)",
            "17:00-21:00 高橋健太 (営業部)"
        ]
        
        for shift in sample_shifts:
            self.shift_listbox.insert(tk.END, shift)
        
        if not sample_shifts:
            self.shift_listbox.insert(tk.END, "この日のシフトはありません")
    
    def add_shift(self):
        """シフトを追加"""
        if not self.selected_date:
            tk.messagebox.showwarning("警告", "日付を選択してください")
            return
        
        # シフト追加ダイアログ（簡易版）
        tk.messagebox.showinfo("情報", "シフト追加機能は実装中です")
    
    def edit_shift(self):
        """シフトを編集"""
        selection = self.shift_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("警告", "編集するシフトを選択してください")
            return
        
        tk.messagebox.showinfo("情報", "シフト編集機能は実装中です")
    
    def delete_shift(self):
        """シフトを削除"""
        selection = self.shift_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("警告", "削除するシフトを選択してください")
            return
        
        result = tk.messagebox.askyesno("確認", "選択したシフトを削除しますか？")
        if result:
            self.shift_listbox.delete(selection[0])