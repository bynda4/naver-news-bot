import requests
import os
import time
import feedparser

# 스크립트 위치 기준 절대 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 환경 변수 검증
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

if not token or not chat_id:
    print("에러: TELEGRAM_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
    exit(1)

NEWS_SOURCES = [
    {
        "name": "연합뉴스 속보",
        "url": "https://www.yna.co.kr/rss/news.xml",
        "db": "last_title_yna.txt"
    },
    {
        "name": "한국경제 증권",
        "url": "https://www.hankyung.com/feed/finance", 
        "db": "last_title_hk.txt"
    },
    {
        "name": "매일경제 증권",
        "url": "https://www.mk.co.kr/rss/50200011/", 
        "db": "last_title_mk.txt"
    }
]

def fetch_latest(url, max_retries=3):
    """RSS 피드에서 최신 기사를 가져옵니다. 실패 시 재시도합니다."""
    for attempt in range(max_retries):
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"로그: {url} 파싱 실패 (시도 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue

            if feed.entries:
                entry = feed.entries[0]
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()

                if title and link:
                    return title, link

        except Exception as e:
            print(f"추출 오류 발생 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)

    return None, None

def main():
    for source in NEWS_SOURCES:
        print(f"로그: {source['name']} 확인 중...")
        title, link = fetch_latest(source["url"])

        if not title:
            print(f"로그: {source['name']}에서 기사를 가져오지 못했습니다.")
            continue

        # 절대 경로로 DB 파일 접근
        db_path = os.path.join(BASE_DIR, source["db"])

        last_title = ""
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title == last_title:
            print(f"로그: {source['name']} 새로운 뉴스 없음.")
            continue

        message = f"📢 [{source['name']}]\n\n📌 {title}\n\n🔗 {link}"
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"

        try:
            res = requests.post(send_url, data={'chat_id': chat_id, 'text': message}, timeout=10)
            if res.status_code == 200:
                with open(db_path, "w", encoding="utf-8") as f:
                    f.write(title)
                print(f"로그: {source['name']} 전송 성공!")
            else:
                print(f"로그: {source['name']} 전송 실패 (상태코드: {res.status_code}) - {res.text}")
        except Exception as e:
            print(f"로그: {source['name']} 전송 에러: {e}")

if __name__ == "__main__":
    main()