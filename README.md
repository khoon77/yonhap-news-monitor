# 연합뉴스 헤드라인 모니터

연합뉴스 "이 시각 헤드라인" 기사를 시간대별로 모니터링하여 텔레그램으로 실시간 알림을 제공하는 시스템입니다.

## 🎯 주요 기능

- **시간대별 자동 모니터링** - 매 30분마다 연합뉴스 헤드라인 확인
- **텔레그램 실시간 알림** - 새로운 헤드라인을 즉시 텔레그램으로 전송
- **중복 제거** - 이미 전송된 기사는 다시 알림하지 않음
- **GitHub Actions 24/7 운영** - 컴퓨터 꺼져도 자동으로 계속 실행

## 📱 알림 형태

```
📰 日언론 "한일 정상회담 23일 전후 도쿄 개최 조율"

⏰ 08-09 10:30
📍 연합뉴스
🔗 기사 읽기
```

## 🚀 GitHub에서 사용하기

### 1단계: 파일 업로드
다음 파일들을 GitHub 저장소에 업로드하세요:

#### 📁 필수 파일들
- `yonhap_news_monitor.py` - 메인 모니터링 코드
- `yonhap_github_monitor.py` - GitHub Actions 실행 파일
- `yonhap_config.json` - 설정 파일
- `telegram_bot.py` - 텔레그램 봇 기능
- `utils.py` - 공통 유틸리티
- `requirements.txt` - Python 패키지 목록
- `.github/workflows/yonhap-news-monitor.yml` - 자동 실행 설정

### 2단계: 텔레그램 봇 설정
1. **@BotFather**에게 `/newbot` 명령으로 봇 생성
2. **봇 토큰** 받기
3. **채팅 ID** 확인 (봇에게 메시지 보낸 후 `https://api.telegram.org/bot{토큰}/getUpdates` 접속)

### 3단계: GitHub Secrets 설정
Repository Settings → Secrets and variables → Actions에서 추가:

```
TELEGRAM_BOT_TOKEN = 당신의_봇_토큰
TELEGRAM_CHAT_ID = 당신의_채팅_ID
```

### 4단계: 실행 확인
- **Actions** 탭에서 "Yonhap News Monitor" 워크플로우 확인
- **"Run workflow"** 버튼으로 수동 테스트 가능
- 매 30분마다 자동 실행됩니다

## ⚙️ 설정 옵션

`yonhap_config.json`에서 다음을 조정할 수 있습니다:

```json
{
    "monitoring": {
        "interval_minutes": 30,        // 모니터링 간격 (분)
        "max_articles_per_run": 5      // 한 번에 최대 알림 개수
    }
}
```

## 📊 실행 스케줄

```yaml
# 매 30분마다 (00분, 30분)
- cron: '0,30 * * * *'

# 다른 시간 간격 예시:
# 매 15분: '*/15 * * * *'
# 매 시간: '0 * * * *'
# 평일 9-18시만: '0 9-18 * * 1-5'
```

## 🔍 로그 확인

GitHub Actions의 로그에서 다음을 확인할 수 있습니다:
- 수집된 기사 개수
- 새로운 기사 발견 여부
- 텔레그램 전송 성공/실패
- 오류 메시지 (있는 경우)

## 🛠️ 문제 해결

### 봇이 메시지를 보내지 않는 경우
1. GitHub Secrets 설정 확인
2. 텔레그램 봇 토큰 유효성 확인
3. 채팅 ID 정확성 확인

### 기사를 수집하지 못하는 경우
- 연합뉴스 사이트 구조 변경 가능성
- GitHub Actions 로그에서 오류 메시지 확인

## 💡 추가 기능

### 키워드 필터링
특정 키워드가 포함된 기사만 알림받고 싶다면 `yonhap_config.json` 수정:

```json
{
    "keywords": {
        "include": ["정치", "경제", "사회"],
        "exclude": ["광고", "홍보"]
    }
}
```

### 시간대 제한
특정 시간에만 알림받고 싶다면 `.github/workflows/yonhap-news-monitor.yml` 수정:

```yaml
# 평일 오전 9시-오후 6시만 실행
- cron: '0,30 9-18 * * 1-5'
```

## 📈 GitHub Actions 사용량

- **무료 계정**: 월 2,000분 무료
- **30분 간격**: 월 약 1,440분 사용 (24시간 × 30일 × 2회)
- **충분한 무료 사용량**으로 24/7 운영 가능

---

**연합뉴스의 신속하고 정확한 헤드라인을 놓치지 마세요!** 📰