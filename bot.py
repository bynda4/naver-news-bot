import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
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
        print(f"Error: {e}")
    return None, None

def main():
    print("--- 봇 작동 시작 ---")
    title, link = get_latest_news()
    if not title:
        print("뉴스를 가져오지 못했습니다.")
        return

    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    print(f"새 뉴스 발견! 전송합니다: {title}")
    message = f"📢 [증권속보]\n\n{title}\n\n{link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        f.write(title)
    print("--- 작업 완료 ---")

# ▼ 이 부분을 아주 주의해서 봐주세요!
if __name__ == "__main__":
    main()  # <--- 반드시 앞에 스페이스 4칸 또는 Tab이 있어야 합니다!
