# -*- coding: utf-8 -*-
"""
データインポートウィザード
ユーザーが簡単にデータを準備できるツール
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import os

class DataImportWizard:
    """データインポートウィザード"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 AI Shift Manager - データインポートウィザード")
        self.root.geometry("800x600")
        
        self.current_step = 0
        self.steps = [
            "データ形式選択",
            "ファイル選択", 
            "データ確認",
            "インポート実行"
        ]
        
        self.user_data = {
            'import_type': None,
            'files': {},
            'preview_data': {},
            'validation_results': {}
        }
        
        self.create_ui()
    
    def create_ui(self):
        """UI作成"""
        # ヘッダー
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text="🚀 データインポートウィザード", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack()
        
        # プログレスバー
        self.progress_frame = ttk.Frame(header_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress_bar.pack()
        
        # ステップ表示
        self.step_label = ttk.Label(header_frame, text="", font=("Segoe UI", 10))
        self.step_label.pack(pady=(5, 0))
        
        # メインコンテンツエリア
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # ボタンエリア
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.back_btn = ttk.Button(button_frame, text="← 戻る", command=self.go_back)
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(button_frame, text="次へ →", command=self.go_next)
        self.next_btn.pack(side=tk.RIGHT)
        
        # 最初のステップを表示
        self.update_step()
    
    def update_step(self):
        """ステップ更新"""
        # プログレスバー更新
        progress = (self.current_step / (len(self.steps) - 1)) * 100
        self.progress_bar['value'] = progress
        
        # ステップラベル更新
        self.step_label.config(text=f"ステップ {self.current_step + 1}/{len(self.steps)}: {self.steps[self.current_step]}")
        
        # ボタン状態更新
        self.back_btn.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_btn.config(text="完了" if self.current_step == len(self.steps) - 1 else "次へ →")
        
        # コンテンツエリアクリア
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 各ステップのUI作成
        if self.current_step == 0:
            self.create_step1_ui()
        elif self.current_step == 1:
            self.create_step2_ui()
        elif self.current_step == 2:
            self.create_step3_ui()
        elif self.current_step == 3:
            self.create_step4_ui()
    
    def create_step1_ui(self):
        """ステップ1: データ形式選択"""
        ttk.Label(self.content_frame, text="データの準備方法を選択してください", 
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
        
        # 選択肢
        self.import_type_var = tk.StringVar()
        
        options = [
            ("sample", "🎬 サンプルデータを使用", "デモ・テスト用のリアルなサンプルデータを生成"),
            ("csv", "📊 既存CSVファイルを使用", "お手持ちのタイムカード・スタッフデータを読み込み"),
            ("excel", "📈 Excelファイルを使用", "Excel形式のデータファイルを読み込み"),
            ("manual", "✏️ 手動でデータ入力", "少数のスタッフ情報を手動で入力")
        ]
        
        for value, title, description in options:
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(frame, text=title, variable=self.import_type_var, value=value)
            radio.pack(anchor=tk.W)
            
            desc_label = ttk.Label(frame, text=f"  {description}", foreground="gray")
            desc_label.pack(anchor=tk.W, padx=(20, 0))
    
    def create_step2_ui(self):
        """ステップ2: ファイル選択"""
        import_type = self.import_type_var.get()
        
        if import_type == "sample":
            self.create_sample_selection_ui()
        elif import_type in ["csv", "excel"]:
            self.create_file_selection_ui()
        elif import_type == "manual":
            self.create_manual_input_ui()
    
    def create_sample_selection_ui(self):
        """サンプルデータ選択UI"""
        ttk.Label(self.content_frame, text="業界を選択してください", 
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
        
        self.industry_var = tk.StringVar(value="retail")
        
        industries = [
            ("retail", "🛍️ 小売店", "レジ・フロア・倉庫などの部門"),
            ("restaurant", "🍽️ 飲食店", "ホール・キッチン・レジなどの部門"),
            ("office", "🏢 事務所", "営業・総務・経理などの部門")
        ]
        
        for value, title, description in industries:
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(frame, text=title, variable=self.industry_var, value=value)
            radio.pack(anchor=tk.W)
            
            desc_label = ttk.Label(frame, text=f"  {description}", foreground="gray")
            desc_label.pack(anchor=tk.W, padx=(20, 0))
        
        # データ量設定
        ttk.Label(self.content_frame, text="データ量設定", 
                 font=("Segoe UI", 10, "bold")).pack(pady=(20, 10), anchor=tk.W)
        
        settings_frame = ttk.Frame(self.content_frame)
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="スタッフ数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.staff_count_var = tk.StringVar(value="12")
        ttk.Spinbox(settings_frame, from_=5, to=50, textvariable=self.staff_count_var, width=10).grid(row=0, column=1)
        
        ttk.Label(settings_frame, text="データ期間:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.days_var = tk.StringVar(value="30")
        ttk.Spinbox(settings_frame, from_=7, to=90, textvariable=self.days_var, width=10).grid(row=1, column=1, pady=(10, 0))
        ttk.Label(settings_frame, text="日").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(10, 0))
    
    def create_file_selection_ui(self):
        """ファイル選択UI"""
        ttk.Label(self.content_frame, text="データファイルを選択してください", 
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
        
        # タイムカードファイル
        timecard_frame = ttk.LabelFrame(self.content_frame, text="📊 タイムカードデータ（必須）", padding=10)
        timecard_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.timecard_file_var = tk.StringVar()
        ttk.Entry(timecard_frame, textvariable=self.timecard_file_var, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(timecard_frame, text="参照", 
                  command=lambda: self.select_file(self.timecard_file_var, "タイムカードファイル")).pack(side=tk.LEFT)
        
        # スタッフファイル
        staff_frame = ttk.LabelFrame(self.content_frame, text="👥 スタッフ情報（オプション）", padding=10)
        staff_frame.pack(fill=tk.X)
        
        self.staff_file_var = tk.StringVar()
        ttk.Entry(staff_frame, textvariable=self.staff_file_var, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(staff_frame, text="参照", 
                  command=lambda: self.select_file(self.staff_file_var, "スタッフファイル")).pack(side=tk.LEFT)
    
    def select_file(self, var, title):
        """ファイル選択ダイアログ"""
        filetypes = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(title=f"{title}を選択", filetypes=filetypes)
        if filename:
            var.set(filename)
    
    def go_back(self):
        """前のステップに戻る"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()
    
    def go_next(self):
        """次のステップに進む"""
        if self.current_step < len(self.steps) - 1:
            if self.validate_current_step():
                self.current_step += 1
                self.update_step()
        else:
            self.finish_import()
    
    def validate_current_step(self):
        """現在のステップの検証"""
        if self.current_step == 0:
            if not self.import_type_var.get():
                messagebox.showwarning("選択エラー", "データ形式を選択してください")
                return False
        elif self.current_step == 1:
            import_type = self.import_type_var.get()
            if import_type in ["csv", "excel"] and not self.timecard_file_var.get():
                messagebox.showwarning("ファイルエラー", "タイムカードファイルを選択してください")
                return False
        
        return True
    
    def finish_import(self):
        """インポート完了"""
        messagebox.showinfo("完了", "データインポートが完了しました！\n\nAI Shift Managerを開始できます。")
        self.root.quit()
    
    def run(self):
        """ウィザード実行"""
        self.root.mainloop()

if __name__ == "__main__":
    wizard = DataImportWizard()
    wizard.run()