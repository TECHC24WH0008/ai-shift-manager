# -*- coding: utf-8 -*-
"""
欠勤対応タブ
欠勤管理とAI代替要員機能のUI
"""

import tkinter as tk
from tkinter import ttk
from features.absence_manager import AbsenceManager

class AbsenceManagementTab:
    """欠勤対応タブクラス"""
    
    def __init__(self, parent_frame, data_manager=None):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        # 欠勤マネージャーを初期化
        self.absence_manager = AbsenceManager(parent_frame, data_manager)
    
    def get_absence_statistics(self):
        """欠勤統計を取得"""
        return self.absence_manager.get_absence_statistics()
    
    def refresh_absence_data(self):
        """欠勤データを更新"""
        self.absence_manager.load_absence_records()