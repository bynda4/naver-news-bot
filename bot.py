import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # [변경] 가장 신뢰도 높은 연합뉴스 경제 속보 RSS
    url = "https://www.yna.co.kr/rss/economy.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 인코딩 설정 (한글 깨짐 방지)
        resp.encoding = 'utf-8'
        content = resp.text

        # 1. <item> 태그 단위로 기사 리스트 추출
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        
        for item in items:
            # 2. 제목과 링크 추출
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL)
            
            if title_match and link_match:
                # CDATA 등 불순물 제거
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title_match.group(1)).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link_match.group(1)).strip()
                
                # 'NAVER'나 '경제' 같은 짧은 노이즈가 아닌 진짜 뉴스 문장인지 확인
                if len(title) > 10:
                    return title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 연합뉴스 경제 속보 소스 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("로그: 유효한 기사를 찾지 못했습니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"로그: 이미 전송한 기사입니다. ({title[:15]}...)")
        return

    # 최종 전송
    print(f"전송 시도: {title}")
    message = f"📢 [경제 속보]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 성공! ---")
    except Exception as e:
        print(f"네트워크 오류: {e}")

if __name__ == "__main__":
    main()
