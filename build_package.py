#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Shift Manager - パッケージビルドスクリプト
配布用パッケージを作成するためのスクリプト
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """ビルド関連のディレクトリをクリーンアップ"""
    dirs_to_clean = ['build', 'dist', '*.egg-info', '__pycache__']
    
    for pattern in dirs_to_clean:
        if '*' in pattern:
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"削除: {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"削除: {pattern}")

def remove_pycache():
    """__pycache__ディレクトリを再帰的に削除"""
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)
            print(f"削除: {pycache_path}")

def build_wheel():
    """Wheelパッケージをビルド"""
    try:
        print("Wheelパッケージをビルド中...")
        result = subprocess.run([
            sys.executable, '-m', 'build', '--wheel'
        ], check=True, capture_output=True, text=True)
        print("Wheelビルド成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Wheelビルドエラー: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def build_sdist():
    """ソース配布パッケージをビルド"""
    try:
        print("ソース配布パッケージをビルド中...")
        result = subprocess.run([
            sys.executable, '-m', 'build', '--sdist'
        ], check=True, capture_output=True, text=True)
        print("ソース配布ビルド成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ソース配布ビルドエラー: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def install_build_deps():
    """ビルドに必要な依存関係をインストール"""
    try:
        print("ビルド依存関係をインストール中...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade',
            'build', 'wheel', 'setuptools', 'twine'
        ], check=True)
        print("ビルド依存関係のインストール完了!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依存関係インストールエラー: {e}")
        return False

def check_package():
    """パッケージの整合性をチェック"""
    try:
        print("パッケージの整合性をチェック中...")
        result = subprocess.run([
            sys.executable, '-m', 'twine', 'check', 'dist/*'
        ], check=True, capture_output=True, text=True)
        print("パッケージチェック成功!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"パッケージチェックエラー: {e}")
        print(f"エラー出力: {e.stderr}")
        return False

def main():
    """メイン処理"""
    print("=== AI Shift Manager パッケージビルド ===")
    
    # 1. ビルド依存関係のインストール
    if not install_build_deps():
        print("❌ ビルド依存関係のインストールに失敗しました")
        return False
    
    # 2. クリーンアップ
    print("\n--- クリーンアップ ---")
    clean_build()
    remove_pycache()
    
    # 3. Wheelパッケージのビルド
    print("\n--- Wheelパッケージビルド ---")
    if not build_wheel():
        print("❌ Wheelビルドに失敗しました")
        return False
    
    # 4. ソース配布パッケージのビルド
    print("\n--- ソース配布パッケージビルド ---")
    if not build_sdist():
        print("❌ ソース配布ビルドに失敗しました")
        return False
    
    # 5. パッケージの整合性チェック
    print("\n--- パッケージ整合性チェック ---")
    if not check_package():
        print("❌ パッケージチェックに失敗しました")
        return False
    
    # 6. 結果表示
    print("\n=== ビルド完了 ===")
    print("✅ パッケージが正常にビルドされました!")
    
    if os.path.exists('dist'):
        print("\n📦 作成されたパッケージ:")
        for file in os.listdir('dist'):
            file_path = os.path.join('dist', file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size:,} bytes)")
    
    print("\n🚀 インストール方法:")
    print("  pip install dist/ai_shift_manager-1.0.0-py3-none-any.whl")
    
    print("\n📤 PyPIアップロード方法:")
    print("  python -m twine upload dist/*")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)