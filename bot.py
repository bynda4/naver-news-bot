import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 뉴스 RSS (네이버 경제 속보를 더 정확하게 타겟팅)
    url = "https://news.google.com/rss/search?q=site:news.naver.com+경제&hl=ko&gl=KR&ceid=KR:ko"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 1. <item> 또는 <ITEM>을 대소문자 구분 없이 찾습니다.
        # re.IGNORECASE를 사용하여 어떤 형식이든 대응합니다.
        items = re.findall(r'<(item|ITEM)>(.*?)</\1>', content, re.DOTALL | re.IGNORECASE)
        
        if items:
            # 첫 번째 아이템의 내용 부분만 추출
            first_item_content = items[0][1]
            
            # 2. 제목 추출: <title>과 </title> 사이 (대소문자 무시)
            title_match = re.search(r'<(title|TITLE)>(.*?)</\1>', first_item_content, re.DOTALL | re.IGNORECASE)
            title = title_match.group(2) if title_match else ""
            
            # 3. 링크 추출: <link>과 </link> 사이 (대소문자 무시)
            link_match = re.search(r'<(link|LINK)>(.*?)</\1>', first_item_content, re.DOTALL | re.IGNORECASE)
            link = link_match.group(2) if link_match else ""
            
            # 불필요한 CDATA 및 HTML 엔티티 제거
            title = re.sub(r'<!\[CDATA\[|\]\]>', '', title).strip()
            link = re.sub(r'<!\[CDATA\[|\]\]>', '', link).strip()
            
            # 꼬리표( - 네이버 뉴스) 제거 및 특수문자 변환
            title = title.split(' - ')[0]
            title = title.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            return title, link
                
    except Exception as e:
        print(f"추출 과정 오류: {e}")
        
    return None, None

def main():
    print("--- 초정밀 뉴스 데이터 추출 시작 ---")
    title, link = get_latest_news()
    
    # "경제 - Naver News" 같은 채널 제목이 혹시라도 다시 잡히지 않도록 이중 방어
    if not title or len(title) < 5 or "Google" in title:
        print("유효한 기사 제목을 찾지 못했습니다. RSS 소스를 다시 확인 중입니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"이미 전송한 뉴스: {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 전송 시도: {title}")
    message = f"📢 [네이버 경제 속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 완료 ---")
        else:
            print(f"전송 실패 코드: {res.status_code}")
    except Exception as e:
        print(f"전송 중 네트워크 에러: {e}")

if __name__ == "__main__":
    main()
