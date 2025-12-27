import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def clean_text(text):
    """HTML 태그와 노이즈를 제거하는 함수"""
    if not text: return ""
    # CDATA 및 HTML 태그 제거
    text = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', text)
    # 특수문자 복원
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()

def get_latest_news():
    # 구글 뉴스 RSS
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # <item> 단위로 분격적 분리
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        for item in items:
            # 1. 링크 먼저 확보
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            link = clean_text(link_match.group(1)) if link_match else ""

            # 2. 제목 후보군 수집 (<title> 태그와 <description> 태그 모두 확인)
            # 간혹 <title>에는 채널명이, <description>에 진짜 제목이 들어있는 경우가 있음
            title_candidates = re.findall(r'<(title|description)[^>]*>(.*?)</\1>', item, re.DOTALL | re.IGNORECASE)
            
            best_title = ""
            for tag_name, tag_content in title_candidates:
                cleaned = clean_text(tag_content)
                # "NAVER", "Google", "경제" 등 짧은 노이즈는 무시하고 가장 긴 텍스트를 제목으로 선택
                if len(cleaned) > len(best_title):
                    best_title = cleaned

            # 3. 최종 정제 (언론사 꼬리표 제거)
            if " - " in best_title:
                best_title = best_title.rsplit(" - ", 1)[0].strip()

            # 제목이 충분히 길고 유효한 경우에만 반환
            if len(best_title) > 10 and "NAVER" not in best_title:
                return best_title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 제목 추출 최종 끝장전 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("유효한 기사를 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스: {title}")
        return

    # 텔레그램 전송
    print(f"전송 준비 완료: {title}")
    message = f"📢 [실시간 경제 뉴스]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 성공 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    main()
