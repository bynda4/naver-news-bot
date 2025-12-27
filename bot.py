import requests
import os
import re

# 환경 변수 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('CHAT_ID')

def get_latest_news():
    # 구글 뉴스 경제 섹션 RSS
    url = "https://news.google.com/rss/topics/CAAqIggKIhxDQklTR0dnTWF4b0pDRW5sYm5Sc1pYUmxSMEV0S0FBUAE?hl=ko&gl=KR&ceid=KR%3Ako"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        content = resp.text

        # 1. <item> 태그를 모두 찾습니다.
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL | re.IGNORECASE)
        
        if not items:
            # 아이템이 없을 경우 원본 데이터 일부 출력 (디버깅용)
            print("데이터 구조 분석용 일부 출력:", content[:500])
            return None, None

        # 2. 첫 번째 아이템을 무조건 선택 (필터링 없음)
        first_item = items[0]
        
        # 3. 제목과 링크 추출
        title_match = re.search(r'<title[^>]*>(.*?)</title>', first_item, re.DOTALL | re.IGNORECASE)
        link_match = re.search(r'<link[^>]*>(.*?)</link>', first_item, re.DOTALL | re.IGNORECASE)
        
        title = title_match.group(1) if title_match else "제목 없음"
        link = link_match.group(1) if link_match else "링크 없음"

        # 기본적인 태그 정리만 수행 (CDATA 등 제거)
        title = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', title).strip()
        link = re.sub(r'<!\[CDATA\[|\]\]>|<[^>]*>', '', link).strip()
        
        return title, link
                    
    except Exception as e:
        print(f"데이터 획득 중 에러: {e}")
        
    return None, None

def main():
    print("--- 필터 무시! 무조건 전송 모드 가동 ---")
    title, link = get_latest_news()
    
    if not title:
        print("데이터를 아예 읽어오지 못했습니다.")
        return

    # [테스트용] 중복 체크를 잠시 끕니다. 실행할 때마다 메시지가 와야 정상입니다.
    # 중복 체크를 끄면 텔레그램으로 결과가 바로바로 날아옵니다.
    
    print(f"발견된 제목: {title}")
    print(f"발견된 링크: {link}")
    
    message = f"📢 [수집 데이터]\n\n제목: {title}\n\n링크: {link}"
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        res = requests.post(send_url, data={'chat_id': chat_id, 'text': message})
        if res.status_code == 200:
            print("--- 텔레그램 전송 성공 ---")
        else:
            print(f"전송 실패 상태코드: {res.status_code}")
            print(f"응답 내용: {res.text}")
    except Exception as e:
        print(f"전송 중 네트워크 에러: {e}")

if __name__ == "__main__":
    main()
