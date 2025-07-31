# -*- coding: utf-8 -*-
"""
パフォーマンステスト
CSV vs SQLite の性能比較
"""

import time
import random
import string
from datetime import datetime, timedelta
from data.database_manager import DatabaseManager
import pandas as pd

class PerformanceTest:
    """パフォーマンステストクラス"""
    
    def __init__(self):
        self.db = DatabaseManager("test_performance.db")
        self.test_data = []
    
    def generate_test_data(self, count: int = 1000):
        """テストデータ生成"""
        departments = ['営業部', '総務部', '管理部', '製造部', '販売部']
        positions = ['スタッフ', 'リーダー', '主任', '係長']
        employment_types = ['正社員', 'パート', 'アルバイト']
        
        self.test_data = []
        
        for i in range(count):
            staff_data = {
                'staff_id': f'EMP{i+1:04d}',
                'name': f'テスト{i+1:04d}',
                'department': random.choice(departments),
                'position': random.choice(positions),
                'hourly_wage': random.randint(800, 2000),
                'employment_type': random.choice(employment_types),
                'hire_date': (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime('%Y-%m-%d'),
                'skill_level': random.randint(1, 5),
                'preferred_hours': 'フルタイム',
                'contact': f'090-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                'notes': f'テストデータ{i+1}'
            }
            self.test_data.append(staff_data)
    
    def test_sqlite_performance(self):
        """SQLite性能テスト"""
        print("=== SQLite性能テスト ===")
        
        # 1. 一括挿入テスト
        start_time = time.time()
        for staff_data in self.test_data:
            self.db.add_staff(staff_data)
        insert_time = time.time() - start_time
        print(f"挿入時間 ({len(self.test_data)}件): {insert_time:.3f}秒")
        
        # 2. 全件取得テスト
        start_time = time.time()
        all_staff = self.db.get_staff_list()
        select_all_time = time.time() - start_time
        print(f"全件取得時間 ({len(all_staff)}件): {select_all_time:.3f}秒")
        
        # 3. 検索テスト
        start_time = time.time()
        for i in range(100):
            search_term = f"テスト{random.randint(1, len(self.test_data)):04d}"
            results = self.db.search_staff(search_term)
        search_time = time.time() - start_time
        print(f"検索時間 (100回): {search_time:.3f}秒")
        
        # 4. 更新テスト
        start_time = time.time()
        for i in range(100):
            staff_id = f'EMP{random.randint(1, len(self.test_data)):04d}'
            update_data = {'hourly_wage': random.randint(800, 2000)}
            self.db.update_staff(staff_id, update_data)
        update_time = time.time() - start_time
        print(f"更新時間 (100回): {update_time:.3f}秒")
        
        return {
            'insert_time': insert_time,
            'select_all_time': select_all_time,
            'search_time': search_time,
            'update_time': update_time
        }
    
    def test_csv_performance(self):
        """CSV性能テスト"""
        print("\n=== CSV性能テスト ===")
        
        # DataFrameに変換
        df = pd.DataFrame(self.test_data)
        
        # 1. CSV保存テスト
        start_time = time.time()
        df.to_csv('test_performance.csv', index=False, encoding='utf-8')
        save_time = time.time() - start_time
        print(f"CSV保存時間 ({len(self.test_data)}件): {save_time:.3f}秒")
        
        # 2. CSV読み込みテスト
        start_time = time.time()
        loaded_df = pd.read_csv('test_performance.csv', encoding='utf-8')
        load_time = time.time() - start_time
        print(f"CSV読み込み時間 ({len(loaded_df)}件): {load_time:.3f}秒")
        
        # 3. 検索テスト
        start_time = time.time()
        for i in range(100):
            search_term = f"テスト{random.randint(1, len(self.test_data)):04d}"
            results = loaded_df[loaded_df['name'].str.contains(search_term, na=False)]
        search_time = time.time() - start_time
        print(f"検索時間 (100回): {search_time:.3f}秒")
        
        # 4. 更新テスト
        start_time = time.time()
        for i in range(100):
            staff_id = f'EMP{random.randint(1, len(self.test_data)):04d}'
            mask = loaded_df['staff_id'] == staff_id
            loaded_df.loc[mask, 'hourly_wage'] = random.randint(800, 2000)
        update_time = time.time() - start_time
        print(f"更新時間 (100回): {update_time:.3f}秒")
        
        return {
            'save_time': save_time,
            'load_time': load_time,
            'search_time': search_time,
            'update_time': update_time
        }
    
    def run_comparison(self, data_count: int = 1000):
        """性能比較実行"""
        print(f"📊 パフォーマンステスト開始 (データ数: {data_count}件)")
        print("="*50)
        
        # テストデータ生成
        self.generate_test_data(data_count)
        
        # SQLiteテスト
        sqlite_results = self.test_sqlite_performance()
        
        # CSVテスト
        csv_results = self.test_csv_performance()
        
        # 結果比較
        print("\n📈 性能比較結果")
        print("="*50)
        
        comparisons = [
            ("データ挿入/保存", sqlite_results['insert_time'], csv_results['save_time']),
            ("データ読み込み", sqlite_results['select_all_time'], csv_results['load_time']),
            ("検索処理", sqlite_results['search_time'], csv_results['search_time']),
            ("更新処理", sqlite_results['update_time'], csv_results['update_time'])
        ]
        
        for operation, sqlite_time, csv_time in comparisons:
            improvement = ((csv_time - sqlite_time) / csv_time * 100) if csv_time > 0 else 0
            faster = "SQLite" if sqlite_time < csv_time else "CSV"
            
            print(f"{operation}:")
            print(f"  SQLite: {sqlite_time:.3f}秒")
            print(f"  CSV:    {csv_time:.3f}秒")
            print(f"  結果:   {faster}が{abs(improvement):.1f}%高速")
            print()
        
        # 総合評価
        sqlite_total = sum(sqlite_results.values())
        csv_total = sum(csv_results.values())
        overall_improvement = ((csv_total - sqlite_total) / csv_total * 100) if csv_total > 0 else 0
        
        print(f"🏆 総合結果:")
        print(f"SQLite総時間: {sqlite_total:.3f}秒")
        print(f"CSV総時間:    {csv_total:.3f}秒")
        print(f"SQLiteが{overall_improvement:.1f}%高速")
        
        return sqlite_results, csv_results

if __name__ == "__main__":
    test = PerformanceTest()
    test.run_comparison(1000)