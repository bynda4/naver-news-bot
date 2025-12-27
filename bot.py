import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

# 매체별 설정 (이름, RSS주소, 저장파일명)
NEWS_SOURCES = [
    {
        "name": "연합뉴스 속보",
        "url": "https://www.yna.co.kr/rss/news.xml",
        "db": "last_title_yna.txt"
    },
    {
        "name": "한국경제 증권",
        "url": "https://www.hankyung.com/feed/stock",
        "db": "last_title_hk.txt"
    }
]

def fetch_latest(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
        if items:
            item = items[0]
            title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL).group(1)).strip()
            link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL).group(1)).strip()
            return title, link
    except Exception as e:
        print(f"오류 발생: {e}")
    return None, None

def main():
    for source in NEWS_SOURCES:
        title, link = fetch_latest(source["url"])
        if not title: continue

        # 매체별 개별 중복 체크
        last_title = ""
        if os.path.exists(source["db"]):
            with open(source["db"], "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title == last_title:
            print(f"[{source['name']}] 새로운 뉴스가 없습니다.")
            continue

        # 전송
        message = f"📢 [{source['name']}]\n\n📌 {title}\n\n🔗 {link}"
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
            if res.status_code == 200:
                with open(source["db"], "w", encoding="utf-8") as f:
                    f.write(title)
                print(f"[{source['name']}] 전송 성공")
        except Exception as e:
            print(f"전송 에러: {e}")

if __name__ == "__main__":
    main()
