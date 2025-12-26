import requests
from bs4 import BeautifulSoup
import os

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 금융 경제 뉴스 전체 리스트
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'euc-kr' # 네이버 금융은 euc-kr을 사용합니다.
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # [수정] 네이버 금융 속보의 제목을 찾는 가장 정확한 경로
        # 보통 dl.newsList 아래 dt.articleSubject 또는 dd.articleSubject에 제목이 있습니다.
        news_element = soup.select_one(".newsList .articleSubject a")
        
        if not news_element:
            # 보조 수단: 좀 더 넓은 범위에서 찾아보기
            news_element = soup.select_one("dt.articleSubject a")

        if news_element:
            title = news_element.get_text(strip=True)
            link = "https://finance.naver.com" + news_element['href']
            return title, link
                
    except Exception as e:
        print(f"크롤링 에러 발생: {e}")
        
    return None, None

def main():
    print("--- 봇 작동 시작 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오지 못했습니다. (선택자 불일치 가능성)")
        return

    # 중복 체크 로직
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 메시지 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [실시간 증권속보]\n\n{title}\n\n{link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 텔레그램 전송 및 기록 완료 ---")
        else:
            print(f"텔레그램 전송 실패: {res.status_code}")
    except Exception as e:
        print(f"전송 중 에러: {e}")

if __name__ == "__main__":
    main()
