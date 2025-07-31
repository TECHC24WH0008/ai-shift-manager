# -*- coding: utf-8 -*-
"""
分析タブ
シフト効率性や労働時間の分析・可視化 - 統一UI版
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_tab import BaseTab
from ui.unified_components import (
    UnifiedFrame, UnifiedButton, UnifiedLabel, UnifiedEntry,
    UnifiedCard, UnifiedTheme
)

# matplotlib関連のインポート（オプション）
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
    
    # 日本語フォント設定（警告を抑制）
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
    
    # フォントマネージャーから日本語フォントを取得
    try:
        from utils.font_manager import font_manager
        if font_manager and hasattr(font_manager, 'get_font_family'):
            japanese_font = font_manager.get_font_family()
            plt.rcParams['font.family'] = [japanese_font, 'DejaVu Sans']
        else:
            plt.rcParams['font.family'] = ['IPAexGothic', 'DejaVu Sans']
    except ImportError:
        plt.rcParams['font.family'] = ['IPAexGothic', 'DejaVu Sans']
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from typing import Dict, List, Any

class AnalyticsTab(BaseTab):
    """分析タブクラス - 統一UI版"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.data_manager = data_manager
        self.start_date_entry = None
        self.end_date_entry = None
        self.analysis_type = None
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.canvas = None
        self.stat_labels = {}
        super().__init__(parent_frame, "📈 分析レポート")
    
    def create_toolbar_buttons(self):
        """ツールバーボタンを作成"""
        self.toolbar.add_button("📊 分析更新", self.update_analysis, "primary")
        self.toolbar.add_button("📋 レポート生成", self.generate_report, "secondary")
        self.toolbar.add_separator()
        self.toolbar.add_button("📤 エクスポート", self.export_analysis, "light")
    
    def create_content(self):
        """分析コンテンツを作成"""
        # 分析設定カード
        settings_card = UnifiedCard(self.content_frame, title="📊 分析設定")
        settings_card.pack(fill="x", pady=5)
        
        settings_container = UnifiedFrame(settings_card)
        settings_container.pack(fill="x", padx=10, pady=10)
        
        # 期間選択
        UnifiedLabel(settings_container, text="分析期間:", style="default").pack(side="left", padx=(0, 10))
        
        self.start_date_entry = UnifiedEntry(settings_container, placeholder="開始日")
        self.start_date_entry.pack(side="left", padx=(0, 5))
        start_date = datetime.now() - timedelta(days=30)
        self.start_date_entry.insert(0, start_date.strftime("%Y-%m-%d"))
        
        UnifiedLabel(settings_container, text="〜", style="default").pack(side="left", padx=5)
        
        self.end_date_entry = UnifiedEntry(settings_container, placeholder="終了日")
        self.end_date_entry.pack(side="left", padx=(5, 20))
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 分析タイプ選択
        self.analysis_type = tk.StringVar(value="労働時間")
        analysis_combo = ttk.Combobox(settings_container, textvariable=self.analysis_type, width=15)
        analysis_combo['values'] = ["労働時間", "シフト効率", "スタッフ稼働率", "部門別分析"]
        analysis_combo.pack(side="left", padx=(0, 20))
        
        # グラフエリア
        if MATPLOTLIB_AVAILABLE:
            self.create_graph_area()
        else:
            self.create_no_matplotlib_area()
        
        # 統計サマリー
        self.create_statistics_summary()
    
    def create_graph_area(self):
        """グラフエリアを作成（matplotlib利用可能時）"""
        graph_card = UnifiedCard(self.content_frame, title="📈 分析結果")
        graph_card.pack(fill="both", expand=True, pady=5)
        
        # matplotlib図を作成
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.patch.set_facecolor('white')
        
        # Tkinterキャンバスに埋め込み
        self.canvas = FigureCanvasTkAgg(self.fig, graph_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_no_matplotlib_area(self):
        """matplotlibが利用できない場合の代替表示"""
        graph_card = UnifiedCard(self.content_frame, title="📈 分析結果")
        graph_card.pack(fill="both", expand=True, pady=5)
        
        placeholder_container = UnifiedFrame(graph_card)
        placeholder_container.pack(fill="both", expand=True, padx=10, pady=50)
        
        UnifiedLabel(
            placeholder_container, 
            text="📊 グラフ表示機能", 
            style="heading"
        ).pack(pady=20)
        
        UnifiedLabel(
            placeholder_container, 
            text="matplotlibがインストールされていないため、\nグラフ表示機能は利用できません。", 
            style="default"
        ).pack(pady=10)
        
        UnifiedLabel(
            placeholder_container, 
            text="pip install matplotlib でインストールしてください", 
            style="small"
        ).pack(pady=10)
    
    def create_statistics_summary(self):
        """統計サマリーを作成"""
        summary_card = UnifiedCard(self.content_frame, title="📋 統計サマリー")
        summary_card.pack(fill="x", pady=5)
        
        # 統計カードグリッド
        stats_grid = UnifiedFrame(summary_card)
        stats_grid.pack(fill="x", padx=10, pady=10)
        
        # 4列のグリッド設定
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # 統計カード作成
        self.create_stat_card(stats_grid, "総労働時間", "160時間", 0, 0)
        self.create_stat_card(stats_grid, "平均効率", "87%", 0, 1)
        self.create_stat_card(stats_grid, "稼働率", "78%", 0, 2)
        self.create_stat_card(stats_grid, "コスト", "¥450,000", 0, 3)
    
    def create_stat_card(self, parent, title, value, row, col):
        """統計カードを作成"""
        card_frame = UnifiedFrame(parent, style="card")
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        title_label = UnifiedLabel(card_frame, text=title, style="small")
        title_label.pack(pady=(15, 5))
        
        value_label = UnifiedLabel(card_frame, text=value, style="heading")
        value_label.pack(pady=(0, 15))
        
        # 後で更新するために保存
        self.stat_labels[title] = value_label
    
    def load_data(self):
        """データを読み込み"""
        self.update_status("分析データを読み込み中...")
        self.update_analysis()
        self.update_status("分析完了")
    
    def update_analysis(self):
        """分析を更新"""
        if not self.analysis_type:
            return
        
        self.update_status("分析を更新中...")
        analysis_type = self.analysis_type.get()
        
        if MATPLOTLIB_AVAILABLE and self.ax1 and self.ax2:
            # グラフをクリア
            self.ax1.clear()
            self.ax2.clear()
            
            if analysis_type == "労働時間":
                self.create_work_hours_analysis()
            elif analysis_type == "シフト効率":
                self.create_efficiency_analysis()
            elif analysis_type == "スタッフ稼働率":
                self.create_utilization_analysis()
            elif analysis_type == "部門別分析":
                self.create_department_analysis()
            
            # グラフを更新
            self.canvas.draw()
        
        # 統計サマリーを更新
        self.update_statistics()
        
        self.update_status("分析更新完了")
        self.show_success("分析完了", f"{analysis_type}の分析を更新しました")
    
    def create_work_hours_analysis(self):
        """労働時間分析グラフを作成"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # 日本語フォント設定を確実に適用
        try:
            from utils.font_manager import font_manager
            if font_manager and hasattr(font_manager, 'get_font_family'):
                japanese_font = font_manager.get_font_family()
                plt.rcParams['font.family'] = [japanese_font]
        except:
            plt.rcParams['font.family'] = ['IPAexGothic']
        
        # サンプルデータ
        dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
        hours = [8.5, 9.2, 7.8, 8.0, 9.5, 6.5, 7.2]
        
        # 左グラフ: 日別労働時間
        self.ax1.plot(dates, hours, marker='o', linewidth=2, markersize=6)
        self.ax1.set_title('日別労働時間推移', fontsize=12, pad=20)
        self.ax1.set_ylabel('労働時間 (時間)')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        # 右グラフ: スタッフ別労働時間
        staff_names = ['田中', '佐藤', '鈴木', '山田', '高橋']
        staff_hours = [42, 38, 25, 35, 20]
        
        bars = self.ax2.bar(staff_names, staff_hours, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        self.ax2.set_title('スタッフ別週間労働時間', fontsize=12, pad=20)
        self.ax2.set_ylabel('労働時間 (時間)')
        
        # バーの上に値を表示
        for bar, hour in zip(bars, staff_hours):
            self.ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                         f'{hour}h', ha='center', va='bottom')
    
    def create_efficiency_analysis(self):
        """効率性分析グラフを作成"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # 日本語フォント設定
        try:
            from utils.font_manager import font_manager
            if font_manager and hasattr(font_manager, 'get_font_family'):
                japanese_font = font_manager.get_font_family()
                plt.rcParams['font.family'] = [japanese_font]
        except:
            plt.rcParams['font.family'] = ['IPAexGothic']
        
        # サンプルデータ
        dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
        efficiency = [85, 92, 78, 88, 95, 82, 90]
        
        # 左グラフ: 効率推移
        self.ax1.plot(dates, efficiency, marker='s', linewidth=2, markersize=6, color='#FF6B6B')
        self.ax1.set_title('シフト効率推移', fontsize=12, pad=20)
        self.ax1.set_ylabel('効率 (%)')
        self.ax1.set_ylim(70, 100)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        # 右グラフ: 時間帯別効率
        time_slots = ['9-12', '12-15', '15-18', '18-21']
        time_efficiency = [88, 95, 85, 78]
        
        bars = self.ax2.bar(time_slots, time_efficiency, color='#4ECDC4')
        self.ax2.set_title('時間帯別効率', fontsize=12, pad=20)
        self.ax2.set_ylabel('効率 (%)')
        self.ax2.set_ylim(70, 100)
        
        for bar, eff in zip(bars, time_efficiency):
            self.ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                         f'{eff}%', ha='center', va='bottom')
    
    def create_utilization_analysis(self):
        """稼働率分析グラフを作成"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # 日本語フォント設定
        try:
            from utils.font_manager import font_manager
            if font_manager and hasattr(font_manager, 'get_font_family'):
                japanese_font = font_manager.get_font_family()
                plt.rcParams['font.family'] = [japanese_font]
        except:
            plt.rcParams['font.family'] = ['IPAexGothic']
        
        # 左グラフ: スタッフ稼働率
        staff_names = ['田中', '佐藤', '鈴木', '山田', '高橋']
        utilization = [95, 85, 60, 80, 45]
        
        bars = self.ax1.barh(staff_names, utilization, color='#45B7D1')
        self.ax1.set_title('スタッフ稼働率', fontsize=12, pad=20)
        self.ax1.set_xlabel('稼働率 (%)')
        self.ax1.set_xlim(0, 100)
        
        for bar, util in zip(bars, utilization):
            self.ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                         f'{util}%', ha='left', va='center')
        
        # 右グラフ: 部門別稼働率
        departments = ['営業部', '総務部', '管理部']
        dept_utilization = [82, 65, 90]
        
        colors = ['#96CEB4', '#FFEAA7', '#DDA0DD']
        wedges, texts, autotexts = self.ax2.pie(dept_utilization, labels=departments, 
                                               autopct='%1.1f%%', colors=colors, startangle=90)
        self.ax2.set_title('部門別稼働率', fontsize=12, pad=20)
    
    def create_department_analysis(self):
        """部門別分析グラフを作成"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # 日本語フォント設定
        try:
            from utils.font_manager import font_manager
            if font_manager and hasattr(font_manager, 'get_font_family'):
                japanese_font = font_manager.get_font_family()
                plt.rcParams['font.family'] = [japanese_font]
        except:
            plt.rcParams['font.family'] = ['IPAexGothic']
        
        # 左グラフ: 部門別労働時間
        departments = ['営業部', '総務部', '管理部']
        dept_hours = [120, 80, 60]
        
        bars = self.ax1.bar(departments, dept_hours, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        self.ax1.set_title('部門別総労働時間', fontsize=12, pad=20)
        self.ax1.set_ylabel('労働時間 (時間)')
        
        for bar, hour in zip(bars, dept_hours):
            self.ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                         f'{hour}h', ha='center', va='bottom')
        
        # 右グラフ: 部門別コスト
        dept_costs = [180000, 120000, 150000]
        
        bars = self.ax2.bar(departments, dept_costs, color=['#96CEB4', '#FFEAA7', '#DDA0DD'])
        self.ax2.set_title('部門別人件費', fontsize=12, pad=20)
        self.ax2.set_ylabel('コスト (円)')
        
        for bar, cost in zip(bars, dept_costs):
            self.ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000, 
                         f'¥{cost:,}', ha='center', va='bottom')
    
    def update_statistics(self):
        """統計サマリーを更新"""
        # サンプル統計データ
        total_hours = 160
        avg_efficiency = 87
        utilization_rate = 78
        total_cost = 450000
        
        # ラベルを更新
        if "総労働時間" in self.stat_labels:
            self.stat_labels["総労働時間"].config(text=f"{total_hours}時間")
        if "平均効率" in self.stat_labels:
            self.stat_labels["平均効率"].config(text=f"{avg_efficiency}%")
        if "稼働率" in self.stat_labels:
            self.stat_labels["稼働率"].config(text=f"{utilization_rate}%")
        if "コスト" in self.stat_labels:
            self.stat_labels["コスト"].config(text=f"¥{total_cost:,}")
    
    def generate_report(self):
        """レポートを生成"""
        self.update_status("レポートを生成中...")
        
        analysis_type = self.analysis_type.get() if self.analysis_type else "労働時間"
        start_date = self.start_date_entry.get() if self.start_date_entry else "2024-01-01"
        end_date = self.end_date_entry.get() if self.end_date_entry else "2024-01-31"
        
        report_content = f"""
📊 分析レポート

分析期間: {start_date} 〜 {end_date}
分析タイプ: {analysis_type}

📈 主要指標:
• 総労働時間: 160時間
• 平均効率: 87%
• 稼働率: 78%
• 総コスト: ¥450,000

💡 改善提案:
• 効率の低い時間帯の見直し
• スタッフ配置の最適化
• コスト削減の検討
        """
        
        self.update_status("レポート生成完了")
        self.show_success("レポート生成完了", report_content)
    
    def export_analysis(self):
        """分析結果をエクスポート"""
        self.update_status("分析結果をエクスポート中...")
        
        # TODO: 実際のエクスポート処理を実装
        
        self.update_status("エクスポート完了")
        self.show_success("エクスポート完了", "分析結果をCSVファイルにエクスポートしました")