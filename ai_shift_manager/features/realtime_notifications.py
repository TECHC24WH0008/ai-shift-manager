# -*- coding: utf-8 -*-
"""
リアルタイム通知システム
タイムカード、欠勤、代替要員の即座通知
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
import logging

class RealtimeNotificationSystem:
    """リアルタイム通知システム"""
    
    def __init__(self, parent_app=None):
        self.parent_app = parent_app
        self.notification_queue = []
        self.is_running = False
        self.notification_thread = None
        
        # 通知設定
        self.notification_settings = {
            "shift_start_reminder": True,      # シフト開始前通知
            "absence_alert": True,             # 欠勤アラート
            "substitute_suggestion": True,     # 代替要員提案
            "timecard_anomaly": True,         # タイムカード異常
            "reminder_minutes": 30            # 事前通知時間
        }
        
        # 通知履歴
        self.notification_history = []
    
    def start_monitoring(self):
        """監視開始"""
        if not self.is_running:
            self.is_running = True
            self.notification_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.notification_thread.start()
            logging.info("リアルタイム通知監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.is_running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=1)
        logging.info("リアルタイム通知監視を停止しました")
    
    def _monitoring_loop(self):
        """監視ループ"""
        while self.is_running:
            try:
                # 各種チェックを実行
                self._check_shift_reminders()
                self._check_absence_alerts()
                self._check_timecard_anomalies()
                self._process_notification_queue()
                
                # 1分間隔でチェック
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"通知監視エラー: {e}")
                time.sleep(60)
    
    def _check_shift_reminders(self):
        """シフト開始前通知チェック"""
        if not self.notification_settings["shift_start_reminder"]:
            return
        
        try:
            current_time = datetime.now()
            reminder_time = current_time + timedelta(minutes=self.notification_settings["reminder_minutes"])
            
            # 今後30分以内に開始するシフトをチェック
            upcoming_shifts = self._get_upcoming_shifts(reminder_time)
            
            for shift in upcoming_shifts:
                notification = {
                    "type": "shift_reminder",
                    "title": "🕐 シフト開始通知",
                    "message": f"{shift['staff_name']}さんのシフトが{shift['start_time']}に開始します",
                    "priority": "normal",
                    "timestamp": current_time,
                    "data": shift
                }
                self._add_notification(notification)
                
        except Exception as e:
            logging.error(f"シフト通知チェックエラー: {e}")
    
    def _check_absence_alerts(self):
        """欠勤アラートチェック"""
        if not self.notification_settings["absence_alert"]:
            return
        
        try:
            current_time = datetime.now()
            
            # 開始時刻を過ぎても出勤していないシフトをチェック
            overdue_shifts = self._get_overdue_shifts(current_time)
            
            for shift in overdue_shifts:
                # AI代替要員を即座に提案
                substitute_candidates = self._get_substitute_candidates(shift)
                
                notification = {
                    "type": "absence_alert",
                    "title": "⚠️ 欠勤アラート",
                    "message": f"{shift['staff_name']}さんが未出勤です。代替要員を提案しますか？",
                    "priority": "high",
                    "timestamp": current_time,
                    "data": {
                        "shift": shift,
                        "substitutes": substitute_candidates
                    },
                    "actions": ["代替要員表示", "欠勤登録", "後で確認"]
                }
                self._add_notification(notification)
                
        except Exception as e:
            logging.error(f"欠勤アラートチェックエラー: {e}")
    
    def _check_timecard_anomalies(self):
        """タイムカード異常チェック"""
        if not self.notification_settings["timecard_anomaly"]:
            return
        
        try:
            current_time = datetime.now()
            
            # 異常なタイムカードパターンを検出
            anomalies = self._detect_timecard_anomalies(current_time)
            
            for anomaly in anomalies:
                notification = {
                    "type": "timecard_anomaly",
                    "title": "📊 タイムカード異常",
                    "message": f"{anomaly['staff_name']}: {anomaly['issue']}",
                    "priority": "normal",
                    "timestamp": current_time,
                    "data": anomaly
                }
                self._add_notification(notification)
                
        except Exception as e:
            logging.error(f"タイムカード異常チェックエラー: {e}")
    
    def _add_notification(self, notification: Dict):
        """通知をキューに追加"""
        # 重複チェック
        if not self._is_duplicate_notification(notification):
            self.notification_queue.append(notification)
            self.notification_history.append(notification)
            
            # 履歴は最大100件まで
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-100:]
    
    def _is_duplicate_notification(self, new_notification: Dict) -> bool:
        """重複通知チェック"""
        current_time = datetime.now()
        
        # 過去5分以内の同じタイプの通知をチェック
        for notification in reversed(self.notification_history[-10:]):
            if (notification["type"] == new_notification["type"] and
                (current_time - notification["timestamp"]).total_seconds() < 300):
                return True
        return False
    
    def _process_notification_queue(self):
        """通知キューの処理"""
        while self.notification_queue:
            notification = self.notification_queue.pop(0)
            self._show_notification(notification)
    
    def _show_notification(self, notification: Dict):
        """通知表示"""
        try:
            if notification["priority"] == "high":
                # 高優先度通知：アクション付きダイアログ
                self._show_action_dialog(notification)
            else:
                # 通常通知：情報ダイアログ
                self._show_info_notification(notification)
                
        except Exception as e:
            logging.error(f"通知表示エラー: {e}")
    
    def _show_action_dialog(self, notification: Dict):
        """アクション付き通知ダイアログ"""
        if notification["type"] == "absence_alert":
            # 欠勤アラートの場合
            result = messagebox.askyesnocancel(
                notification["title"],
                notification["message"],
                icon="warning"
            )
            
            if result is True:  # Yes - 代替要員表示
                self._show_substitute_candidates(notification["data"])
            elif result is False:  # No - 欠勤登録
                self._register_absence(notification["data"]["shift"])
            # Cancel - 何もしない
    
    def _show_info_notification(self, notification: Dict):
        """情報通知"""
        messagebox.showinfo(
            notification["title"],
            notification["message"],
            icon="info"
        )
    
    def _show_substitute_candidates(self, data: Dict):
        """代替要員候補表示"""
        shift = data["shift"]
        substitutes = data["substitutes"]
        
        if not substitutes:
            messagebox.showinfo("代替要員", "適切な代替要員が見つかりませんでした")
            return
        
        # 代替要員選択ダイアログ
        substitute_window = tk.Toplevel()
        substitute_window.title("🤖 AI代替要員提案")
        substitute_window.geometry("500x400")
        
        # 候補リスト表示
        tk.Label(substitute_window, text=f"欠勤: {shift['staff_name']}さん", 
                font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        tk.Label(substitute_window, text="AI推薦代替要員:", 
                font=("Segoe UI", 10)).pack()
        
        for i, candidate in enumerate(substitutes[:3]):  # 上位3名
            candidate_frame = tk.Frame(substitute_window, relief=tk.RAISED, bd=1)
            candidate_frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(candidate_frame, 
                    text=f"#{i+1} {candidate['name']} (適合度: {candidate['score']:.0f}%)",
                    font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
            
            tk.Label(candidate_frame, 
                    text=f"理由: {candidate['reason']}",
                    font=("Segoe UI", 9)).pack(anchor=tk.W)
            
            tk.Button(candidate_frame, text="選択", 
                     command=lambda c=candidate: self._assign_substitute(shift, c)).pack(side=tk.RIGHT)
    
    def _assign_substitute(self, shift: Dict, substitute: Dict):
        """代替要員を決定"""
        messagebox.showinfo("決定", f"{substitute['name']}さんを代替要員に決定しました")
        # 実際の代替要員登録処理をここに実装
    
    def _register_absence(self, shift: Dict):
        """欠勤登録"""
        messagebox.showinfo("欠勤登録", f"{shift['staff_name']}さんの欠勤を登録しました")
        # 実際の欠勤登録処理をここに実装
    
    # データ取得メソッド（実際のデータソースに接続）
    def _get_upcoming_shifts(self, target_time: datetime) -> List[Dict]:
        """今後のシフト取得"""
        # サンプルデータ
        return [
            {
                "staff_name": "田中太郎",
                "start_time": "09:00",
                "shift_id": "S001"
            }
        ]
    
    def _get_overdue_shifts(self, current_time: datetime) -> List[Dict]:
        """遅刻シフト取得"""
        # サンプルデータ
        return [
            {
                "staff_name": "佐藤花子",
                "start_time": "09:00",
                "shift_id": "S002"
            }
        ]
    
    def _get_substitute_candidates(self, shift: Dict) -> List[Dict]:
        """代替要員候補取得"""
        # サンプルデータ
        return [
            {
                "name": "鈴木次郎",
                "score": 95,
                "reason": "同部門・同スキルレベル・勤務可能"
            },
            {
                "name": "山田美咲", 
                "score": 85,
                "reason": "異部門だが経験あり・勤務可能"
            }
        ]
    
    def _detect_timecard_anomalies(self, current_time: datetime) -> List[Dict]:
        """タイムカード異常検出"""
        # サンプルデータ
        return [
            {
                "staff_name": "高橋健太",
                "issue": "連続12時間勤務が検出されました"
            }
        ]