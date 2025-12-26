import requests
from bs4 import BeautifulSoup
import os

# 깃허브 Secrets 설정값 불러오기
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    # 네이버 금융 뉴스 속보 페이지 (시장지표/경제 전반)
    url = "https://finance.naver.com/news/news_list.naver?mode=LSD&section_id=101"
    
    # 네이버 차단을 피하기 위한 더 상세한 브라우저 정보 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        # 한글 깨짐 방지
        resp.encoding = 'euc-kr' 
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 네이버 금융 뉴스 리스트의 제목을 찾는 더 정확한 경로
        # 'dd.articleSubject a' 또는 'dt.articleSubject a' 둘 다 대응
        first_news = soup.select_one(".newsList .articleSubject a")
        
        if first_news:
            title = first_news.get_text(strip=True)
            link = "https://finance.naver.com" + first_news['href']
            return title, link
        else:
            # 첫 번째 선택자가 실패할 경우 대비한 보조 선택자
            fallback_news = soup.select_one("dl > dd > a")
            if fallback_news:
                title = fallback_news.get_text(strip=True)
                link = "https://finance.naver.com" + fallback_news['href']
                return title, link
                
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        
    return None, None

def send_telegram(title, link):
    if not title or not link:
        print("뉴스를 가져오지 못했습니다. 선택자를 확인해 주세요.")
        return

    message = f"📢 [증권속보]\n\n{title}\n\n링크: {link}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': message}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f"전송 성공: {title}")
    else:
        print(f"전송 실패 상태코드: {response.status_code}")
        print(f"응답 내용: {response.text}")

if __name__ == "__main__":
    t, l = get_latest_news()
    send_telegram(t, l)
