import requests
from bs4 import BeautifulSoup
import time

def get_latest_news():
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 속보 리스트의 첫 번째 기사 추출 (예시 선택자)
    first_news = soup.select_one("dl.newsList dt.articleSubject a")
    title = first_news.get_text(strip=True)
    link = "https://finance.naver.com" + first_news['href']
    return title, link

def send_telegram(title, link):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    message = f"📢 [증권속보]\n{title}\n{link}"
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)

# 실제 실행 시에는 무한 루프 + time.sleep(60) 등으로 주기적 체크