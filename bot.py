import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # [변경] 검색 쿼리 대신 구글 뉴스 '경제' 카테고리(Topic) 피드를 직접 사용
    # 이 피드는 기사 제목이 훨씬 깨끗하게 들어옵니다.
    url = "https://news.google.com/rss/topics/CAAqIggKIhxDQklTR0dnTWF4b0pDRW5sYm5Sc1pYUmxSMEV0S0FBUAE?hl=ko&gl=KR&ceid=KR%3Ako"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # <item> 태그 단위로 분리
        items = content.split('<item>')
        if len(items) < 2: return None, None
        
        # 첫 번째 아이템은 헤더 정보이므로 두 번째(index 1)부터 탐색
        for item in items[1:]:
            # 제목 추출: <title>과 </title> 사이 문자열 추출
            if '<title>' in item and '</title>' in item:
                title = item.split('<title>')[1].split('</title>')[0]
                # 링크 추출: <link>과 </link> 사이
                link = item.split('<link>')[1].split('</link>')[0]

                # 불순물 제거 (CDATA, 태그 등)
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
                link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
                
                # 언론사 꼬리표 제거 (뒤에서부터 ' - ' 기준 절단)
                if ' - ' in title:
                    title = title.rsplit(' - ', 1)[0]
                
                # [검증] 제목이 "경제"가 아니고 충분히 길어야 함
                if len(title) > 10 and title != "경제":
                    return title, link
                    
    except Exception as e:
        print(f"오류: {e}")
        
    return None, None

def main():
    print("--- 구글 토픽 피드 전환 및 제목 정밀 추출 ---")
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
        print(f"중복 뉴스 (전송 생략): {title}")
        return

    # 텔레그램 전송
    print(f"전송할 새 뉴스: {title}")
    message = f"📢 [실시간 경제 뉴스]\n\n📌 {title}\n\n🔗 링크: {link}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 성공 및 기록 완료 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()
