# -*- coding: utf-8 -*-
"""
欠勤対応管理機能
欠勤者の管理と代替要員の調整
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class AbsenceManager:
    """欠勤対応管理クラス"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        # 欠勤データ
        self.absence_records = []
        self.substitute_suggestions = []
        
        self.create_absence_ui()
    
    def create_absence_ui(self):
        """欠勤対応UIを作成"""
        # メインコンテナ
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部: 欠勤登録
        absence_frame = ttk.LabelFrame(main_container, text="⚠️ 欠勤登録", padding=10)
        absence_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 欠勤登録フォーム
        form_frame = ttk.Frame(absence_frame)
        form_frame.pack(fill=tk.X)
        
        # スタッフ選択
        ttk.Label(form_frame, text="スタッフ:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.staff_combo = ttk.Combobox(form_frame, width=20)
        self.staff_combo.grid(row=0, column=1, padx=(0, 20))
        
        # 日付選択
        ttk.Label(form_frame, text="日付:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.date_entry = ttk.Entry(form_frame, width=15)
        self.date_entry.grid(row=0, column=3, padx=(0, 20))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 理由入力
        ttk.Label(form_frame, text="理由:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.reason_entry = ttk.Entry(form_frame, width=40)
        self.reason_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=(10, 0), padx=(0, 20))
        
        # 登録ボタン
        register_btn = ttk.Button(form_frame, text="欠勤登録", command=self.register_absence)
        register_btn.grid(row=1, column=3, pady=(10, 0))
        
        # 中央: 欠勤一覧と代替候補
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側: 欠勤一覧
        absence_list_frame = ttk.LabelFrame(content_frame, text="📋 欠勤一覧", padding=10)
        absence_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 欠勤リスト
        self.absence_tree = ttk.Treeview(absence_list_frame, columns=('date', 'staff', 'reason', 'status'), show='headings', height=10)
        self.absence_tree.heading('date', text='日付')
        self.absence_tree.heading('staff', text='スタッフ')
        self.absence_tree.heading('reason', text='理由')
        self.absence_tree.heading('status', text='状態')
        
        self.absence_tree.column('date', width=100)
        self.absence_tree.column('staff', width=120)
        self.absence_tree.column('reason', width=150)
        self.absence_tree.column('status', width=80)
        
        self.absence_tree.pack(fill=tk.BOTH, expand=True)
        self.absence_tree.bind('<<TreeviewSelect>>', self.on_absence_select)
        
        # 右側: AI代替候補
        substitute_frame = ttk.LabelFrame(content_frame, text="🤖 AI代替候補", padding=10)
        substitute_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 代替候補リスト
        self.substitute_tree = ttk.Treeview(substitute_frame, columns=('staff', 'score', 'reason'), show='headings', height=8)
        self.substitute_tree.heading('staff', text='候補者')
        self.substitute_tree.heading('score', text='適合度')
        self.substitute_tree.heading('reason', text='推薦理由')
        
        self.substitute_tree.column('staff', width=100)
        self.substitute_tree.column('score', width=80)
        self.substitute_tree.column('reason', width=200)
        
        self.substitute_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 代替候補ボタン
        substitute_btn_frame = ttk.Frame(substitute_frame)
        substitute_btn_frame.pack(fill=tk.X)
        
        analyze_btn = ttk.Button(substitute_btn_frame, text="AI分析実行", command=self.analyze_substitutes)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        assign_btn = ttk.Button(substitute_btn_frame, text="代替要員決定", command=self.assign_substitute)
        assign_btn.pack(side=tk.LEFT)
        
        # 初期データ読み込み
        self.load_staff_list()
        self.load_absence_records()
    
    def load_staff_list(self):
        """スタッフリストを読み込み"""
        # サンプルスタッフデータ
        staff_list = [
            "田中太郎", "佐藤花子", "鈴木次郎", "山田美咲", "高橋健太"
        ]
        self.staff_combo['values'] = staff_list
    
    def load_absence_records(self):
        """欠勤記録を読み込み"""
        # サンプル欠勤データ
        sample_absences = [
            ("2024-01-15", "田中太郎", "体調不良", "未対応"),
            ("2024-01-16", "佐藤花子", "家庭の事情", "代替済"),
            ("2024-01-18", "山田美咲", "急用", "未対応")
        ]
        
        for absence in sample_absences:
            self.absence_tree.insert('', tk.END, values=absence)
    
    def register_absence(self):
        """欠勤を登録"""
        staff = self.staff_combo.get()
        date = self.date_entry.get()
        reason = self.reason_entry.get()
        
        if not all([staff, date, reason]):
            messagebox.showwarning("入力エラー", "すべての項目を入力してください")
            return
        
        # 欠勤記録を追加
        self.absence_tree.insert('', tk.END, values=(date, staff, reason, "未対応"))
        
        # フォームをクリア
        self.staff_combo.set('')
        self.reason_entry.delete(0, tk.END)
        
        messagebox.showinfo("登録完了", f"{staff}さんの欠勤を登録しました")
    
    def on_absence_select(self, event):
        """欠勤選択時の処理"""
        selection = self.absence_tree.selection()
        if selection:
            item = self.absence_tree.item(selection[0])
            values = item['values']
            
            # 選択された欠勤に対してAI分析を実行
            self.analyze_substitutes_for_absence(values)
    
    def analyze_substitutes(self):
        """AI代替候補分析を実行"""
        selection = self.absence_tree.selection()
        if not selection:
            messagebox.showwarning("選択エラー", "欠勤記録を選択してください")
            return
        
        item = self.absence_tree.item(selection[0])
        values = item['values']
        self.analyze_substitutes_for_absence(values)
    
    def analyze_substitutes_for_absence(self, absence_data):
        """指定された欠勤に対する代替候補を分析"""
        date, absent_staff, reason, status = absence_data
        
        # 既存の候補をクリア
        for item in self.substitute_tree.get_children():
            self.substitute_tree.delete(item)
        
        # AI分析結果（サンプル）
        candidates = [
            ("鈴木次郎", "95%", "同部門・同スキルレベル・勤務可能"),
            ("高橋健太", "85%", "異部門だが経験あり・勤務可能"),
            ("山田美咲", "75%", "同部門・スキル不足だが対応可能"),
            ("佐藤花子", "60%", "リーダー経験あり・他業務との調整必要")
        ]
        
        for candidate in candidates:
            self.substitute_tree.insert('', tk.END, values=candidate)
        
        messagebox.showinfo("分析完了", f"{absent_staff}さんの代替候補を分析しました")
    
    def assign_substitute(self):
        """代替要員を決定"""
        absence_selection = self.absence_tree.selection()
        substitute_selection = self.substitute_tree.selection()
        
        if not absence_selection or not substitute_selection:
            messagebox.showwarning("選択エラー", "欠勤記録と代替候補を選択してください")
            return
        
        # 欠勤記録の状態を更新
        absence_item = self.absence_tree.item(absence_selection[0])
        absence_values = list(absence_item['values'])
        absence_values[3] = "代替済"
        self.absence_tree.item(absence_selection[0], values=absence_values)
        
        # 代替要員情報を取得
        substitute_item = self.substitute_tree.item(substitute_selection[0])
        substitute_name = substitute_item['values'][0]
        
        messagebox.showinfo("決定完了", f"{substitute_name}さんを代替要員に決定しました")
    
    def get_absence_statistics(self) -> Dict:
        """欠勤統計を取得"""
        total_absences = len(self.absence_tree.get_children())
        resolved_count = 0
        
        for item in self.absence_tree.get_children():
            values = self.absence_tree.item(item)['values']
            if values[3] == "代替済":
                resolved_count += 1
        
        return {
            "total_absences": total_absences,
            "resolved_absences": resolved_count,
            "pending_absences": total_absences - resolved_count,
            "resolution_rate": (resolved_count / total_absences * 100) if total_absences > 0 else 0
        }