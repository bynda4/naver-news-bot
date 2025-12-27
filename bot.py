import requests
import os
import re
from urllib.parse import quote

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_all_news():
    keyword = quote("경제")
    url = f"https://news.google.com/rss/search?q={keyword}+site:news.naver.com&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text
        
        # 1. <item> 태그 단위로 모든 기사 덩어리를 찾습니다.
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        print(f"로그: 총 {len(items)}개의 기사를 발견했습니다.")

        results = []
        for item in items:
            # 2. 각 아이템 안에서 제목만 추출
            title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
            if title_match:
                title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title_match.group(1)).strip()
                # 꼬리표 제거
                title = title.split(' - ')[0].strip()
                results.append(title)
        
        return results
                    
    except Exception as e:
        print(f"데이터 추출 중 에러: {e}")
        return []

def main():
    print("--- 100개 기사 무조건 전수 전송 가동 ---")
    news_list = get_all_news()
    
    if not news_list:
        print("로그: 기사를 하나도 찾지 못했습니다.")
        return

    # 3. 텔레그램 전송 (너무 많으면 텔레그램에서 차단될 수 있으니 10개씩 묶어서 보냅니다)
    print(f"로그: 총 {len(news_list)}개의 제목을 전송합니다.")
    
    # 5개씩 끊어서 한 메시지에 담아 보냅니다 (도배 방지)
    for i in range(0, len(news_list), 5):
        chunk = news_list[i:i+5]
        message = "📢 [수집된 뉴스 리스트]\n\n"
        for idx, t in enumerate(chunk):
            message += f"{i + idx + 1}. {t}\n"
        
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        
    print("--- 전송 시도 완료 ---")

if __name__ == "__main__":
    main()
