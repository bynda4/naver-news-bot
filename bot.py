import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 모든 <item> 항목을 리스트로 추출
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        for item in items:
            # 제목과 링크 추출
            title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                raw_title = title_match.group(1)
                link = link_match.group(1)
                
                # CDATA 및 태그 제거
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', raw_title).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
                
                # ' - 네이버 뉴스' 꼬리표 제거
                title = title.split(' - ')[0]

                # [중요] 필터링: 제목이 너무 짧거나(예: '경제'), 채널명인 경우 건너뜀
                if len(title) > 10 and "Naver News" not in title:
                    return title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 뉴스 리스트 정밀 스캔 시작 ---")
    title, link = get_latest_news()
    
    if not title:
        print("유효한 기사를 리스트에서 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스 (건너뜀): {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [네이버 경제 속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 완료 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"에러: {e}")

if __name__ == "__main__":
    main()
