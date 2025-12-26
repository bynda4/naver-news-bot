import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 뉴스를 통해 네이버 경제 뉴스를 검색하여 가져옵니다. (차단 회피용)
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 내장 파서인 html.parser를 사용하여 안전하게 읽습니다.
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # 첫 번째 기사 아이템 찾기
        item = soup.find('item')
        if item:
            title = item.title.get_text(strip=True)
            # 구글 뉴스 링크는 리다이렉트되므로 그대로 사용합니다.
            link = item.link.get_text(strip=True)
            return title, link
                
    except Exception as e:
        print(f"데이터 획득 오류: {e}")
        
    return None, None

def main():
    print("--- 안정화된 뉴스 봇 가동 (중복 방지 포함) ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다.")
        return

    # 1. 중복 체크 (이전 타이틀 불러오기)
    last_title = ""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                last_title = f.read().strip()
        except Exception:
            pass

    # 2. 동일한 제목이면 종료
    if title == last_title:
        print(f"이미 전송된 뉴스입니다: {title}")
        return

    # 3. 텔레그램 메시지 전송
    print(f"새 뉴스 전송 중: {title}")
    message = f"📢 [경제 실시간 속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            # 4. 전송 성공 시에만 파일에 제목 기록 (중복 방지용)
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 완료 ---")
        else:
            print(f"텔레그램 전송 실패: {res.status_code}")
    except Exception as e:
        print(f"네트워크 오류: {e}")

if __name__ == "__main__":
    main()
