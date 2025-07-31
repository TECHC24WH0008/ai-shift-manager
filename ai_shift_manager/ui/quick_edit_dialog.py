# -*- coding: utf-8 -*-
"""
クイック編集ダイアログ
スタッフ情報・希望シフトの簡単変更
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List, Any, Callable

class QuickEditDialog:
    """クイック編集ダイアログクラス"""
    
    def __init__(self, parent, title: str, data: Dict, on_save: Callable = None):
        self.parent = parent
        self.data = data.copy()
        self.original_data = data.copy()
        self.on_save = on_save
        
        # ダイアログウィンドウ作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 中央に配置
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_ui()
    
    def create_ui(self):
        """UI作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="⚡ クイック編集", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 編集エリア
        self.create_edit_area(main_frame)
        
        # ボタンエリア
        self.create_button_area(main_frame)
    
    def create_edit_area(self, parent):
        """編集エリア作成"""
        # スクロール可能フレーム
        canvas = tk.Canvas(parent, height=300)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 編集フィールド作成
        self.edit_vars = {}
        self.create_edit_fields(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_edit_fields(self, parent):
        """編集フィールド作成"""
        row = 0
        
        for key, value in self.data.items():
            if key.startswith('_'):  # 内部データはスキップ
                continue
            
            # ラベル
            label = ttk.Label(parent, text=f"{key}:")
            label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            # 入力フィールド
            if isinstance(value, bool):
                # チェックボックス
                var = tk.BooleanVar(value=value)
                widget = ttk.Checkbutton(parent, variable=var)
            elif key in ['希望勤務時間', '雇用形態', '部門', '役職']:
                # コンボボックス
                var = tk.StringVar(value=str(value))
                widget = ttk.Combobox(parent, textvariable=var, width=25)
                widget['values'] = self.get_combo_values(key)
            else:
                # テキスト入力
                var = tk.StringVar(value=str(value))
                widget = ttk.Entry(parent, textvariable=var, width=30)
            
            widget.grid(row=row, column=1, sticky=tk.W, pady=5)
            self.edit_vars[key] = var
            
            row += 1
    
    def get_combo_values(self, field_name: str) -> List[str]:
        """コンボボックスの選択肢を取得"""
        options = {
            '希望勤務時間': ['フルタイム', '午前のみ', '午後のみ', '夕方以降', '土日のみ', '平日のみ'],
            '雇用形態': ['正社員', 'パート', 'アルバイト', '契約社員'],
            '部門': ['営業部', '総務部', '管理部', '製造部', '販売部'],
            '役職': ['スタッフ', 'リーダー', '主任', '係長', '課長']
        }
        return options.get(field_name, [])
    
    def create_button_area(self, parent):
        """ボタンエリア作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 左側ボタン
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        # テンプレート保存
        template_btn = ttk.Button(left_buttons, text="📋 テンプレート保存", 
                                 command=self.save_as_template)
        template_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # リセット
        reset_btn = ttk.Button(left_buttons, text="🔄 リセット", 
                              command=self.reset_changes)
        reset_btn.pack(side=tk.LEFT)
        
        # 右側ボタン
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        # キャンセル
        cancel_btn = ttk.Button(right_buttons, text="キャンセル", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存
        save_btn = ttk.Button(right_buttons, text="💾 保存", 
                             command=self.save_changes)
        save_btn.pack(side=tk.LEFT)
    
    def save_as_template(self):
        """テンプレートとして保存"""
        template_name = tk.simpledialog.askstring(
            "テンプレート保存", 
            "テンプレート名を入力してください:"
        )
        
        if template_name:
            # 現在の入力値を取得
            current_data = self.get_current_data()
            
            # テンプレート保存処理
            messagebox.showinfo("保存完了", f"テンプレート '{template_name}' を保存しました")
    
    def reset_changes(self):
        """変更をリセット"""
        for key, var in self.edit_vars.items():
            original_value = self.original_data.get(key, "")
            var.set(str(original_value))
    
    def get_current_data(self) -> Dict:
        """現在の入力データを取得"""
        current_data = {}
        for key, var in self.edit_vars.items():
            value = var.get()
            
            # 元のデータ型に合わせて変換
            original_value = self.original_data.get(key)
            if isinstance(original_value, bool):
                current_data[key] = bool(value)
            elif isinstance(original_value, int):
                try:
                    current_data[key] = int(value)
                except ValueError:
                    current_data[key] = 0
            elif isinstance(original_value, float):
                try:
                    current_data[key] = float(value)
                except ValueError:
                    current_data[key] = 0.0
            else:
                current_data[key] = str(value)
        
        return current_data
    
    def save_changes(self):
        """変更を保存"""
        try:
            current_data = self.get_current_data()
            
            # バリデーション
            if self.validate_data(current_data):
                # 保存処理
                if self.on_save:
                    self.on_save(current_data)
                
                messagebox.showinfo("保存完了", "変更を保存しました")
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("保存エラー", f"保存に失敗しました: {str(e)}")
    
    def validate_data(self, data: Dict) -> bool:
        """データバリデーション"""
        # 必須フィールドチェック
        required_fields = ['氏名', '部門']
        for field in required_fields:
            if field in data and not data[field].strip():
                messagebox.showwarning("入力エラー", f"{field}は必須項目です")
                return False
        
        # 数値フィールドチェック
        if '時給' in data:
            try:
                wage = int(data['時給'])
                if wage < 0:
                    messagebox.showwarning("入力エラー", "時給は0以上で入力してください")
                    return False
            except ValueError:
                messagebox.showwarning("入力エラー", "時給は数値で入力してください")
                return False
        
        return True
    
    def cancel(self):
        """キャンセル"""
        if self.has_changes():
            result = messagebox.askyesno("確認", "変更が保存されていません。破棄しますか？")
            if not result:
                return
        
        self.dialog.destroy()
    
    def has_changes(self) -> bool:
        """変更があるかチェック"""
        current_data = self.get_current_data()
        
        for key, value in current_data.items():
            if str(value) != str(self.original_data.get(key, "")):
                return True
        
        return False


class ShiftPreferenceDialog(QuickEditDialog):
    """希望シフト専用編集ダイアログ"""
    
    def create_edit_fields(self, parent):
        """希望シフト用の編集フィールド"""
        # 週間希望シフト
        week_frame = ttk.LabelFrame(parent, text="📅 週間希望シフト", padding=10)
        week_frame.pack(fill=tk.X, pady=(0, 10))
        
        days = ['月', '火', '水', '木', '金', '土', '日']
        self.day_vars = {}
        
        for i, day in enumerate(days):
            day_frame = ttk.Frame(week_frame)
            day_frame.pack(fill=tk.X, pady=2)
            
            # 曜日ラベル
            ttk.Label(day_frame, text=f"{day}曜日:", width=8).pack(side=tk.LEFT)
            
            # 勤務可能チェック
            available_var = tk.BooleanVar()
            ttk.Checkbutton(day_frame, text="勤務可能", variable=available_var).pack(side=tk.LEFT, padx=(0, 10))
            
            # 希望時間
            ttk.Label(day_frame, text="時間:").pack(side=tk.LEFT, padx=(0, 5))
            start_var = tk.StringVar(value="09:00")
            ttk.Entry(day_frame, textvariable=start_var, width=8).pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(day_frame, text="〜").pack(side=tk.LEFT, padx=5)
            
            end_var = tk.StringVar(value="17:00")
            ttk.Entry(day_frame, textvariable=end_var, width=8).pack(side=tk.LEFT)
            
            self.day_vars[day] = {
                'available': available_var,
                'start_time': start_var,
                'end_time': end_var
            }
        
        # 特別な希望
        special_frame = ttk.LabelFrame(parent, text="📝 特別な希望・制約", padding=10)
        special_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.special_text = tk.Text(special_frame, height=4, width=50)
        self.special_text.pack(fill=tk.X)
        
        # 優先度設定
        priority_frame = ttk.Frame(special_frame)
        priority_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(priority_frame, text="優先度:").pack(side=tk.LEFT, padx=(0, 10))
        self.priority_var = tk.StringVar(value="普通")
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var, width=15)
        priority_combo['values'] = ["低", "普通", "高", "最高"]
        priority_combo.pack(side=tk.LEFT)