import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 뉴스 경제 섹션 RSS
    url = "https://news.google.com/rss/topics/CAAqIggKIhxDQklTR0dnTWF4b0pDRW5sYm5Sc1pYUmxSMEV0S0FBUAE?hl=ko&gl=KR&ceid=KR%3Ako"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 1. <item> 태그 단위로 기사들을 쪼갭니다.
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        for item in items:
            # 2. 아이템 안에서 제목(<title>)과 링크(<link>)를 찾습니다.
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                title = title_match.group(1)
                link = link_match.group(1)
                
                # 3. 불필요한 태그 제거 및 정리
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
                
                # [핵심] 필터링: 제목이 "경제"이거나 "Google 뉴스" 등 대제목이면 다음 아이템으로 패스!
                # 진짜 뉴스는 보통 최소 15자 이상입니다.
                if len(title) <= 10 or title == "경제" or "Google" in title:
                    continue 

                # 4. 언론사 이름 제거 (예: "삼성전자 주가 폭등 - 네이버 뉴스" -> "삼성전자 주가 폭등")
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0].strip()
                
                return title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 대제목 무시 및 진짜 뉴스 탐색 시작 ---")
    title, link = get_latest_news()
    
    if not title:
        print("기사 리스트에서 유효한 제목을 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"이미 전송된 뉴스입니다: {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견: {title}")
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
        print(f"네트워크 에러: {e}")

if __name__ == "__main__":
    main()
