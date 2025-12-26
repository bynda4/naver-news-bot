import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # [변경] PC 금융 페이지 대신 모바일 뉴스 경제 속보를 사용합니다.
    # 이 경로는 봇 차단이 현저히 적습니다.
    url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=101"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-kr',
        'Referer': 'https://m.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8' # 일반 뉴스는 utf-8을 사용합니다.
        
        if resp.status_code != 200:
            print(f"접속 실패: {resp.status_code}")
            return None, None

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 뉴스 목록에서 첫 번째 기사 찾기 (일반 뉴스 섹션 구조)
        # 1순위: 포토가 있는 뉴스, 2순위: 포토 없는 뉴스
        post = soup.select_one("ul.type06_headline li dl dt:not(.photo) a")
        if not post:
            post = soup.select_one("ul.type06 li dl dt:not(.photo) a")
            
        if post:
            title = post.get_text(strip=True)
            link = post['href']
            return title, link
                
    except Exception as e:
        print(f"오류 발생: {e}")
        
    return None, None

def main():
    print("--- 네이버 모바일 우회 모드 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("모바일 경로로도 뉴스 추출에 실패했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"이미 확인한 뉴스입니다: {title}")
        return

    # 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [경제 속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 기록 완료 ---")
    else:
        print(f"텔레그램 전송 실패")

if __name__ == "__main__":
    main()
