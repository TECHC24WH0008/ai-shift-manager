# -*- coding: utf-8 -*-
"""
AI Shift Manager - メインアプリケーション（リファクタリング版）
中小企業向け完全オフライン AI シフト管理システム

使用方法:
python main_refactored.py

作者: TECHC24WH0008
ライセンス: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Any

# 必要なモジュールをインポート
try:
    from core.config import app_config
    from core.templates import ShiftTemplates
    from ui.components import *
    from ai.nlg_engine import NaturalLanguageGenerator
    from data.data_manager import DataManager
    from ui.tabs.dashboard_tab import DashboardTab
    from ui.tabs.calendar_tab import CalendarTab
    from ui.tabs.absence_management_tab import AbsenceManagementTab
    from ui.tabs.data_management_tab import DataManagementTab
    from ui.tabs.shift_creation_tab import ShiftCreationTab
    from ui.tabs.analytics_tab import AnalyticsTab
    from ui.tabs.settings_tab import SettingsTab
except ImportError as e:
    print(f"モジュールのインポートエラー: {e}")
    print("必要なファイルが不足している可能性があります。")
    print("フォルダ構成を確認してください。")
    sys.exit(1)

class AIShiftManagerApp:
    """AI Shift Manager メインアプリケーション（リファクタリング版）"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # コンポーネント初期化
        self.nlg = NaturalLanguageGenerator()
        self.data_manager = DataManager()
        
        # アプリケーション状態
        self.current_template = None
        self.shift_config = {}
        self.schedule_data = {}
        
        # UI コンポーネント
        self.status_indicator = None
        self.dashboard_tab = None
        
        # 初期化
        self.load_app_config()
        self.setup_theme()
        
        # 初回起動時はテンプレート選択画面
        if not self.current_template:
            self.show_template_selection()
        else:
            self.create_main_interface()
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title(app_config.get("app.name", "AI Shift Manager"))
        self.root.geometry(app_config.get("app.window_size", "900x700"))
        self.root.resizable(True, True)
    
    def setup_theme(self):
        """テーマとスタイルを設定"""
        style = ttk.Style()
        colors = app_config.get_colors()
        
        # 背景色設定
        self.root.configure(bg=colors.get("light", "#F8FAFC"))
        
        # カスタムスタイル定義
        style.configure('Title.TLabel', 
                       font=app_config.get_fonts().get("title", ("Segoe UI", 20, "bold")),
                       foreground=colors.get("primary", "#2563EB"),
                       background=colors.get("light", "#F8FAFC"))
        
        style.configure('Heading.TLabel', 
                       font=app_config.get_fonts().get("heading", ("Segoe UI", 14, "bold")),
                       foreground=colors.get("dark", "#1E293B"),
                       background=colors.get("light", "#F8FAFC"))
    
    def load_app_config(self):
        """アプリケーション設定を読み込み"""
        try:
            if os.path.exists("last_template.json"):
                import json
                with open("last_template.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.current_template = config.get("template_id")
                    self.shift_config = config.get("shift_config", {})
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
    
    def save_app_config(self):
        """アプリケーション設定を保存"""
        try:
            import json
            config = {
                "template_id": self.current_template,
                "shift_config": self.shift_config,
                "last_updated": datetime.now().isoformat()
            }
            with open("last_template.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定保存エラー: {e}")
    
    def show_template_selection(self):
        """テンプレート選択画面を表示"""
        # メインフレームをクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ヘッダー部分
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # タイトル
        title_label = ttk.Label(header_frame, text="🏢 業界テンプレートを選択", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="あなたの業界に最適化されたシフト管理テンプレートを選択してください",
                                  style='Heading.TLabel')
        subtitle_label.pack(pady=(10, 0))
        
        # テンプレート選択エリア
        selection_card = Card(main_container, title="📋 利用可能なテンプレート")
        selection_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # テンプレート一覧
        templates = ShiftTemplates.get_all_templates()
        self.selected_template = tk.StringVar()
        
        # シンプルなリスト表示
        template_frame = ttk.Frame(selection_card)
        template_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for template_id, template_info in templates.items():
            # テンプレートボタン
            template_btn = ttk.Radiobutton(
                template_frame,
                text=f"{template_info['name']} - {template_info['description']}",
                variable=self.selected_template,
                value=template_id,
                command=lambda: self.on_template_selected()
            )
            template_btn.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # ヘルプボタン
        help_btn = ModernButton(
            button_frame,
            text="ヘルプ",
            icon="❓",
            command=self.show_template_help,
            style="secondary"
        )
        help_btn.pack(side=tk.LEFT)
        
        # 右側ボタン
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side=tk.RIGHT)
        
        # キャンセルボタン
        cancel_btn = ModernButton(
            action_frame,
            text="キャンセル",
            command=self.root.quit,
            style="secondary"
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 決定ボタン
        confirm_btn = ModernButton(
            action_frame,
            text="決定して開始",
            icon="🚀",
            command=self.confirm_template_selection,
            style="primary"
        )
        confirm_btn.pack(side=tk.LEFT)
    
    def on_template_selected(self):
        """テンプレート選択時の処理"""
        pass
    
    def show_template_help(self):
        """テンプレートヘルプを表示"""
        help_text = """🏢 業界テンプレートについて

各テンプレートは業界の特性に合わせて最適化されています：

🍽️ 飲食店
• ピーク時間帯（ランチ・ディナー）に対応
• 深夜営業や酒類販売の法的要件を考慮

🛍️ 小売店  
• 開店準備・棚卸し業務に対応
• セール時の増員体制

🏢 事務所
• 定時勤務中心の安定したシフト
• 電話・来客対応の継続性

🏥 医療・介護
• 24時間体制の安全な人員配置
• 有資格者の必須配置

🎓 教育機関
• 授業時間に合わせた配置
• 安全管理体制の確保

⚙️ カスタム設定
• 独自の業界要件に対応
• 柔軟な時間帯・役職設定"""
        
        messagebox.showinfo("テンプレートヘルプ", help_text)
    
    def confirm_template_selection(self):
        """テンプレート選択確定"""
        if not self.selected_template.get():
            messagebox.showwarning("選択エラー", "テンプレートを選択してください。")
            return
        
        self.current_template = self.selected_template.get()
        self.save_app_config()
        self.create_main_interface()
    
    def create_main_interface(self):
        """メインインターフェースを作成"""
        # メインフレームをクリア
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ヘッダー部分
        self.create_header(main_container)
        
        # タブコンテナ作成
        self.notebook = TabContainer(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 各タブを作成（リファクタリング版）
        self.create_tabs()
    
    def create_header(self, parent):
        """ヘッダー部分を作成"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # タイトルとステータス
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)
        
        # アプリタイトル
        title_label = ttk.Label(title_frame, text="🤖 AI Shift Manager", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # ステータス表示
        self.status_indicator = StatusIndicator(title_frame)
        self.status_indicator.pack(side=tk.RIGHT)
        self.status_indicator.set_status("success", "準備完了")
        
        # 現在のテンプレート表示
        if self.current_template:
            templates = ShiftTemplates.get_all_templates()
            template_info = templates.get(self.current_template, {})
            template_frame = ttk.Frame(header_frame)
            template_frame.pack(fill=tk.X, pady=(10, 0))
            
            template_label = ttk.Label(
                template_frame, 
                text=f"📋 現在のテンプレート: {template_info.get('name', '不明')}",
                style='Heading.TLabel'
            )
            template_label.pack(side=tk.LEFT)
            
            # テンプレート変更ボタン
            change_btn = ModernButton(
                template_frame, 
                text="変更", 
                command=self.show_template_selection,
                style="primary"
            )
            change_btn.pack(side=tk.RIGHT)
    
    def create_tabs(self):
        """各タブを作成（リファクタリング版）"""
        # 実際のタブクラスを使用
        self.create_dashboard_tab()
        self.create_calendar_tab()
        self.create_absence_management_tab()
        self.create_data_management_tab()
        self.create_shift_creation_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """ダッシュボードタブを作成"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(dashboard_frame, "ダッシュボード", "📊")
        
        # DashboardTabクラスを使用
        self.dashboard_tab = DashboardTab(dashboard_frame, self.data_manager)
    
    def create_calendar_tab(self):
        """カレンダータブを作成"""
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(calendar_frame, "カレンダー", "📅")
        
        # CalendarTabクラスを使用
        self.calendar_tab = CalendarTab(calendar_frame, self.data_manager)
    
    def create_absence_management_tab(self):
        """欠勤対応タブを作成"""
        absence_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(absence_frame, "欠勤対応", "⚠️")
        
        # AbsenceManagementTabクラスを使用
        self.absence_tab = AbsenceManagementTab(absence_frame, self.data_manager)
    
    def create_data_management_tab(self):
        """データ管理タブを作成"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(data_frame, "データ管理", "📁")
        
        # DataManagementTabクラスを使用（既存）
        self.data_tab = DataManagementTab(data_frame, self.data_manager)
    
    def create_shift_creation_tab(self):
        """シフト作成タブを作成"""
        shift_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(shift_frame, "シフト作成", "🎯")
        
        # ShiftCreationTabクラスを使用
        self.shift_tab = ShiftCreationTab(shift_frame, self.data_manager)
    
    def create_analytics_tab(self):
        """分析タブを作成"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(analytics_frame, "分析", "📈")
        
        # AnalyticsTabクラスを使用
        self.analytics_tab = AnalyticsTab(analytics_frame, self.data_manager)
    
    def create_settings_tab(self):
        """設定タブを作成"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add_tab(settings_frame, "設定", "⚙️")
        
        # SettingsTabクラスを使用
        self.settings_tab = SettingsTab(settings_frame, self.data_manager)
    
    def add_activity(self, message: str):
        """アクティビティを追加"""
        # ダッシュボードタブにアクティビティを追加
        if hasattr(self, 'dashboard_tab') and self.dashboard_tab:
            self.dashboard_tab.add_activity(message)

def create_sample_data():
    """サンプルデータファイルを作成"""
    staff_data = """従業員ID,氏名,部門,役職,時給,雇用形態,入社日,スキルレベル,希望勤務時間,連絡先,備考
EMP001,田中太郎,営業部,スタッフ,1200,正社員,2023-04-01,3,フルタイム,090-1234-5678,リーダー候補
EMP002,佐藤花子,営業部,リーダー,1500,正社員,2022-01-15,5,フルタイム,090-2345-6789,研修担当可
EMP003,鈴木次郎,総務部,スタッフ,1000,パート,2023-06-01,2,午前のみ,090-3456-7890,学生
EMP004,山田美咲,営業部,スタッフ,1100,パート,2023-03-01,4,夕方以降,090-4567-8901,主婦
EMP005,高橋健太,営業部,スタッフ,1050,アルバイト,2023-07-01,1,土日のみ,090-5678-9012,新人研修中"""
    
    timecard_data = """日付,従業員ID,氏名,出勤時間,退勤時間,休憩時間,実働時間,部門,業務内容,評価
2024-01-01,EMP001,田中太郎,09:00,17:00,60,480,営業部,接客・レジ,4.5
2024-01-01,EMP002,佐藤花子,10:00,18:00,60,420,営業部,接客・指導,5.0
2024-01-01,EMP003,鈴木次郎,09:00,13:00,0,240,総務部,事務作業,4.0
2024-01-02,EMP001,田中太郎,09:00,17:00,60,480,営業部,接客・レジ,4.8
2024-01-02,EMP004,山田美咲,17:00,21:00,0,240,営業部,接客・清掃,4.2"""
    
    with open("sample_staff_info.csv", "w", encoding="utf-8") as f:
        f.write(staff_data)
    
    with open("sample_timecard.csv", "w", encoding="utf-8") as f:
        f.write(timecard_data)

def main():
    """メイン関数"""
    print("🚀 AI Shift Manager (リファクタリング版) を起動中...")
    print("="*50)
    
    if not os.path.exists("sample_staff_info.csv"):
        print("📊 サンプルデータファイルを作成中...")
        create_sample_data()
        print("✅ サンプルデータファイルを作成しました")
    
    try:
        import pandas
        import numpy
        print("✅ 必要なライブラリが確認されました")
    except ImportError as e:
        print(f"❌ 必要なライブラリが不足しています: {e}")
        print("以下のコマンドでインストールしてください:")
        print("pip install pandas numpy openpyxl")
        return
    
    try:
        root = tk.Tk()
        app = AIShiftManagerApp(root)
        
        print("✅ AI Shift Manager が正常に起動しました！")
        print("\n📖 リファクタリング版の特徴:")
        print("  • モジュール分割による保守性向上")
        print("  • 各機能の独立性確保")
        print("  • コードの再利用性向上")
        print("  • テストしやすい構造")
        print("\n🎯 楽しいシフト管理をお楽しみください！")
        print("="*50)
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {e}")
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{str(e)}")

if __name__ == "__main__":
    main()