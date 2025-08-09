#!/usr/bin/env python3
"""
연합뉴스 헤드라인 모니터
시간대별 헤드라인 기사를 텔레그램으로 알림
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import trafilatura
import re
import hashlib
import os
from telegram_bot import TelegramBot
from utils import setup_logging, save_processed_articles, load_processed_articles

class YonhapNewsMonitor:
    def __init__(self, config):
        self.config = config
        self.telegram_bot = TelegramBot(config)
        self.processed_articles = load_processed_articles()
        self.logger = logging.getLogger(__name__)
        
    def get_yonhap_headlines(self):
        """연합뉴스 헤드라인 페이지에서 기사 수집"""
        try:
            url = "https://www.yna.co.kr/report/headline?site=wholemenu_headline"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            self.logger.info(f"연합뉴스 헤드라인 확인: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # 헤드라인 기사 추출
            headline_items = soup.find_all('div', class_='headline-list')
            
            if not headline_items:
                # 다른 구조 시도
                headline_items = soup.find_all('article')
                if not headline_items:
                    headline_items = soup.find_all('div', {'class': re.compile(r'.*item.*|.*news.*|.*article.*')})
            
            for item in headline_items[:10]:  # 최대 10개 기사
                try:
                    # 제목 추출
                    title_elem = item.find('a') or item.find('h2') or item.find('h3')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    # 링크 추출
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = 'https://www.yna.co.kr' + link
                    
                    # 시간 정보 추출
                    time_elem = item.find('time') or item.find('span', {'class': re.compile(r'.*time.*|.*date.*')})
                    published_time = ''
                    if time_elem:
                        published_time = time_elem.get_text(strip=True)
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'link': link,
                            'published_time': published_time,
                            'source': '연합뉴스'
                        })
                        
                except Exception as e:
                    self.logger.warning(f"기사 파싱 오류: {e}")
                    continue
            
            # 일반 텍스트에서 기사 추출 (fallback)
            if not articles:
                text_content = trafilatura.extract(response.content)
                if text_content:
                    lines = text_content.split('\n')
                    current_title = None
                    current_link = None
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # 헤드라인 패턴 찾기
                        if '[연합뉴스 이 시각 헤드라인]' in line or '■' in line:
                            if current_title and current_link:
                                articles.append({
                                    'title': current_title,
                                    'link': current_link,
                                    'published_time': '',
                                    'source': '연합뉴스'
                                })
                            current_title = line.replace('■', '').strip()
                            current_link = None
                            
                        elif line.startswith('전문보기:') or line.startswith('https://'):
                            current_link = line.replace('전문보기:', '').strip()
                            
                        elif '시각' in line and ':' in line:
                            # 시간 정보
                            pass
            
            self.logger.info(f"연합뉴스에서 {len(articles)}개 기사 수집")
            return articles
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"연합뉴스 스크래핑 오류: {e}")
            return []
        except Exception as e:
            self.logger.error(f"연합뉴스 처리 중 오류: {e}")
            return []
    
    def generate_article_hash(self, article):
        """기사 해시 생성"""
        content = f"{article['title']}{article['link']}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_processed(self, article_hash):
        """이미 처리된 기사인지 확인"""
        return article_hash in self.processed_articles
    
    def filter_new_articles(self, articles):
        """새로운 기사만 필터링"""
        new_articles = []
        for article in articles:
            article_hash = self.generate_article_hash(article)
            if not self.is_processed(article_hash):
                new_articles.append(article)
                self.processed_articles[article_hash] = {
                    'title': article['title'],
                    'processed_at': datetime.now().isoformat(),
                    'source': article['source']
                }
        return new_articles
    
    def send_article_notification(self, article):
        """개별 기사 텔레그램 알림 전송"""
        try:
            # 메시지 포맷 (심플하게)
            message = f"📰 <b>{article['title']}</b>\n\n"
            
            if article.get('published_time'):
                message += f"⏰ {article['published_time']}\n"
            
            message += f"📍 {article['source']}\n"
            message += f"🔗 <a href='{article['link']}'>기사 읽기</a>"
            
            return self.telegram_bot.send_message(message)
            
        except Exception as e:
            self.logger.error(f"텔레그램 알림 전송 오류: {e}")
            return False
    
    def monitor_news(self):
        """뉴스 모니터링 실행"""
        try:
            self.logger.info("연합뉴스 헤드라인 모니터링 시작...")
            
            # 연합뉴스 헤드라인 수집
            articles = self.get_yonhap_headlines()
            
            if not articles:
                self.logger.info("수집된 기사가 없습니다.")
                return
            
            # 새로운 기사 필터링
            new_articles = self.filter_new_articles(articles)
            
            if not new_articles:
                self.logger.info("새로운 기사가 없습니다.")
                return
            
            self.logger.info(f"새로운 기사 {len(new_articles)}개 발견")
            
            # 최대 5개까지만 알림 (스팸 방지)
            max_articles = min(len(new_articles), self.config.get('max_articles_per_run', 5))
            successful_notifications = 0
            
            for article in new_articles[:max_articles]:
                if self.send_article_notification(article):
                    successful_notifications += 1
                    time.sleep(2)  # 2초 간격으로 전송
                else:
                    break
            
            self.logger.info(f"텔레그램 알림 전송 완료: {successful_notifications}/{max_articles}개 성공")
            
            # 처리된 기사 정보 저장
            save_processed_articles(self.processed_articles)
            
            self.logger.info(f"{len(new_articles)}개 기사 처리 완료")
            
        except Exception as e:
            self.logger.error(f"뉴스 모니터링 오류: {e}")

def main():
    """메인 함수"""
    try:
        # 로깅 설정
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # 설정 로드
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 연합뉴스 모니터 초기화
        monitor = YonhapNewsMonitor(config)
        
        # 텔레그램 봇 연결 테스트
        if monitor.telegram_bot.test_connection():
            logger.info("✅ 텔레그램 봇 연결 성공")
            monitor.telegram_bot.send_message("📰 연합뉴스 헤드라인 모니터링을 시작합니다.")
        else:
            logger.error("❌ 텔레그램 봇 연결 실패")
            return
        
        # 단일 실행 (GitHub Actions용)
        monitor.monitor_news()
        
    except Exception as e:
        logger.error(f"프로그램 실행 오류: {e}")

if __name__ == "__main__":
    main()