import requests
import os
import re
from urllib.parse import quote

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    keyword = quote("경제")
    url = f"https://news.google.com/rss/search?q={keyword}+site:news.naver.com&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: return None, None

        content = resp.text
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        print(f"로그: 총 {len(items)}개의 기사 후보를 분석합니다.")

        for idx, item in enumerate(items):
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title_match.group(1)).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link_match.group(1)).strip()
                
                # [제목 정밀 검증]
                # 1. 제목이 너무 짧지 않아야 함
                # 2. 제목에 'naver.com'이나 'http' 같은 주소가 포함되지 않아야 함
                if len(title) > 15 and "naver.com" not in title.lower() and "http" not in title.lower():
                    clean_title = title.split(' - ')[0].strip()
                    print(f"로그: {idx+1}번째 항목에서 진짜 기사 제목 확정! ({clean_title[:30]}...)")
                    return clean_title, link
                    
    except Exception as e:
        print(f"추출 중 오류: {e}")
        
    return None, None

def main():
    print("--- 뉴스 제목 텍스트 정밀 검증 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("로그: 모든 리스트를 검사했지만 유효한 텍스트 제목을 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"로그: 이미 전송한 기사입니다. (제목: {title[:20]}...)")
        return

    # 전송
    message = f"📢 [경제 실시간 속보]\n\n📌 {title}\n\n🔗 링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print(f"--- 전송 완료: {title[:20]}... ---")
    except Exception as e:
        print(f"전송 에러: {e}")

if __name__ == "__main__":
    main()
