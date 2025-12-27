import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    # 연합뉴스 경제 속보 RSS
    url = "https://www.yna.co.kr/rss/economy.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8' # 한글 깨짐 방지
        content = resp.text

        # <item> 태그 단위로 기사 리스트 추출
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        
        if items:
            # 첫 번째 아이템(가장 최신 뉴스) 추출
            item = items[0]
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL)
            link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL)
            
            if title_match and link_match:
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title_match.group(1)).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link_match.group(1)).strip()
                return title, link
                    
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 중복 체크 없이 무조건 전송 모드 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("로그: 전송할 기사를 찾지 못했습니다.")
        return

    # [수정] 중복 체크 로직을 완전히 삭제했습니다.
    # 실행 시마다 무조건 메시지를 보냅니다.
    
    print(f"전송 시도: {title}")
    message = f"📢 [경제 속보]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            print("--- 텔레그램 전송 성공! ---")
        else:
            print(f"전송 실패 상태코드: {res.status_code}")
    except Exception as e:
        print(f"네트워크 오류: {e}")

if __name__ == "__main__":
    main()
