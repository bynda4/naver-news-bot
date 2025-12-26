import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 뉴스 RSS (경제 섹션) - 차단이 거의 없는 기계용 통로
    url = "https://news.naver.com/rss/sections/101"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # RSS는 XML 형식이므로 html.parser로도 충분히 읽을 수 있습니다.
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # RSS에서 개별 기사는 <item> 태그 안에 있습니다.
        item = soup.find('item')
        if item:
            # <title>과 <link> 태그를 찾습니다.
            title = item.find('title').get_text(strip=True)
            link = item.find('link').get_text(strip=True)
            return title, link
            
    except Exception as e:
        print(f"RSS 읽기 오류: {e}")
        
    return None, None

def main():
    print("--- RSS 봇 가동 시작 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다. RSS 피드 접근에 문제가 있습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [경제 뉴스 속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 기록 완료 ---")
    else:
        print(f"텔레그램 전송 실패: {res.status_code}")

if __name__ == "__main__":
    main()
