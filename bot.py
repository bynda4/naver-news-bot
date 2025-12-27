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

        # <item> 태그 단위로 쪼개기
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        for item in items:
            # [수정] 제목 추출 방식을 더 유연하게 (태그 내부의 어떤 문자든 낚아챔)
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
            
            if title_match and link_match:
                title = title_match.group(1)
                link = link_match.group(1)
                
                # CDATA, HTML 태그, 특수문자 제거
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
                
                # ' - 네이버 뉴스' 꼬리표 및 지저분한 앞뒤 공백 제거
                title = title.split(' - ')[0].strip()

                # 제목이 제대로 추출되었고 너무 짧지 않은지 확인
                if len(title) > 5 and "Naver News" not in title and title != "경제":
                    return title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 제목 추출 정밀 보정 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("유효한 기사 제목을 찾지 못했습니다.")
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
    print(f"새 뉴스 전송 시도: {title}")
    
    # [수정] 메시지 포맷 가독성 높임
    message = f"📢 [네이버 경제 뉴스]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 성공 ---")
        else:
            print(f"전송 실패 코드: {res.status_code}")
    except Exception as e:
        print(f"네트워크 에러: {e}")

if __name__ == "__main__":
    main()
