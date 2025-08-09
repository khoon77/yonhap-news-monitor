#!/usr/bin/env python3
"""
연합뉴스 헤드라인 모니터 - GitHub Actions 전용
"""

import json
import os
import logging
from yonhap_news_monitor import YonhapNewsMonitor
from utils import setup_logging

def main():
    """GitHub Actions에서 실행되는 메인 함수"""
    try:
        # 로깅 설정
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("연합뉴스 헤드라인 모니터링 시작 (GitHub Actions)")
        
        # 설정 로드
        config_file = 'yonhap_config.json'
        if not os.path.exists(config_file):
            # 기본 config.json 사용
            config_file = 'config.json'
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 환경변수에서 텔레그램 설정 가져오기
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not telegram_bot_token or not telegram_chat_id:
            logger.error("텔레그램 환경변수가 설정되지 않았습니다")
            return
        
        # 환경변수로 설정 오버라이드
        config['telegram'] = {
            'bot_token': telegram_bot_token,
            'chat_id': telegram_chat_id
        }
        
        # 처리된 기사 파일명 설정
        config['storage'] = config.get('storage', {})
        config['storage']['processed_articles_file'] = 'yonhap_processed_articles.json'
        
        # 연합뉴스 모니터 초기화 및 실행
        monitor = YonhapNewsMonitor(config)
        
        # 텔레그램 봇 연결 테스트
        if monitor.telegram_bot.test_connection():
            logger.info("✅ 텔레그램 봇 연결 성공")
        else:
            logger.error("❌ 텔레그램 봇 연결 실패")
            return
        
        # 뉴스 모니터링 실행
        monitor.monitor_news()
        
        logger.info("연합뉴스 헤드라인 모니터링 완료")
        
    except Exception as e:
        logger.error(f"GitHub Actions 실행 오류: {e}")
        raise

if __name__ == "__main__":
    main()