"""
유틸리티 함수 모듈 - 공통 기능 제공
"""

import os
import logging
import json
from datetime import datetime
import hashlib
import re

def setup_logging(logging_config=None):
    """로깅 설정"""
    if logging_config is None:
        logging_config = {'level': 'INFO', 'file': 'news_monitor.log'}
        
    log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
    log_file = logging_config.get('file', 'news_monitor.log')
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 로깅 설정
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("로깅 시스템 초기화 완료")

def clean_text(text):
    """텍스트 정리 (HTML 태그 제거, 공백 정리 등)"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 연속 공백을 단일 공백으로 변환
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text

def truncate_text(text, max_length=100):
    """텍스트 길이 제한"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def is_valid_url(url):
    """URL 유효성 검사"""
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def generate_content_hash(content):
    """콘텐츠 해시 생성"""
    if not content:
        return ""
    
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def format_datetime(dt_string, output_format='%Y-%m-%d %H:%M'):
    """날짜시간 문자열 포맷팅"""
    try:
        # 다양한 입력 형식 시도
        input_formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z'
        ]
        
        dt = None
        for fmt in input_formats:
            try:
                dt = datetime.strptime(dt_string, fmt)
                break
            except ValueError:
                continue
        
        if dt:
            return dt.strftime(output_format)
        
        return dt_string  # 파싱 실패시 원본 반환
        
    except Exception:
        return dt_string

def save_json(data, filename, encoding='utf-8'):
    """JSON 파일 저장"""
    try:
        with open(filename, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"JSON 저장 실패 ({filename}): {e}")
        return False

def load_json(filename, default=None, encoding='utf-8'):
    """JSON 파일 로드"""
    try:
        with open(filename, 'r', encoding=encoding) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.info(f"JSON 파일이 없습니다: {filename}")
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        logging.error(f"JSON 파일 파싱 오류 ({filename}): {e}")
        return default if default is not None else {}

def ensure_directory(directory):
    """디렉토리 존재 확인 및 생성"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"디렉토리 생성: {directory}")
        return True
    except Exception as e:
        logging.error(f"디렉토리 생성 실패 ({directory}): {e}")
        return False

def get_file_size(filename):
    """파일 크기 반환 (바이트)"""
    try:
        return os.path.getsize(filename)
    except OSError:
        return 0

def format_file_size(size_bytes):
    """파일 크기를 읽기 쉬운 형식으로 변환"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names)-1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_telegram_config(bot_token, chat_id):
    """텔레그램 설정 유효성 검사"""
    if not bot_token or len(bot_token) < 10:
        return False, "봇 토큰이 유효하지 않습니다."
    
    if not chat_id:
        return False, "채팅 ID가 설정되지 않았습니다."
    
    try:
        # 채팅 ID가 숫자인지 확인 (음수 포함)
        int(chat_id)
    except ValueError:
        return False, "채팅 ID 형식이 올바르지 않습니다."
    
    return True, "설정이 유효합니다."

def save_processed_articles(articles_dict, filename="processed_articles.json"):
    """처리된 기사 정보 저장"""
    return save_json(articles_dict, filename)

def load_processed_articles(filename="processed_articles.json"):
    """처리된 기사 정보 로드"""
    return load_json(filename, default={})

def get_system_info():
    """시스템 정보 반환"""
    info = {
        'python_version': os.sys.version,
        'platform': os.name,
        'current_directory': os.getcwd(),
        'environment_variables': {
            'TELEGRAM_BOT_TOKEN': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
            'TELEGRAM_CHAT_ID': bool(os.getenv('TELEGRAM_CHAT_ID'))
        }
    }
    
    return info
