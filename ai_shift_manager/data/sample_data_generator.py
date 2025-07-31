# -*- coding: utf-8 -*-
"""
リアルなサンプルデータ生成器
実際の企業で使われそうなタイムカードデータを大量生成
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import json
import os

class SampleDataGenerator:
    """リアルなサンプルデータ生成クラス"""
    
    def __init__(self):
        # 業界別設定
        self.industry_templates = {
            'retail': {
                'name': '小売店',
                'departments': ['レジ', 'フロア', '倉庫', '管理'],
                'positions': ['スタッフ', 'リーダー', '主任', '店長'],
                'shifts': ['早番', '中番', '遅番'],
                'business_hours': (9, 21),
                'peak_hours': [(11, 13), (17, 19)]
            },
            'restaurant': {
                'name': '飲食店',
                'departments': ['ホール', 'キッチン', 'レジ', '管理'],
                'positions': ['スタッフ', 'リーダー', 'シェフ', '店長'],
                'shifts': ['モーニング', 'ランチ', 'ディナー', '深夜'],
                'business_hours': (7, 23),
                'peak_hours': [(11, 14), (18, 21)]
            },
            'office': {
                'name': '事務所',
                'departments': ['営業部', '総務部', '経理部', '管理部'],
                'positions': ['スタッフ', '主任', '係長', '課長'],
                'shifts': ['日勤'],
                'business_hours': (9, 18),
                'peak_hours': [(10, 12), (14, 16)]
            }
        }
        
        # 日本人の名前サンプル
        self.sample_names = [
            '田中太郎', '佐藤花子', '鈴木次郎', '山田美咲', '高橋健太',
            '渡辺由美', '伊藤大輔', '中村真理', '小林和也', '加藤恵子',
            '吉田雄一', '山本さくら', '松本直樹', '井上麻衣', '木村拓也',
            '林美穂', '清水健二', '森田愛', '池田正人', '橋本千春'
        ]
    
    def generate_comprehensive_data(self, industry: str = 'retail', 
                                  staff_count: int = 15, 
                                  days: int = 30) -> Dict[str, pd.DataFrame]:
        """包括的なサンプルデータ生成"""
        
        if industry not in self.industry_templates:
            industry = 'retail'
        
        template = self.industry_templates[industry]
        
        # 1. スタッフマスター生成
        staff_df = self._generate_staff_master(staff_count, template)
        
        # 2. タイムカードデータ生成
        timecard_df = self._generate_timecard_data(staff_df, template, days)
        
        # 3. シフト希望データ生成
        preferences_df = self._generate_shift_preferences(staff_df, template)
        
        # 4. 欠勤データ生成
        absence_df = self._generate_absence_data(staff_df, days)
        
        return {
            'staff': staff_df,
            'timecard': timecard_df,
            'preferences': preferences_df,
            'absence': absence_df,
            'metadata': {
                'industry': template['name'],
                'generated_date': datetime.now().isoformat(),
                'staff_count': staff_count,
                'days_covered': days
            }
        }
    
    def _generate_staff_master(self, count: int, template: Dict) -> pd.DataFrame:
        """スタッフマスター生成"""
        staff_data = []
        
        for i in range(count):
            staff_id = f"EMP{i+1:03d}"
            name = random.choice(self.sample_names)
            department = random.choice(template['departments'])
            position = random.choice(template['positions'])
            
            # 役職に応じた時給設定
            wage_ranges = {
                'スタッフ': (900, 1200),
                'リーダー': (1200, 1500),
                '主任': (1400, 1700),
                '係長': (1600, 2000),
                '課長': (1800, 2500),
                'シェフ': (1300, 1800),
                '店長': (2000, 3000)
            }
            
            wage = random.randint(*wage_ranges.get(position, (1000, 1500)))
            
            employment_types = ['正社員', 'パート', 'アルバイト']
            employment_weights = [0.3, 0.4, 0.3]
            employment_type = random.choices(employment_types, weights=employment_weights)[0]
            
            hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
            
            staff_data.append({
                '従業員ID': staff_id,
                '氏名': name,
                '部門': department,
                '役職': position,
                '時給': wage,
                '雇用形態': employment_type,
                '入社日': hire_date.strftime('%Y-%m-%d'),
                'スキルレベル': random.randint(1, 5),
                '希望勤務時間': random.choice(['フルタイム', '午前のみ', '午後のみ', '夕方以降', '土日のみ']),
                '連絡先': f"090-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                '備考': random.choice(['', '研修中', 'リーダー候補', '経験豊富', '新人'])
            })
        
        return pd.DataFrame(staff_data)    

    def _generate_timecard_data(self, staff_df: pd.DataFrame, 
                               template: Dict, days: int) -> pd.DataFrame:
        """リアルなタイムカードデータ生成"""
        timecard_data = []
        
        start_date = datetime.now() - timedelta(days=days)
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 土日の出勤率を下げる
            is_weekend = current_date.weekday() >= 5
            attendance_rate = 0.4 if is_weekend else 0.85
            
            for _, staff in staff_df.iterrows():
                # 出勤するかどうか
                if random.random() > attendance_rate:
                    continue
                
                # 遅刻・早退の確率
                is_late = random.random() < 0.1
                is_early_leave = random.random() < 0.05
                
                # 基本勤務時間
                business_start, business_end = template['business_hours']
                
                # 出勤時間（遅刻考慮）
                scheduled_start = business_start
                if staff['雇用形態'] == 'パート':
                    # パートは様々な時間帯
                    scheduled_start = random.choice([9, 10, 13, 17])
                
                actual_start = scheduled_start
                if is_late:
                    actual_start += random.uniform(0.1, 0.5)  # 6-30分遅刻
                
                # 退勤時間
                if staff['雇用形態'] == 'パート':
                    work_hours = random.choice([4, 5, 6, 8])
                else:
                    work_hours = 8
                
                scheduled_end = scheduled_start + work_hours
                actual_end = scheduled_end
                
                if is_early_leave:
                    actual_end -= random.uniform(0.5, 1.0)  # 30-60分早退
                
                # 休憩時間
                break_minutes = 60 if work_hours >= 6 else 0
                
                # 実働時間計算
                actual_work_hours = actual_end - actual_start
                actual_work_minutes = int(actual_work_hours * 60) - break_minutes
                
                # 業務内容（部門に応じて）
                work_content_map = {
                    'レジ': ['レジ操作', '接客', '商品案内'],
                    'フロア': ['接客', '商品陳列', '清掃'],
                    'キッチン': ['調理', '仕込み', '清掃'],
                    'ホール': ['接客', 'オーダー取り', '配膳'],
                    '営業部': ['顧客対応', '資料作成', '外回り'],
                    '総務部': ['事務処理', '電話対応', '来客対応']
                }
                
                work_content = random.choice(
                    work_content_map.get(staff['部門'], ['一般業務'])
                )
                
                # パフォーマンス評価
                base_performance = 4.0
                if staff['スキルレベル'] >= 4:
                    base_performance = 4.5
                elif staff['スキルレベル'] <= 2:
                    base_performance = 3.5
                
                performance = base_performance + random.uniform(-0.5, 0.5)
                performance = max(1.0, min(5.0, performance))
                
                timecard_data.append({
                    '日付': date_str,
                    '従業員ID': staff['従業員ID'],
                    '氏名': staff['氏名'],
                    '部門': staff['部門'],
                    '役職': staff['役職'],
                    '予定開始': f"{int(scheduled_start):02d}:{int((scheduled_start % 1) * 60):02d}",
                    '実際出勤': f"{int(actual_start):02d}:{int((actual_start % 1) * 60):02d}",
                    '実際退勤': f"{int(actual_end):02d}:{int((actual_end % 1) * 60):02d}",
                    '休憩時間': break_minutes,
                    '実働時間': max(0, actual_work_minutes),
                    '業務内容': work_content,
                    '評価': round(performance, 1),
                    '勤務場所': template['name'],
                    '出勤状況': '遅刻' if is_late else '早退' if is_early_leave else '正常'
                })
        
        return pd.DataFrame(timecard_data)
    
    def _generate_shift_preferences(self, staff_df: pd.DataFrame, 
                                  template: Dict) -> pd.DataFrame:
        """シフト希望データ生成"""
        preferences_data = []
        
        for _, staff in staff_df.iterrows():
            # 各曜日の希望を生成
            for day_of_week in range(7):  # 0=月曜, 6=日曜
                day_names = ['月', '火', '水', '木', '金', '土', '日']
                
                # 雇用形態に応じた勤務希望
                if staff['雇用形態'] == '正社員':
                    availability = 4 if day_of_week < 5 else 2  # 平日優先
                elif staff['雇用形態'] == 'パート':
                    availability = random.choice([2, 3, 4])
                else:  # アルバイト
                    availability = 3 if day_of_week >= 5 else 2  # 土日優先
                
                if availability >= 2:  # 勤務可能な場合のみ
                    start_time = random.choice(['09:00', '10:00', '13:00', '17:00'])
                    end_time_options = {
                        '09:00': ['17:00', '18:00'],
                        '10:00': ['18:00', '19:00'],
                        '13:00': ['21:00', '22:00'],
                        '17:00': ['21:00', '22:00', '23:00']
                    }
                    end_time = random.choice(end_time_options[start_time])
                    
                    preferences_data.append({
                        '従業員ID': staff['従業員ID'],
                        '氏名': staff['氏名'],
                        '曜日': day_names[day_of_week],
                        '希望開始時間': start_time,
                        '希望終了時間': end_time,
                        '優先度': availability,
                        '特記事項': random.choice(['', '学校あり', '他バイトあり', '家庭の事情'])
                    })
        
        return pd.DataFrame(preferences_data)
    
    def _generate_absence_data(self, staff_df: pd.DataFrame, days: int) -> pd.DataFrame:
        """欠勤データ生成"""
        absence_data = []
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 各スタッフに対して欠勤を生成
        for _, staff in staff_df.iterrows():
            # 欠勤回数（月1-2回程度）
            absence_count = random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.1, 0.05])[0]
            
            for _ in range(absence_count):
                absence_date = start_date + timedelta(days=random.randint(0, days-1))
                
                absence_types = ['体調不良', '家庭の事情', '急用', '交通機関遅延', '私用']
                absence_type = random.choice(absence_types)
                
                # 通知タイミング
                notification_times = ['前日', '当日朝', '当日直前', '無断']
                notification_time = random.choices(
                    notification_times, 
                    weights=[0.4, 0.4, 0.15, 0.05]
                )[0]
                
                absence_data.append({
                    '欠勤日': absence_date.strftime('%Y-%m-%d'),
                    '従業員ID': staff['従業員ID'],
                    '氏名': staff['氏名'],
                    '部門': staff['部門'],
                    '欠勤理由': absence_type,
                    '通知タイミング': notification_time,
                    '代替要員': random.choice(['あり', 'なし', '調整中']),
                    '影響度': random.choice(['軽微', '中程度', '深刻'])
                })
        
        return pd.DataFrame(absence_data)
    
    def save_sample_data(self, data_dict: Dict, output_dir: str = 'sample_data'):
        """サンプルデータをファイル保存"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # CSV形式で保存
        for data_type, df in data_dict.items():
            if isinstance(df, pd.DataFrame):
                filename = f"{output_dir}/{data_type}_sample.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ {data_type}データ保存: {filename} ({len(df)}件)")
        
        # メタデータをJSON保存
        if 'metadata' in data_dict:
            with open(f"{output_dir}/metadata.json", 'w', encoding='utf-8') as f:
                json.dump(data_dict['metadata'], f, ensure_ascii=False, indent=2)
            print(f"✅ メタデータ保存: {output_dir}/metadata.json")
    
    def create_demo_scenario(self, industry: str = 'retail') -> Dict:
        """デモ用シナリオデータ作成"""
        print(f"🎬 {self.industry_templates[industry]['name']}のデモシナリオ作成中...")
        
        # リアルなデータ生成
        data = self.generate_comprehensive_data(
            industry=industry,
            staff_count=12,  # デモに適したサイズ
            days=21  # 3週間分
        )
        
        # デモ用の特別なシナリオを追加
        demo_scenarios = self._create_demo_scenarios(data)
        data['demo_scenarios'] = demo_scenarios
        
        return data
    
    def _create_demo_scenarios(self, data: Dict) -> List[Dict]:
        """デモ用シナリオ作成"""
        scenarios = [
            {
                'title': '🔥 緊急欠勤対応',
                'description': '朝一番でスタッフから欠勤連絡。即座に代替要員を見つける必要がある。',
                'absent_staff_id': data['staff'].iloc[0]['従業員ID'],
                'absence_date': datetime.now().strftime('%Y-%m-%d'),
                'urgency': 'high'
            },
            {
                'title': '📅 週末シフト調整',
                'description': '土日の忙しい時間帯で人手不足。経験豊富なスタッフが必要。',
                'absent_staff_id': data['staff'].iloc[1]['従業員ID'],
                'absence_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'urgency': 'medium'
            }
        ]
        
        return scenarios


def main():
    """メイン実行関数"""
    print("🚀 リアルなサンプルデータ生成開始")
    print("="*50)
    
    generator = SampleDataGenerator()
    
    # 業界別データ生成
    industries = ['retail', 'restaurant', 'office']
    
    for industry in industries:
        print(f"\n📊 {generator.industry_templates[industry]['name']}のデータ生成中...")
        
        # データ生成
        data = generator.create_demo_scenario(industry)
        
        # 保存
        output_dir = f"sample_data_{industry}"
        generator.save_sample_data(data, output_dir)
        
        print(f"✅ {generator.industry_templates[industry]['name']}完了!")
    
    print("\n🎉 全業界のサンプルデータ生成完了!")
    print("="*50)
    print("\n📁 生成されたファイル:")
    print("  📂 sample_data_retail/")
    print("  📂 sample_data_restaurant/") 
    print("  📂 sample_data_office/")
    print("\n🎯 次のステップ:")
    print("  1. python test_emergency_system.py でテスト実行")
    print("  2. 生成されたCSVファイルで実際の動作確認")
    print("  3. デモ・プレゼンテーション用データとして活用")

if __name__ == "__main__":
    main()