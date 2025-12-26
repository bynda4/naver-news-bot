import requests
from bs4 import BeautifulSoup
import os

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'euc-kr' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        first_news = soup.select_one(".newsList .articleSubject a")
        
        if first_news:
            return first_news.get_text(strip=True), "https://finance.naver.com" + first_news['href']
    except Exception as e:
        print(f"크롤링 오류: {e}")
    return None, None

def send_telegram(title, link):
    # 1. 이전 뉴스 제목 읽기
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 2. 중복 확인
    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return False # 전송 안 함

    # 3. 텔레그램 전송
    message = f"📢 [증권속보]\n\n{title}\n\n{link}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': message})
    
    # 4. 새로운 제목 저장
    with open(DB_FILE, "w", encoding="utf-8") as f:
        f.write(title)
    return True

if __name__ == "__main__":
    t, l = get_latest_news()
    if t:
        send_telegram(t, l)
