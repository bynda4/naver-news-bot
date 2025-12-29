import requests
import os
import re

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

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

def fetch_latest(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.encoding = 'utf-8'
        
        if resp.status_code != 200:
            print(f"로그: {url} 접속 실패 (상태코드: {resp.status_code})")
            return None, None

        items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL | re.IGNORECASE)
        if items:
            item = items[0]
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title_match.group(1)).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link_match.group(1)).strip()
                return title, link
    except Exception as e:
        print(f"추출 오류 발생: {e}")
    return None, None

def main():
    for source in NEWS_SOURCES:
        print(f"로그: {source['name']} 확인 중...")
        title, link = fetch_latest(source["url"])
        
        if not title:
            print(f"로그: {source['name']}에서 기사를 가져오지 못했습니다.")
            continue

        last_title = ""
        if os.path.exists(source["db"]):
            with open(source["db"], "r", encoding="utf-8") as f:
                last_title = f.read().strip()

        if title == last_title:
            print(f"로그: {source['name']} 새로운 뉴스 없음.")
            continue

        message = f"📢 [{source['name']}]\n\n📌 {title}\n\n🔗 {link}"
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
            if res.status_code == 200:
                with open(source["db"], "w", encoding="utf-8") as f:
                    f.write(title)
                print(f"로그: {source['name']} 전송 성공!")
        except Exception as e:
            print(f"로그: {source['name']} 전송 에러: {e}")

if __name__ == "__main__":
    main()