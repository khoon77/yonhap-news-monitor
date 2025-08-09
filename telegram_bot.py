"""
텔레그램 봇 모듈 - 텔레그램을 통한 알림 전송
"""

import logging
import requests
import time
from urllib.parse import quote

class TelegramBot:
    def __init__(self, config):
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def test_connection(self):
        """텔레그램 봇 연결 테스트"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    logging.info(f"텔레그램 봇 연결 성공: {bot_info.get('username', 'Unknown')}")
                    return True
            
            logging.error(f"텔레그램 봇 연결 실패: {response.text}")
            return False
            
        except Exception as e:
            logging.error(f"텔레그램 봇 연결 테스트 오류: {e}")
            return False
    
    def send_message(self, message, parse_mode='HTML'):
        """텔레그램 메시지 전송"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            # 메시지 길이 제한 (4096자)
            if len(message) > 4090:
                message = message[:4090] + "..."
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    logging.info("텔레그램 메시지 전송 성공")
                    return True
                else:
                    logging.error(f"텔레그램 메시지 전송 실패: {data.get('description', 'Unknown error')}")
            else:
                logging.error(f"텔레그램 API 오류: {response.status_code} - {response.text}")
                
            return False
            
        except Exception as e:
            logging.error(f"텔레그램 메시지 전송 오류: {e}")
            return False
    
    def format_article(self, article):
        """기사 정보를 텔레그램 메시지 형식으로 변환 (간단 버전)"""
        title = article.get('title', 'No Title')
        url = article.get('url', '')
        source = article.get('source', 'Unknown Source')
        
        # HTML 특수문자 이스케이프
        title = self.escape_html(title)
        source = self.escape_html(source)
        
        # 간단한 형식: 제목과 링크만
        message = f"📰 <b>{title}</b>\n"
        message += f"🌐 {source}\n"
        message += f"🔗 <a href='{url}'>기사 읽기</a>"
        
        return message
    
    def escape_html(self, text):
        """HTML 특수문자 이스케이프"""
        if not text:
            return ""
        
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        
        return text
    
    def send_news_notification(self, articles):
        """뉴스 기사들을 텔레그램으로 전송 (간단 형식)"""
        if not articles:
            return True
        
        try:
            success_count = 0
            
            # 헤더 메시지 (한 번만 전송)
            header = f"🚨 <b>새로운 비트코인 뉴스 {len(articles)}개 발견!</b>\n\n"
            
            # 모든 기사를 하나의 메시지로 합치기
            full_message = header
            for i, article in enumerate(articles, 1):
                full_message += f"<b>{i}.</b> " + self.format_article(article) + "\n\n"
            
            # 메시지 길이가 너무 길면 분할 전송
            if len(full_message) > 4000:
                # 각 기사를 개별 메시지로 전송
                self.send_message(header)
                time.sleep(1)
                
                for i, article in enumerate(articles, 1):
                    try:
                        message = f"<b>{i}.</b> " + self.format_article(article)
                        if self.send_message(message):
                            success_count += 1
                        time.sleep(1)
                    except Exception as e:
                        logging.error(f"기사 전송 오류 ({i}번째): {e}")
            else:
                # 한 번에 전송
                if self.send_message(full_message):
                    success_count = len(articles)
            
            logging.info(f"텔레그램 알림 전송 완료: {success_count}/{len(articles)}개 성공")
            return success_count > 0
            
        except Exception as e:
            logging.error(f"뉴스 알림 전송 오류: {e}")
            return False
