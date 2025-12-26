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
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'euc-kr' 
        
        if resp.status_code != 200:
            print(f"접속 실패 (상태코드: {resp.status_code})")
            return None, None

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # [수정] 가장 확실한 방법: 모든 링크(a) 중에서 뉴스 제목처럼 보이는 것을 순서대로 탐색
        # 네이버 금융 뉴스는 보통 newsList 클래스 안의 dt 또는 dd 태그 안에 있습니다.
        candidates = soup.select('.newsList dt a, .newsList dd a, dt.articleSubject a, .articleSubject a')
        
        for cand in candidates:
            title = cand.get_text(strip=True)
            link_href = cand.get('href', '')
            
            # 제목이 너무 짧거나(광고 등) 링크가 없으면 건너뜁니다.
            if len(title) > 5 and 'article_id' in link_href:
                full_link = "https://finance.naver.com" + link_href
                return title, full_link
                
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        
    return None, None

def main():
    print("--- 네이버 뉴스 정밀 추적 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 찾지 못했습니다. 네이버가 평소와 다른 화면을 보내준 것 같습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"이미 처리된 뉴스입니다: {title}")
        return

    # 전송
    print(f"발견된 새 뉴스: {title}")
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
