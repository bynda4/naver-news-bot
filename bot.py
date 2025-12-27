import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 뉴스 RSS (네이버 경제)
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 1. <item> 태그가 시작되는 지점을 찾습니다. (대소문자 무시)
        # 굳이 정규표현식을 쓰지 않고 가장 원시적인 방법으로 접근합니다.
        lower_content = content.lower()
        start_pos = lower_content.find('<item>')
        
        if start_pos == -1:
            print("전체 응답 내용 데이터 일부 출력:", content[:300]) # 진단을 위해 데이터 일부 출력
            return None, None
            
        # 첫 번째 <item> 내용만 추출
        end_pos = lower_content.find('</item>', start_pos)
        first_item = content[start_pos:end_pos+7]

        # 2. 제목(title) 추출 - 필터링 없이 <a> 태그나 CDATA 등 모두 포함해서 일단 긁음
        title = re.search(r'<(title|TITLE)>(.*?)</\1>', first_item, re.S | re.I).group(2)
        
        # 3. 링크(link) 추출
        link = re.search(r'<(link|LINK)>(.*?)</\1>', first_item, re.S | re.I).group(2)
        
        # 최소한의 정돈 (HTML 태그 및 CDATA 제거)
        title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
        link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
        
        return title, link
                
    except Exception as e:
        print(f"데이터 파싱 중 에러: {e}")
        
    return None, None

def main():
    print("--- 필터 해제: 무조건 수집 모드 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("여전히 데이터를 찾지 못했습니다. 소스 코드 구조가 예상과 완전히 다릅니다.")
        return

    # 중복 체크 (이것마저 방해된다면 나중에 제거 가능합니다)
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스 (전송 안 함): {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [실시간 뉴스]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 완료 ---")
    else:
        print(f"전송 실패: {res.status_code}")

if __name__ == "__main__":
    main()
