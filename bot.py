import requests
from bs4 import BeautifulSoup
import os

# 1. 깃허브 Secrets 설정값 불러오기
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    # 네이버 금융 '주요뉴스' 페이지 (구조가 가장 안정적입니다)
    url = "https://finance.naver.com/news/mainnews.naver"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = 'euc-kr' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 메인 뉴스 제목과 링크를 찾는 가장 확실한 경로
        # .mainNewsList 안의 첫 번째 제목을 가져옵니다.
        first_news = soup.select_one(".mainNewsList .articleSubject a")
        
        if not first_news:
            # 보조 선택자: 일반 뉴스 리스트 구조
            first_news = soup.select_one("dl.newsList dt.articleSubject a")

        if first_news:
            title = first_news.get_text(strip=True)
            link = "https://finance.naver.com" + first_news['href']
            return title, link
                
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        
    return None, None

def send_telegram(title, link):
    if not title or not link:
        print("뉴스를 가져오지 못했습니다. 선택자를 확인해 주세요.")
        return

    # 메시지 포맷 가독성 높이기
    message = f"📢 [네이버 증권 메인뉴스]\n\n제목: {title}\n\n링크 이동: {link}"
    
    # API 요청
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    response = requests.post(send_url, data=payload)
    
    if response.status_code == 200:
        print(f"전송 성공: {title}")
    else:
        print(f"전송 실패! 상태코드: {response.status_code}")
        print(f"응답내용: {response.text}")

if __name__ == "__main__":
    t, l = get_latest_news()
    send_telegram(t, l)
