import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 금융 경제 속보 페이지
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 네이버 금융은 EUC-KR 인코딩을 사용하므로 반드시 설정해야 한글이 안 깨집니다.
        resp.encoding = 'euc-kr' 
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 첫 번째 뉴스 제목과 링크 찾기
        # .newsList 내부의 첫 번째 기사 제목(a 태그)을 선택합니다.
        news_element = soup.select_one(".newsList .articleSubject a")
        
        if news_element:
            title = news_element.get_text(strip=True)
            link = "https://finance.naver.com" + news_element['href']
            return title, link
        else:
            # 선택자가 안 맞을 경우를 대비한 보조 선택자
            news_element = soup.select_one("dt.articleSubject a")
            if news_element:
                title = news_element.get_text(strip=True)
                link = "https://finance.naver.com" + news_element['href']
                return title, link
                
    except Exception as e:
        print(f"네이버 크롤링 오류: {e}")
        
    return None, None

def main():
    print("--- 네이버 뉴스 복구 봇 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다. 네이버에서 접속을 차단했을 수 있습니다.")
        return

    # 1. 중복 체크 (기존 타이틀 읽기)
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 2. 제목이 같으면 전송하지 않음
    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 3. 새 뉴스 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [네이버 증권속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            # 4. 전송 성공 시에만 새 제목 저장
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 완료 ---")
        else:
            print(f"텔레그램 전송 실패: {res.status_code}")
    except Exception as e:
        print(f"텔레그램 오류: {e}")

if __name__ == "__main__":
    main()
