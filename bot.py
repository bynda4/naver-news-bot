import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 검색 쿼리를 더 구체화하여 잡음을 줄입니다.
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 1. <item> 태그를 먼저 추출합니다.
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        for item in items:
            # 2. 제목 추출: <title>...</title> 사이의 모든 것 (줄바꿈 포함)
            # [^<]+ 는 '<' 기호가 나오기 전까지의 모든 문자를 의미합니다.
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                title = title_match.group(1)
                link = link_match.group(1)
                
                # 3. CDATA 및 HTML 태그를 제거하고 특수문자를 복원합니다.
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title)
                title = title.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                title = title.strip()
                
                # 4. 필터링: 제목이 "네이버 경제 뉴스"이거나 "경제"이면 다음 아이템으로 넘어갑니다.
                if "Naver News" in title or title == "경제" or "네이버" in title and len(title) < 15:
                    continue
                
                # 5. 언론사 꼬리표 제거 (제목만 남김)
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0]
                
                return title, link.strip()
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 제목 추출 4차 보정 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("유효한 기사 제목을 리스트에서 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"이미 처리된 뉴스: {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 전송: {title}")
    message = f"📢 [실시간 경제 뉴스]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 완료 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"네트워크 오류: {e}")

if __name__ == "__main__":
    main()
