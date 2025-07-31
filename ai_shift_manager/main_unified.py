# -*- coding: utf-8 -*-
"""
AI Shift Manager - 統一UI版
完全オフライン対応のシフト管理システム
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import warnings

# 警告を抑制
warnings.filterwarnings('ignore', category=UserWarning)

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# フォント設定を最初に実行
try:
    from utils.font_manager import font_manager
    font_manager.setup_fonts()
except ImportError:
    print("フォントマネージャーが利用できません")

from ui.unified_components import UnifiedTheme, UnifiedFrame, UnifiedLabel
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.shift_creation_tab import ShiftCreationTab
from ui.tabs.calendar_tab import CalendarTab
from ui.tabs.data_management_tab import DataManagementTab
from ui.tabs.analytics_tab import AnalyticsTab
from ui.tabs.settings_tab import SettingsTab

class AIShiftManagerUnified:
    """AI Shift Manager 統一UI版メインクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_ui()
        
    def setup_main_window(self):
        """メインウィンドウを設定"""
        self.root.title("AI Shift Manager - 統一UI版")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # アイコン設定（オプション）
        try:
            # self.root.iconbitmap("assets/icon.ico")
            pass
        except:
            pass
        
        # ウィンドウを中央に配置
        self.center_window()
        
        # 背景色設定
        self.root.configure(bg=UnifiedTheme.COLORS['light'])
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_ui(self):
        """UIを作成"""
        # メインコンテナ
        main_container = UnifiedFrame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # ヘッダー
        self.create_header(main_container)
        
        # タブシステム
        self.create_tab_system(main_container)
        
        # ステータスバー
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """ヘッダーを作成"""
        header_frame = UnifiedFrame(parent, style="sidebar")
        header_frame.pack(fill="x")
        
        # タイトル
        title_label = UnifiedLabel(
            header_frame, 
            text="🤖 AI Shift Manager", 
            style="heading"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # バージョン情報
        version_label = UnifiedLabel(
            header_frame, 
            text="v2.0 - 統一UI版", 
            style="small"
        )
        version_label.pack(side="left", padx=(0, 20), pady=15)
        
        # 右側情報
        info_frame = UnifiedFrame(header_frame, style="sidebar")
        info_frame.pack(side="right", padx=20, pady=15)
        
        status_label = UnifiedLabel(
            info_frame, 
            text="🟢 オフライン", 
            style="success"
        )
        status_label.pack(side="right")
    
    def create_tab_system(self, parent):
        """タブシステムを作成"""
        # タブコンテナ
        tab_container = UnifiedFrame(parent)
        tab_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Notebookウィジェット
        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill="both", expand=True)
        
        # タブを作成
        self.create_tabs()
    
    def create_tabs(self):
        """各タブを作成"""
        # ダッシュボードタブ
        dashboard_frame = UnifiedFrame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 ダッシュボード")
        self.dashboard_tab = DashboardTab(dashboard_frame)
        
        # シフト作成タブ
        shift_frame = UnifiedFrame(self.notebook)
        self.notebook.add(shift_frame, text="📅 シフト作成")
        self.shift_tab = ShiftCreationTab(shift_frame)
        
        # カレンダータブ
        calendar_frame = UnifiedFrame(self.notebook)
        self.notebook.add(calendar_frame, text="�管 カレンダー")
        self.calendar_tab = CalendarTab(calendar_frame)
        
        # データ管理タブ
        data_frame = UnifiedFrame(self.notebook)
        self.notebook.add(data_frame, text="📊 データ管理")
        self.data_tab = DataManagementTab(data_frame)
        
        # 分析タブ
        analytics_frame = UnifiedFrame(self.notebook)
        self.notebook.add(analytics_frame, text="📈 分析")
        self.analytics_tab = AnalyticsTab(analytics_frame)
        
        # 設定タブ
        settings_frame = UnifiedFrame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ 設定")
        self.settings_tab = SettingsTab(settings_frame)
    
    def create_placeholder_tab(self, parent, title, description):
        """プレースホルダータブを作成"""
        container = UnifiedFrame(parent)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = UnifiedLabel(container, text=f"🚧 {title}", style="heading")
        title_label.pack(pady=(50, 20))
        
        # 説明
        desc_label = UnifiedLabel(container, text=description, style="default")
        desc_label.pack(pady=10)
        
        # 実装予定メッセージ
        status_label = UnifiedLabel(
            container, 
            text="この機能は統一UI移行後に実装予定です", 
            style="small"
        )
        status_label.pack(pady=20)
    
    def create_status_bar(self, parent):
        """ステータスバーを作成"""
        status_frame = UnifiedFrame(parent, style="sidebar")
        status_frame.pack(fill="x", side="bottom")
        
        # 左側ステータス
        left_status = UnifiedLabel(
            status_frame, 
            text="準備完了", 
            style="small"
        )
        left_status.pack(side="left", padx=10, pady=5)
        
        # 右側情報
        right_info = UnifiedLabel(
            status_frame, 
            text="統一UI版 | 完全オフライン対応", 
            style="small"
        )
        right_info.pack(side="right", padx=10, pady=5)
    
    def run(self):
        """アプリケーションを実行"""
        print("🚀 AI Shift Manager 統一UI版を起動中...")
        print("=" * 50)
        print("✅ フォント設定完了")
        print("✅ 統一UIコンポーネント読み込み完了")
        print("✅ タブシステム初期化完了")
        print("🎉 アプリケーション起動完了！")
        print("=" * 50)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 アプリケーションを終了します")
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
        finally:
            print("🔚 AI Shift Manager を終了しました")

def main():
    """メイン関数"""
    try:
        app = AIShiftManagerUnified()
        app.run()
    except Exception as e:
        print(f"❌ アプリケーション起動エラー: {e}")
        input("Enterキーを押して終了...")

if __name__ == "__main__":
    main()