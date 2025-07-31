# -*- coding: utf-8 -*-
"""
フォント管理モジュール
日本語フォントの設定と管理
"""

import os
import sys
import warnings
from typing import Dict, List, Optional
import logging

# 警告を抑制
warnings.filterwarnings('ignore', category=UserWarning, module='tkinter')
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')

try:
    import matplotlib
    import matplotlib.font_manager as fm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class FontManager:
    """フォント管理クラス"""
    
    def __init__(self):
        self.font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
        self.default_font = "Arial"  # フォールバック
        self.font_paths = {}
        self.available_fonts = []
    
    def setup_fonts(self):
        """フォント設定"""
        try:
            # フォントディレクトリが存在するか確認
            if not os.path.exists(self.font_dir):
                os.makedirs(self.font_dir, exist_ok=True)
            
            # 同梱フォントの確認
            self.scan_font_directory()
            
            # 日本語フォントが見つからない場合、システムフォントから検索
            if not self.available_fonts:
                self.find_system_japanese_fonts()
            
            # matplotlibのフォント設定
            if MATPLOTLIB_AVAILABLE:
                self.configure_matplotlib_fonts()
            
            return len(self.available_fonts) > 0
            
        except Exception as e:
            logging.error(f"フォント設定エラー: {e}")
            return False
    
    def scan_font_directory(self):
        """同梱フォントディレクトリをスキャン"""
        if not os.path.exists(self.font_dir):
            return
        
        try:
            for file in os.listdir(self.font_dir):
                if file.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(self.font_dir, file)
                    
                    if MATPLOTLIB_AVAILABLE:
                        try:
                            # フォント名を取得
                            font_prop = fm.FontProperties(fname=font_path)
                            font_name = font_prop.get_name()
                            
                            self.font_paths[font_name] = font_path
                            self.available_fonts.append(font_name)
                            
                            # 最初に見つかったフォントをデフォルトに
                            if self.default_font == "Arial":
                                self.default_font = font_name
                            
                            logging.info(f"フォント読み込み: {font_name} ({file})")
                            
                        except Exception as e:
                            logging.error(f"フォント読み込みエラー {file}: {e}")
                    else:
                        # matplotlibが利用できない場合はファイル名ベース
                        font_name = os.path.splitext(file)[0]
                        self.font_paths[font_name] = font_path
                        self.available_fonts.append(font_name)
                        
                        if self.default_font == "Arial":
                            self.default_font = font_name
                            
        except Exception as e:
            logging.error(f"フォントディレクトリスキャンエラー: {e}")
    
    def find_system_japanese_fonts(self):
        """システムから日本語フォントを検索"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        # 一般的な日本語フォント名
        japanese_font_names = [
            'IPAexGothic', 'IPAPGothic', 'IPAGothic', 'IPAexMincho', 'IPAPMincho',
            'MS Gothic', 'MS PGothic', 'MS Mincho', 'MS PMincho',
            'Meiryo', 'Meiryo UI', 'Yu Gothic', 'Yu Mincho',
            'Hiragino Sans', 'Hiragino Kaku Gothic Pro', 'Hiragino Maru Gothic Pro',
            'Noto Sans CJK JP', 'Noto Sans JP'
        ]
        
        try:
            # システムフォントをチェック
            font_list = fm.findSystemFonts()
            
            for font_path in font_list[:100]:  # 最初の100個のみチェック（パフォーマンス向上）
                try:
                    font_prop = fm.FontProperties(fname=font_path)
                    font_name = font_prop.get_name()
                    
                    # 日本語フォントかチェック
                    if any(jp_name in font_name for jp_name in japanese_font_names) or \
                       self.is_japanese_font(font_path):
                        self.font_paths[font_name] = font_path
                        self.available_fonts.append(font_name)
                        
                        # 最初に見つかったフォントをデフォルトに
                        if self.default_font == "Arial":
                            self.default_font = font_name
                        
                        logging.info(f"日本語フォント検出: {font_name}")
                        
                        # 最大5個まで
                        if len(self.available_fonts) >= 5:
                            break
                            
                except:
                    continue
                    
        except Exception as e:
            logging.error(f"システムフォント検索エラー: {e}")
    
    def is_japanese_font(self, font_path: str) -> bool:
        """日本語フォントかどうかを判定（簡易版）"""
        try:
            # フォントファイルサイズで簡易判定（日本語フォントは通常大きい）
            return os.path.getsize(font_path) > 1000000  # 1MB以上
        except:
            return False
    
    def configure_matplotlib_fonts(self):
        """matplotlibのフォント設定"""
        if not MATPLOTLIB_AVAILABLE or not self.available_fonts:
            return
        
        try:
            # フォント設定
            matplotlib.rcParams['font.family'] = 'sans-serif'
            matplotlib.rcParams['font.sans-serif'] = [self.default_font] + self.available_fonts
            
            # 日本語文字化け対策
            matplotlib.rcParams['axes.unicode_minus'] = False
            
            # フォントパスを追加
            for font_path in self.font_paths.values():
                fm.fontManager.addfont(font_path)
            
            # フォントキャッシュをクリア
            try:
                fm._rebuild()
            except:
                pass
            
            logging.info(f"matplotlibフォント設定完了: {self.default_font}")
            
        except Exception as e:
            logging.error(f"matplotlibフォント設定エラー: {e}")
    
    def get_font_family(self) -> str:
        """デフォルトフォントファミリーを取得"""
        return self.default_font
    
    def get_font_config(self) -> Dict:
        """フォント設定を取得"""
        return {
            "family": self.get_font_family(),
            "available_fonts": self.available_fonts,
            "font_paths": self.font_paths
        }

# シングルトンインスタンス
font_manager = FontManager()

# 初期化
if __name__ != "__main__":
    font_manager.setup_fonts()