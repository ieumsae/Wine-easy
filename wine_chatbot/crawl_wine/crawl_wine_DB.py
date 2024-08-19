from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import mysql.connector
import time
import re

# MySQL 데이터베이스 연결 설정
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'wine_db'
}

# MySQL 연결
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Chrome WebDriver 설정 (경로를 자신의 webdriver 경로로 설정)
driver_path = r'C:\co\chromedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

# 페이지 범위 설정
start_index = 140000
end_index = 177533

for i in range(start_index, end_index + 1):
    print(f"현재 크롤링 중인 인덱스: {i}")  # 현재 인덱스를 출력하는 로그 추가
    url = f"https://www.wine21.com/13_search/wine_view.html?Idx={i}&lq=LIST"
    driver.get(url)
    time.sleep(1)  # 페이지 로드를 기다리기 위해 잠시 대기

    try:
        # 페이지에 데이터가 있는지 확인
        if "페이지를 찾을 수 없습니다" in driver.page_source:
            print(f"Page {i} not found.")
            continue
        
        # 각 요소를 안전하게 가져오는 함수
        def get_element_text(selector, multiple=False):
            try:
                if multiple:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    texts = [re.sub(r'\d', '', elem.text).strip() for elem in elements]
                    return ', '.join(texts) if texts else None
                else:
                    text = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    return text if text else None
            except NoSuchElementException:
                return None

        wine_name_ko = get_element_text('body > section > div.inner > div.clear > div.wine-top-right > dl > dt')
        wine_name_en = get_element_text('body > section > div.inner > div.clear > div.wine-top-right > dl > dd')
        country = get_element_text('body > section > div.inner > div.clear > div.wine-top-right > div.bagde-box > p > span:nth-child(2)')
        taste = get_element_text('#tasting > div > div.makersnote-list1 > div.board-list.board-list-makers > div > div.makers-item-tt > div')
        wine_type = get_element_text('body > section > div.inner > div.clear > div.wine-top-right > div.bagde-box > p > span:first-child')
        recommended_dish = get_element_text('body > section > div.inner > div.clear > div.wine-top-right > div.wine-top-right-inner > div:nth-child(2) > div.wine-matching-list.swiper-container.swiper-container-initialized.swiper-container-horizontal > ul li', multiple=True)

        # wine_sweet, wine_body, wine_acidity, wine_tannin 계산
        wine_sweet = len(driver.find_elements(By.CSS_SELECTOR, 'body > section > div.inner > div.clear > div.wine-top-right > div.wine-components > ul > li:nth-child(1) > div .on'))
        wine_body = len(driver.find_elements(By.CSS_SELECTOR, 'body > section > div.inner > div.clear > div.wine-top-right > div.wine-components > ul > li:nth-child(3) > div .on'))
        wine_acidity = len(driver.find_elements(By.CSS_SELECTOR, 'body > section > div.inner > div.clear > div.wine-top-right > div.wine-components > ul > li:nth-child(2) > div .on'))
        wine_tannin = len(driver.find_elements(By.CSS_SELECTOR, 'body > section > div.inner > div.clear > div.wine-top-right > div.wine-components > ul > li:nth-child(4) > div .on'))

        # ","를 제거하고 좌우 모든 값을 가져오기
        def clean_text(text):
            if text and isinstance(text, str):
                return text.replace(",", "").strip()
            return text

        wine_name_ko = clean_text(wine_name_ko)
        wine_name_en = clean_text(wine_name_en)

        # 각 요소를 출력하여 확인
        print(f"wine_name_ko: {wine_name_ko}")
        print(f"wine_name_en: {wine_name_en}")
        print(f"country: {country}")
        print(f"taste: {taste}")
        print(f"wine_type: {wine_type}")
        print(f"wine_sweet: {wine_sweet}")
        print(f"wine_body: {wine_body}")
        print(f"wine_acidity: {wine_acidity}")
        print(f"wine_tannin: {wine_tannin}")
        print(f"recommended_dish: {recommended_dish}")

        # 모든 필수 요소가 존재하는지 확인
        required_fields = [wine_name_ko, wine_name_en, wine_type, country, wine_sweet, wine_body, wine_acidity, wine_tannin, taste, recommended_dish]
        if any(field is None or (isinstance(field, str) and field.strip() == '') for field in required_fields):
            print(f"Skipping insertion for page {i} due to missing or empty data.")
            continue

        # 중복 데이터 확인
        check_query = "SELECT COUNT(*) FROM wine_detail WHERE wine_name_ko = %s AND wine_name_en = %s"
        cursor.execute(check_query, (wine_name_ko, wine_name_en))
        if cursor.fetchone()[0] > 0:
            print(f"Skipping insertion for page {i} due to duplicate data.")
            continue

        # MySQL에 데이터 추가
        columns = ["wine_name_ko", "wine_name_en", "wine_type", "country", "wine_sweet", "wine_body", "wine_acidity", "wine_tannin", "taste", "recommended_dish"]
        values = [wine_name_ko, wine_name_en, wine_type, country, wine_sweet, wine_body, wine_acidity, wine_tannin, taste, recommended_dish]

        insert_query = f"INSERT INTO wine_detail ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
        cursor.execute(insert_query, values)
        conn.commit()

    except Exception as e:
        print(f"Error on {i}: {e}")
        continue

# WebDriver 종료
driver.quit()

# MySQL 연결 종료
cursor.close()
conn.close()
