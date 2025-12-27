import requests
import os
import re
from urllib.parse import quote

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    # [수정] 한글 '경제'를 인터넷 주소 형식(%EA%B2%BD%EC%A0%9C)으로 안전하게 바꿉니다.
    keyword = quote("경제")
    url = f"https://news.google.com/rss/search?q={keyword}+site:news.naver.com&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 만약 또 에러가 나면 내용을 출력하게 함
        if resp.status_code != 200:
            print(f"구글 응답 에러: {resp.status_code}")
            return None, None

        content = resp.text

        # 1. <item> 태그 추출 (대소문자 무시)
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        if not items:
            # 아이템이 없을 경우 원본 데이터 일부 출력
            print("데이터 구조 분석용:", content[:300])
            return None, None

        # 2. 첫 번째 아이템 무조건 선택
        first_item = items[0]
        
        # 3. 제목과 링크 추출
        title_match = re.search(r'<title[^>]*>(.*?)</title>', first_item, re.DOTALL | re.IGNORECASE)
        link_match = re.search(r'<link[^>]*>(.*?)</link>', first_item, re.DOTALL | re.IGNORECASE)
        
        title = title_match.group(1) if title_match else "제목 없음"
        link = link_match.group(1) if link_match else "링크 없음"

        # CDATA 제거
        title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
        link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
        
        return title, link
                    
    except Exception as e:
        print(f"실행 중 에러: {e}")
        
    return None, None

def main():
    print("--- 주소 인코딩 수정 및 무조건 전송 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("최종적으로 데이터를 가져오지 못했습니다.")
        return

    print(f"발견된 제목: {title}")
    
    message = f"📢 [수집 데이터]\n\n제목: {title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            print("--- 텔레그램 전송 성공 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"전송 에러: {e}")

if __name__ == "__main__":
    main()
