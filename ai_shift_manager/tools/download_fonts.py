# -*- coding: utf-8 -*-
"""
日本語フォントダウンロードツール
IPAフォントを自動ダウンロードして配置
"""

import os
import sys
import zipfile
import shutil
import tempfile
from urllib.request import urlretrieve
import logging

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FontDownloader:
    """フォントダウンロードクラス"""
    
    def __init__(self):
        self.font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
        self.temp_dir = tempfile.mkdtemp()
        
        # IPAフォントのURL
        self.ipa_url = "https://moji.or.jp/wp-content/ipafont/IPAexfont/IPAexfont00401.zip"
        
        # ダウンロードするフォントファイル名
        self.target_fonts = [
            "ipaexg.ttf",  # IPAexゴシック
            "ipaexm.ttf"   # IPAex明朝
        ]
    
    def download_fonts(self):
        """フォントをダウンロード"""
        print("📥 日本語フォントをダウンロード中...")
        
        # フォントディレクトリを作成
        os.makedirs(self.font_dir, exist_ok=True)
        
        try:
            # ZIPファイルをダウンロード
            zip_path = os.path.join(self.temp_dir, "ipaexfont.zip")
            urlretrieve(self.ipa_url, zip_path)
            print("✅ ダウンロード完了")
            
            # ZIPを解凍
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            print("✅ 解凍完了")
            
            # フォントファイルをコピー
            extracted_dir = None
            for item in os.listdir(self.temp_dir):
                if os.path.isdir(os.path.join(self.temp_dir, item)) and "IPAex" in item:
                    extracted_dir = os.path.join(self.temp_dir, item)
                    break
            
            if not extracted_dir:
                print("❌ 解凍されたフォントディレクトリが見つかりません")
                return False
            
            # 対象フォントをコピー
            copied_count = 0
            for font_file in self.target_fonts:
                src_path = os.path.join(extracted_dir, font_file)
                if os.path.exists(src_path):
                    dst_path = os.path.join(self.font_dir, font_file)
                    shutil.copy2(src_path, dst_path)
                    print(f"✅ フォントコピー完了: {font_file}")
                    copied_count += 1
            
            if copied_count == 0:
                print("❌ フォントファイルが見つかりませんでした")
                return False
            
            print(f"🎉 {copied_count}個のフォントを正常にインストールしました")
            print(f"📂 フォントディレクトリ: {self.font_dir}")
            return True
            
        except Exception as e:
            print(f"❌ フォントダウンロードエラー: {e}")
            return False
        
        finally:
            # 一時ディレクトリを削除
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
    
    def check_existing_fonts(self):
        """既存のフォントをチェック"""
        if not os.path.exists(self.font_dir):
            return []
        
        existing_fonts = []
        for font_file in self.target_fonts:
            font_path = os.path.join(self.font_dir, font_file)
            if os.path.exists(font_path):
                existing_fonts.append(font_file)
        
        return existing_fonts
    
    def install_fonts(self):
        """フォントインストールのメイン処理"""
        print("🔍 既存フォントをチェック中...")
        existing_fonts = self.check_existing_fonts()
        
        if len(existing_fonts) == len(self.target_fonts):
            print("✅ すべての日本語フォントが既にインストールされています")
            for font in existing_fonts:
                print(f"   - {font}")
            return True
        
        print(f"📥 {len(self.target_fonts) - len(existing_fonts)}個のフォントをダウンロードします...")
        return self.download_fonts()

def main():
    """メイン処理"""
    print("=" * 50)
    print("🎨 AI Shift Manager - 日本語フォントセットアップ")
    print("=" * 50)
    
    downloader = FontDownloader()
    success = downloader.install_fonts()
    
    if success:
        print("\n🎉 フォントセットアップが完了しました！")
        print("💡 アプリケーションを再起動してください。")
    else:
        print("\n❌ フォントセットアップに失敗しました。")
        print("💡 手動でIPAフォントをダウンロードして fonts/ ディレクトリに配置してください。")
    
    return success

if __name__ == "__main__":
    main()