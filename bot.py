import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 RSS (네이버 경제 뉴스)
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # [핵심] <item> 태그들만 모두 찾아 리스트로 만듭니다.
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        if not items:
            print("기사 항목(item)을 찾을 수 없습니다.")
            return None, None

        # 첫 번째 기사(items[0])를 선택
        first_item = items[0]

        # 제목 추출 (<title>...</title>)
        title_match = re.search(r'<title>(.*?)</title>', first_item, re.DOTALL | re.IGNORECASE)
        title = title_match.group(1) if title_match else "제목 없음"
        
        # 링크 추출 (<link>...</link>)
        link_match = re.search(r'<link>(.*?)</link>', first_item, re.DOTALL | re.IGNORECASE)
        link = link_match.group(1) if link_match else ""
        
        # 불필요한 태그 및 CDATA 제거
        title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
        link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
        
        # 구글 뉴스 특유의 꼬리표 " - 네이버 뉴스" 제거
        title = title.split(' - ')[0]
        
        return title, link
                
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None

def main():
    print("--- 실제 기사 1순위 수집 가동 ---")
    title, link = get_latest_news()
    
    # 채널 대제목인 '경제 - Naver News'가 잡히면 무시하도록 방어
    if not title or "Naver News" in title or title == "경제":
        print(f"유효하지 않은 제목 건너뜀: {title}")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스 (전송 안 함): {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견 및 전송: {title}")
    message = f"📢 [네이버 경제 뉴스]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 중복 방지 기록 완료 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"메시지 전송 오류: {e}")

if __name__ == "__main__":
    main()
