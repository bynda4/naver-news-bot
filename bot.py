import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 확인
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

# 파일 경로를 절대 경로로 설정 (중요)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "last_title.txt")

def get_latest_news():
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'euc-kr' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 뉴스 제목 선택자 보강
        first_news = soup.select_one(".newsList .articleSubject a")
        if not first_news:
            first_news = soup.select_one("dt.articleSubject a")
        
        if first_news:
            return first_news.get_text(strip=True), "https://finance.naver.com" + first_news['href']
    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")
    return None, None

def main():
    print("봇 실행을 시작합니다...")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다.")
        return

    # 이전 뉴스 읽기
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()
            print(f"이전 뉴스 제목: {last_title}")

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 메시지 전송
    print(f"새 뉴스 발견! 전송 중: {title}")
    message = f"📢 [증권속보]\n\n{title}\n\n{link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("기록 완료.")
    else:
        print(f"전송 실패: {res.status_code}, {res.text}")

# 이 부분이 맨 왼쪽에 붙어 있어야 합니다 (들여쓰기 금지)
if __name__ == "__main__":
main()
