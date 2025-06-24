import google.generativeai as genai
from datetime import datetime, timedelta
import json
import re
from typing import Dict, Any
from app.utils.config import settings

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def parse_reservation_request(self, natural_language_request: str) -> Dict[str, Any]:
        prompt = f"""
        以下の自然言語による予約リクエストから、必要な情報を抽出してください。
        現在の日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        リクエスト: {natural_language_request}
        
        以下のJSON形式で返してください：
        {{
            "purpose": "利用目的",
            "start_time": "YYYY-MM-DD HH:MM",
            "end_time": "YYYY-MM-DD HH:MM",
            "server_preference": "希望するサーバー名（もしあれば）"
        }}
        
        注意事項：
        - 日付が明記されていない場合は、今日または明日を想定してください
        - 期間が明記されていない場合は、2時間を想定してください
        - 時刻は24時間形式で記載してください
        """
        
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed_data = json.loads(json_match.group())
                parsed_data["start_time"] = datetime.strptime(
                    parsed_data["start_time"], "%Y-%m-%d %H:%M"
                )
                parsed_data["end_time"] = datetime.strptime(
                    parsed_data["end_time"], "%Y-%m-%d %H:%M"
                )
                return parsed_data
            except:
                pass
        
        now = datetime.now()
        return {
            "purpose": natural_language_request,
            "start_time": now,
            "end_time": now + timedelta(hours=2),
            "server_preference": None
        }
    
    def calculate_priority(self, purpose: str, duration: float) -> int:
        prompt = f"""
        以下のGPUサーバー利用目的の優先度を0-100のスコアで評価してください。
        
        利用目的: {purpose}
        利用時間: {duration}時間
        
        評価基準：
        - 研究の重要性・緊急性
        - プロジェクトの締め切り
        - 学習やテストの必要性
        - リソースの効率的な利用
        
        スコアのみを数値で返してください。
        """
        
        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            score = int(re.search(r'\d+', score_text).group())
            return max(0, min(100, score))
        except:
            return 50
    
    def judge_conflict(self, new_reservation: Any, existing_reservation: Any) -> Dict[str, Any]:
        prompt = f"""
        2つのGPUサーバー予約が競合しています。どちらを優先すべきか判断してください。
        
        新規予約:
        - 目的: {new_reservation.purpose}
        - 優先度スコア: {new_reservation.priority_score}
        - 利用時間: {new_reservation.start_time} から {new_reservation.end_time}
        
        既存予約:
        - 目的: {existing_reservation.purpose}
        - 優先度スコア: {existing_reservation.priority_score}
        - 利用時間: {existing_reservation.start_time} から {existing_reservation.end_time}
        
        以下のJSON形式で返してください：
        {{
            "recommend_new": true/false,
            "reason": "判断理由"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "recommend_new": new_reservation.priority_score > existing_reservation.priority_score,
            "reason": "優先度スコアに基づいて判断しました"
        }