import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 구글 뉴스 RSS (대한민국 경제 섹션)
    url = "https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR290T1RWakVnSnNrYzhvQUFQAQ?hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text
        
        # 1. 첫 번째 기사 위치 찾기 (<item> 태그 이후부터 찾기)
        # RSS 제목(구글 뉴스)을 건너뛰기 위해 첫 번째 <item>을 찾습니다.
        start_idx = content.find('<item>')
        if start_idx == -1:
            print("RSS 데이터를 읽었으나 기사(item)가 없습니다.")
            return None, None
            
        first_item = content[start_idx:]
        
        # 2. 제목(title) 추출: <title>과 </title> 사이 글자 낚기
        title_start = first_item.find('<title>') + 7
        title_end = first_item.find('</title>')
        title = first_item[title_start:title_end]
        
        # 3. 링크(link) 추출: <link>과 </link> 사이 글자 낚기
        link_start = first_item.find('<link>') + 6
        link_end = first_item.find('</link>')
        link = first_item[link_start:link_end]
        
        # HTML 특수문자 제거 (예: &quot; -> ")
        title = re.sub(r'&[^;]+;', '', title)
        
        return title.strip(), link.strip()
            
    except Exception as e:
        print(f"데이터 추출 중 오류: {e}")
        
    return None, None

def main():
    print("--- 초강력 문자열 파싱 봇 가동 ---")
    title, link = get_latest_news()
    
    if not title or len(title) < 2:
        print("뉴스를 가져오는 데 실패했습니다. 응답 내용을 확인해야 합니다.")
        return

    # 중복 체크
    last_title = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title == last_title:
        print(f"중복 뉴스입니다: {title}")
        return

    # 텔레그램 전송
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [실시간 경제 뉴스]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(title)
            print("--- 전송 및 기록 완료 ---")
        else:
            print(f"전송 실패: {res.status_code}")
    except Exception as e:
        print(f"텔레그램 오류: {e}")

if __name__ == "__main__":
    main()
