import requests
import os

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')
DB_FILE = "last_title.txt"

def get_latest_news():
    # 네이버 금융 모바일 뉴스 API (가장 안정적이고 차단이 적음)
    url = "https://m.stock.naver.com/api/news/category/mainnews?page=1&pageSize=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://m.stock.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        # JSON 데이터를 파이썬 딕셔너리로 변환
        data = resp.json()
        
        if data and len(data) > 0:
            first_news = data[0]
            title = first_news['title']
            # 뉴스 링크 생성 (언론사 코드 + 기사 코드)
            office_id = first_news['officeId']
            article_id = first_news['articleId']
            link = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
            
            return title, link
    except Exception as e:
        print(f"데이터 가져오기 오류: {e}")
        
    return None, None

def main():
    print("--- 모바일 API 봇 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("뉴스를 가져오는 데 실패했습니다. 네이버 접속 차단 가능성이 있습니다.")
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
    print(f"새 뉴스 발견: {title}")
    message = f"📢 [증권속보]\n\n{title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
    
    if res.status_code == 200:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write(title)
        print("--- 전송 및 기록 완료 ---")
    else:
        print(f"전송 실패 상태코드: {res.status_code}")

if __name__ == "__main__":
    main()
