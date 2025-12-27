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

        # [핵심 수정] 첫 번째 <item> 태그의 위치를 찾습니다. 
        # <item> 이전의 <title>은 전체 채널의 제목이므로 무시해야 합니다.
        item_start = content.find('<item>')
        if item_start == -1:
            return None, None
            
        # 첫 번째 기사 내용만 잘라내기
        first_item = content[item_start:]

        # 제목 추출: <title>과 </title> 사이
        title_match = re.search(r'<title>(.*?)</title>', first_item)
        title = title_match.group(1) if title_match else ""
        
        # 링크 추출: <link>과 </link> 사이
        link_match = re.search(r'<link>(.*?)</link>', first_item)
        link = link_match.group(1) if link_match else ""
        
        # 기사 제목에서 구글 뉴스가 붙이는 언론사 꼬리표( - 네이버 뉴스) 제거
        title = title.split(' - ')[0]
        
        # 특수 문자 및 CDATA 처리
        title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
        link = link.replace('<![CDATA[', '').replace(']]>', '').strip()
        
        return title, link
                
    except Exception as e:
        print(f"추출 오류: {e}")
        
    return None, None

def main():
    print("--- 실제 기사 추출 모드 가동 ---")
    title, link = get_latest_news()
    
    # 제목이 전체 채널명과 같거나 비어있으면 전송 취소
    if not title or "Google 뉴스" in title or title == "경제":
        print("유효한 기사 제목을 찾지 못했습니다.")
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
    print(f"새 뉴스 전송: {title}")
    message = f"📢 [실시간 경제속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 기록 완료 ---")
    else:
        print(f"전송 실패: {res.status_code}")

if __name__ == "__main__":
    main()
