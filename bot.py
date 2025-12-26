import requests
from bs4 import BeautifulSoup
import os

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 금융 경제 뉴스 리스트
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'euc-kr' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 방법 1: 가장 표준적인 제목 위치 (dt.articleSubject)
        news_element = soup.select_one("dl.newsList dt.articleSubject a")
        
        # 방법 2: 실패 시 (dd.articleSubject)
        if not news_element:
            news_element = soup.select_one("dl.newsList dd.articleSubject a")
            
        # 방법 3: 최후의 수단 (모든 articleSubject 클래스 내의 a 태그)
        if not news_element:
            news_element = soup.select_one(".articleSubject a")

        if news_element:
            title = news_element.get_text(strip=True)
            link = "https://finance.naver.com" + news_element['href']
            return title, link
                
    except Exception as e:
        print(f"크롤링 에러: {e}")
        
    return None, None

def main():
    print("--- 봇 작동 시작 ---")
    title, link = get_latest_news()
    
    if not title:
        # 디버깅을 위해 전체 HTML 길이를 출력해봅니다 (정상 접속 확인용)
        print("뉴스를 찾는 데 실패했습니다. HTML 구조를 확인해야 합니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 전송
    print(f"새 뉴스 전송 시도: {title}")
    message = f"📢 [증권속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 기록 완료 ---")
    else:
        print(f"전송 실패: {res.status_code}")

if __name__ == "__main__":
    main()
