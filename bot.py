import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 금융 경제 속보
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    
    # [강화] 실제 브라우저와 거의 흡사한 헤더 정보
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.naver.com/',
        'Connection': 'keep-alive'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"네이버 응답 상태 코드: {resp.status_code}") # 200이 나와야 성공입니다.
        
        if resp.status_code != 200:
            return None, None

        resp.encoding = 'euc-kr' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 제목을 찾는 경로를 여러 개 준비합니다 (하나라도 걸리게)
        news_element = soup.select_one(".newsList .articleSubject a")
        if not news_element:
            news_element = soup.select_one("dt.articleSubject a")
        if not news_element:
            news_element = soup.select_one(".articleSubject a")

        if news_element:
            title = news_element.get_text(strip=True)
            link = "https://finance.naver.com" + news_element['href']
            return title, link
                
    except Exception as e:
        print(f"네이버 크롤링 중 오류: {e}")
        
    return None, None

def main():
    print("--- 네이버 뉴스 복구 및 중복 방지 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다. 네이버가 서버 접속을 차단한 것 같습니다.")
        return

    # 중복 체크 로직
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다 (전송 건너뜀): {title}")
        return

    # 전송 로직
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [네이버 증권속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 중복 방지 기록 완료 ---")
    else:
        print(f"텔레그램 전송 실패: {res.status_code}")

if __name__ == "__main__":
    main()
