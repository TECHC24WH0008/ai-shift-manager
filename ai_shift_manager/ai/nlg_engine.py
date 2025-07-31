# -*- coding: utf-8 -*-
"""
自然言語生成エンジン
完全オフラインで高品質な日本語説明文を生成
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import re

class NaturalLanguageGenerator:
    """自然言語説明生成エンジン（完全オフライン）"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.personality = "professional"  # professional, friendly, casual
        self.context_memory = {}
        self.usage_history = defaultdict(int)
        self.quality_threshold = 0.8
    
    def _load_templates(self) -> Dict:
        """テンプレートを読み込み"""
        return {
            "substitute_recommendation": {
                "high_score": [
                    "{name}さんを強く推奨いたします。{reason_main}で、{reason_sub}です。",
                    "{name}さんが最適な候補者です。{reason_main}し、{reason_sub}ため安心してお任せできます。",
                    "{name}さんなら間違いありません。{reason_main}上、{reason_sub}実績があります。",
                    "{name}さんを第一候補として提案いたします。{reason_main}であり、{reason_sub}点で優れています。"
                ],
                "medium_score": [
                    "{name}さんはいかがでしょうか。{reason_main}ので、{reason_sub}と思います。",
                    "{name}さんも候補として考えられます。{reason_main}し、{reason_sub}でしょう。",
                    "{name}さんという選択肢もあります。{reason_main}ため、{reason_sub}はずです。",
                    "{name}さんを推奨いたします。{reason_main}であり、{reason_sub}と判断されます。"
                ],
                "low_score": [
                    "{name}さんも可能性はありますが、{concern}点にご注意ください。ただし{reason_main}ので、緊急時には対応可能です。",
                    "{name}さんは{concern}ものの、{reason_main}ため、必要に応じて検討してください。",
                    "{name}さんについては{concern}要因がありますが、{reason_main}という利点もあります。"
                ]
            },
            "shift_analysis": {
                "excellent": [
                    "今週のシフトは理想的な配置となっています。",
                    "非常にバランスの取れた優秀なシフト構成です。",
                    "完璧に近いシフト配分が実現できました。"
                ],
                "good": [
                    "今週のシフトは良好な状態です。",
                    "適切なシフト配置ができています。",
                    "効率的で公平なシフトが組めました。"
                ],
                "warning": [
                    "いくつか注意すべき点があります。",
                    "改善の余地がある部分が見受けられます。",
                    "以下の点について確認が必要です。"
                ],
                "critical": [
                    "重要な問題が発見されました。",
                    "緊急に対応が必要な事項があります。",
                    "法令遵守の観点から確認が必要です。"
                ]
            },
            "reasons": {
                "experience": [
                    "同じ部門での勤務経験が豊富",
                    "類似業務の経験が十分",
                    "過去に同様の対応実績がある",
                    "ベテランスタッフとして信頼できる",
                    "長期間の勤務実績がある",
                    "専門知識を持っている"
                ],
                "availability": [
                    "勤務可能時間が一致している",
                    "スケジュールに余裕がある",
                    "希望勤務時間帯と合致している",
                    "柔軟な対応が可能",
                    "即座に対応できる状況",
                    "時間的制約が少ない"
                ],
                "performance": [
                    "勤務態度が非常に良好",
                    "お客様からの評価が高い",
                    "チームワークを大切にする",
                    "責任感が強く信頼できる",
                    "業務品質が安定している",
                    "問題解決能力に優れている"
                ],
                "balance": [
                    "今月の勤務時間がまだ余裕がある",
                    "公平な勤務配分の観点から適切",
                    "ワークライフバランスが保たれている",
                    "適度な勤務頻度を維持できる",
                    "負荷分散の観点から最適",
                    "健康的な勤務パターンを維持"
                ],
                "skills": [
                    "必要なスキルを十分に備えている",
                    "多様な業務に対応できる",
                    "学習能力が高い",
                    "新しい環境に適応しやすい",
                    "コミュニケーション能力が優秀",
                    "リーダーシップを発揮できる"
                ]
            },
            "concerns": [
                "他部門のため慣れが必要な",
                "勤務時間が上限に近い",
                "連続勤務が続いている",
                "研修が必要な業務がある",
                "経験が浅い分野での",
                "体調管理に注意が必要な",
                "スケジュール調整が複雑な"
            ],
            "urgency_expressions": {
                "immediate": ["緊急に", "即座に", "直ちに", "至急"],
                "urgent": ["早急に", "速やかに", "優先的に", "迅速に"],
                "high": ["なるべく早く", "可能な限り迅速に", "優先して"],
                "medium": ["適切なタイミングで", "計画的に", "段階的に"],
                "low": ["余裕をもって", "時間をかけて", "慎重に"]
            }
        }
    
    def generate_substitute_explanation(self, candidate: Dict[str, Any], 
                                      context: Dict[str, Any] = None) -> str:
        """代替候補の説明を生成"""
        name = candidate.get('name', '候補者')
        score = candidate.get('score', 50)
        experience = candidate.get('experience', '中')
        department = candidate.get('department', '同部門')
        availability = candidate.get('availability', '○')
        
        # 文脈を考慮した調整
        if context:
            urgency = context.get('urgency_level', 'medium')
            business_impact = context.get('business_impact', 'medium')
            
            # 緊急度に応じてスコア閾値を調整
            if urgency in ['immediate', 'urgent']:
                score_adjustment = 5  # 緊急時は基準を少し下げる
            else:
                score_adjustment = 0
        else:
            score_adjustment = 0
        
        adjusted_score = score + score_adjustment
        
        # スコアに基づいてテンプレート選択
        if adjusted_score >= 85:
            template_key = "high_score"
        elif adjusted_score >= 65:
            template_key = "medium_score"
        else:
            template_key = "low_score"
        
        # 使用頻度を考慮してテンプレート選択
        available_templates = self.templates["substitute_recommendation"][template_key]
        template = self._select_template_by_usage(available_templates)
        
        # 理由を生成
        reasons = self._generate_comprehensive_reasons(candidate, context)
        concern = self._select_appropriate_concern(candidate) if adjusted_score < 65 else ""
        
        # テンプレートに値を埋め込み
        explanation = template.format(
            name=name,
            reason_main=reasons["main"],
            reason_sub=reasons["sub"],
            concern=concern
        )
        
        # 使用履歴を更新
        self.usage_history[template] += 1
        
        # 後処理で品質向上
        enhanced_explanation = self._enhance_explanation(explanation, candidate, context)
        
        return enhanced_explanation
    
    def _select_template_by_usage(self, templates: List[str]) -> str:
        """使用頻度を考慮してテンプレートを選択"""
        # 使用頻度の低いテンプレートを優先
        template_scores = []
        for template in templates:
            usage_count = self.usage_history.get(template, 0)
            # 使用回数が少ないほど高スコア
            score = 1.0 / (usage_count + 1)
            template_scores.append((template, score))
        
        # 重み付きランダム選択
        total_score = sum(score for _, score in template_scores)
        if total_score == 0:
            return random.choice(templates)
        
        rand_val = random.random() * total_score
        cumulative = 0
        
        for template, score in template_scores:
            cumulative += score
            if rand_val <= cumulative:
                return template
        
        return templates[0]  # フォールバック
    
    def _generate_comprehensive_reasons(self, candidate: Dict[str, Any], 
                                      context: Dict[str, Any] = None) -> Dict[str, str]:
        """包括的な理由を生成"""
        experience = candidate.get('experience', '中')
        department = candidate.get('department', '同部門')
        score = candidate.get('score', 50)
        availability = candidate.get('availability', '○')
        workload = candidate.get('workload', 50)
        past_substitutions = candidate.get('past_substitutions', 0)
        
        reasons = {"main": "", "sub": ""}
        
        # メイン理由の選択ロジック
        reason_candidates = []
        
        if experience == '高':
            reason_candidates.extend(self.templates["reasons"]["experience"])
        
        if availability == '○':
            reason_candidates.extend(self.templates["reasons"]["availability"])
        
        if score >= 80:
            reason_candidates.extend(self.templates["reasons"]["performance"])
        
        if workload < 70:
            reason_candidates.extend(self.templates["reasons"]["balance"])
        
        if past_substitutions > 3:
            reason_candidates.extend(self.templates["reasons"]["skills"])
        
        # メイン理由を選択
        if reason_candidates:
            reasons["main"] = random.choice(reason_candidates)
        else:
            reasons["main"] = random.choice(self.templates["reasons"]["performance"])
        
        # サブ理由の選択（メイン理由と異なるカテゴリから）
        sub_reason_categories = ["performance", "balance", "skills"]
        if department == '同部門':
            sub_reason_categories.append("experience")
        
        # メイン理由のカテゴリを特定して除外
        main_category = self._identify_reason_category(reasons["main"])
        available_sub_categories = [cat for cat in sub_reason_categories if cat != main_category]
        
        if available_sub_categories:
            sub_category = random.choice(available_sub_categories)
            reasons["sub"] = random.choice(self.templates["reasons"][sub_category])
        else:
            reasons["sub"] = random.choice(self.templates["reasons"]["performance"])
        
        return reasons
    
    def _identify_reason_category(self, reason: str) -> str:
        """理由文からカテゴリを特定"""
        for category, reason_list in self.templates["reasons"].items():
            if reason in reason_list:
                return category
        return "performance"  # デフォルト
    
    def _select_appropriate_concern(self, candidate: Dict[str, Any]) -> str:
        """適切な懸念事項を選択"""
        concerns = []
        
        department = candidate.get('department', '同部門')
        workload = candidate.get('workload', 50)
        experience = candidate.get('experience', '中')
        consecutive_days = candidate.get('consecutive_days', 0)
        
        if department != '同部門':
            concerns.append("他部門のため慣れが必要な")
        
        if workload > 80:
            concerns.append("勤務時間が上限に近い")
        
        if consecutive_days >= 4:
            concerns.append("連続勤務が続いている")
        
        if experience == '低':
            concerns.append("研修が必要な業務がある")
        
        if concerns:
            return random.choice(concerns)
        else:
            return random.choice(self.templates["concerns"])
    
    def _enhance_explanation(self, explanation: str, candidate: Dict[str, Any], 
                           context: Dict[str, Any] = None) -> str:
        """説明文を品質向上"""
        enhanced = explanation
        
        # 数値的根拠を追加
        score = candidate.get('score', 50)
        if score >= 80:
            enhanced = self._add_numerical_evidence(enhanced, candidate)
        
        # 緊急度に応じた表現調整
        if context and context.get('urgency_level') in ['immediate', 'urgent']:
            enhanced = self._add_urgency_expression(enhanced, context['urgency_level'])
        
        # 重複表現の除去
        enhanced = self._remove_redundancy(enhanced)
        
        # 敬語の統一
        enhanced = self._normalize_politeness(enhanced)
        
        return enhanced
    
    def _add_numerical_evidence(self, text: str, candidate: Dict[str, Any]) -> str:
        """数値的根拠を追加"""
        score = candidate.get('score', 50)
        past_substitutions = candidate.get('past_substitutions', 0)
        customer_rating = candidate.get('customer_rating', 0)
        
        additions = []
        
        if score >= 90:
            additions.append(f"適性スコア{score}点の優秀な評価")
        
        if past_substitutions > 5:
            additions.append(f"過去{past_substitutions}回の代替勤務実績")
        
        if customer_rating >= 4.5:
            additions.append(f"顧客評価{customer_rating}/5.0の高評価")
        
        if additions:
            evidence = "、".join(additions)
            # 文末の前に挿入
            if text.endswith("。"):
                text = text[:-1] + f"（{evidence}）。"
            else:
                text += f"（{evidence}）"
        
        return text
    
    def _add_urgency_expression(self, text: str, urgency_level: str) -> str:
        """緊急度表現を追加"""
        urgency_expr = random.choice(self.templates["urgency_expressions"].get(urgency_level, ["適切に"]))
        
        # 文頭に緊急度表現を追加
        if urgency_level in ['immediate', 'urgent']:
            text = f"{urgency_expr}対応が必要な状況において、" + text
        
        return text
    
    def _remove_redundancy(self, text: str) -> str:
        """重複表現を除去"""
        # 同じ単語の連続使用を検出・修正
        words = text.split()
        filtered_words = []
        prev_word = ""
        
        for word in words:
            # 助詞や語尾は重複を許可
            if word != prev_word or word in ["です", "ます", "。", "、", "の", "に", "を", "が", "は"]:
                filtered_words.append(word)
            prev_word = word
        
        return ''.join(filtered_words)
    
    def _normalize_politeness(self, text: str) -> str:
        """敬語・丁寧語を統一"""
        # 基本的な敬語変換
        replacements = {
            'できる': 'できます',
            'ある': 'あります', 
            'いる': 'います',
            '高い': '高く',
            '良い': '良く',
            'なる': 'なります',
            'する': 'いたします'
        }
        
        for old, new in replacements.items():
            # 語尾のみ置換（部分一致を避ける）
            text = re.sub(f'{old}(?=[。、]|$)', new, text)
        
        return text
    
    def generate_shift_summary(self, shift_data: Dict[str, Any]) -> str:
        """シフト全体の要約を生成"""
        total_staff = shift_data.get('total_staff', 0)
        coverage_rate = shift_data.get('coverage_rate', 0)
        issues = shift_data.get('issues', [])
        efficiency_score = shift_data.get('efficiency_score', 0)
        
        summary = ""
        
        # 全体評価の決定
        if coverage_rate >= 98 and len(issues) == 0 and efficiency_score >= 90:
            evaluation_key = "excellent"
        elif coverage_rate >= 95 and len(issues) <= 1:
            evaluation_key = "good"
        elif coverage_rate >= 80 or len(issues) <= 3:
            evaluation_key = "warning"
        else:
            evaluation_key = "critical"
        
        summary += random.choice(self.templates["shift_analysis"][evaluation_key])
        
        # 詳細情報
        summary += f"\n\n📊 詳細分析:\n"
        summary += f"• 配置スタッフ数: {total_staff}名\n"
        summary += f"• カバー率: {coverage_rate}%\n"
        
        if efficiency_score > 0:
            summary += f"• 効率性スコア: {efficiency_score}点\n"
        
        # 問題点の詳細
        if issues:
            summary += f"\n⚠️ 注意事項:\n"
            for i, issue in enumerate(issues, 1):
                summary += f"  {i}. {issue}\n"
        
        # 改善提案
        if evaluation_key in ["warning", "critical"]:
            summary += f"\n💡 改善提案:\n"
            suggestions = self._generate_improvement_suggestions(shift_data)
            for suggestion in suggestions:
                summary += f"• {suggestion}\n"
        
        return summary
    
    def _generate_improvement_suggestions(self, shift_data: Dict[str, Any]) -> List[str]:
        """改善提案を生成"""
        suggestions = []
        coverage_rate = shift_data.get('coverage_rate', 0)
        issues = shift_data.get('issues', [])
        
        if coverage_rate < 90:
            suggestions.append("人員配置の見直しを検討してください")
        
        if any("不足" in issue for issue in issues):
            suggestions.append("追加スタッフの確保を推奨します")
        
        if any("連続" in issue for issue in issues):
            suggestions.append("連続勤務の制限を設けることをお勧めします")
        
        if not suggestions:
            suggestions.append("現在の配置を維持しつつ、定期的な見直しを行ってください")
        
        return suggestions
    
    def generate_schedule_description(self, date: str, shifts: List[Dict]) -> str:
        """特定日のスケジュール説明を生成"""
        if not shifts:
            return f"{date}は休業日です。"
        
        # 日付の曜日を取得
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            weekday = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]
            formatted_date = f"{date}（{weekday}）"
        except:
            formatted_date = date
        
        description = f"{formatted_date}のシフト予定:\n\n"
        
        # 時間帯別に整理
        time_slots = {}
        for shift in shifts:
            time_slot = shift.get('time_slot', '時間未定')
            if time_slot not in time_slots:
                time_slots[time_slot] = []
            time_slots[time_slot].append(shift)
        
        # 時間順にソート
        sorted_time_slots = sorted(time_slots.items(), 
                                 key=lambda x: x[0].split('-')[0] if '-' in x[0] else x[0])
        
        for time_slot, staff_list in sorted_time_slots:
            description += f"🕐 {time_slot}:\n"
            
            # 役職別に整理
            leaders = [s for s in staff_list if 'リーダー' in s.get('role', '') or '責任者' in s.get('role', '')]
            staff = [s for s in staff_list if s not in leaders]
            
            # リーダーを先に表示
            for person in leaders + staff:
                name = person.get('name', '未定')
                role = person.get('role', 'スタッフ')
                description += f"  • {name}さん ({role})\n"
            description += "\n"
        
        # 総括と分析
        total_staff = len(shifts)
        unique_staff = len(set(shift.get('name', '') for shift in shifts))
        
        description += f"📋 勤務概要:\n"
        description += f"• 総勤務枠: {total_staff}枠\n"
        description += f"• 実働スタッフ: {unique_staff}名\n"
        
        # 負荷分析
        if unique_staff > 0:
            avg_shifts_per_person = total_staff / unique_staff
            if avg_shifts_per_person > 2:
                description += f"• 注意: 一人当たり平均{avg_shifts_per_person:.1f}枠の勤務となります\n"
        
        return description
    
    def set_personality(self, personality: str):
        """生成する文章の性格を設定"""
        if personality in ["professional", "friendly", "casual"]:
            self.personality = personality
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """生成統計を取得"""
        return {
            "total_generations": sum(self.usage_history.values()),
            "template_usage": dict(self.usage_history),
            "most_used_template": max(self.usage_history.items(), key=lambda x: x[1])[0] if self.usage_history else None,
            "personality": self.personality
        }