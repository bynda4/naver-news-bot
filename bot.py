import requests
from bs4 import BeautifulSoup
import os

# 1. 깃허브 Secrets에 저장한 값을 환경 변수로 가져옵니다.
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 네이버 금융 뉴스 리스트에서 첫 번째 기사 추출
    first_news = soup.select_one("dl.newsList dt.articleSubject a")
    
    if first_news:
        title = first_news.get_text(strip=True)
        link = "https://finance.naver.com" + first_news['href']
        return title, link
    return None, None

def send_telegram(title, link):
    if not title or not link:
        print("뉴스를 가져오지 못했습니다.")
        return

    message = f"📢 [증권속보]\n{title}\n{link}"
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    
    response = requests.get(url)
    if response.status_code == 200:
        print(f"전송 성공: {title}")
    else:
        print(f"전송 실패: {response.status_code}")

# 2. 실제로 코드를 실행하는 부분입니다.
if __name__ == "__main__":
    t, l = get_latest_news()
    send_telegram(t, l)
