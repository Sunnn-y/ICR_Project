from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys  import  Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyautogui
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import math
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

usr  =  "harpny49@hufs.ac.kr"
pwd  =  "jobplanet13579"
company = '삼성물산'

driver.get("https://www.jobplanet.co.kr/users/sign_in?_nav=gb")
time.sleep(3)

# 아이디 입력
login_id = driver.find_element(By.ID, "user_email")
login_id.send_keys(usr)

# 비밀번호 입력
login_pwd = driver.find_element(By.ID, "user_password")
login_pwd.send_keys(pwd)

# 로그인 버튼 클릭
login_id.send_keys(Keys.RETURN)
time.sleep(3)

driver.find_element(By.ID, 'search_bar_search_query').send_keys(company)
time.sleep(1)
pyautogui.press('enter') # enter 치기

companies = driver.find_elements(By.CSS_SELECTOR, '.is_company_card .result_card')
print(len(companies))

for company in companies:
    title = company.find_elements(By.TAG_NAME, 'a')[-1].text                    # 기업명
    url = company.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')     # URL
    companyCode = url.split('/')[4]
    print(f'회사명: {title} 회사코드: {companyCode}')
    driver.get(url)
    time.sleep(5)
    #driver.find_element(By.CSS_SELECTOR, ".premium_modal_header .btn_close_x_ty1").click()
    driver.find_element(By.CSS_SELECTOR, "#premiumReviewChart > div > div.layer_popup_box.layer_popup_box_on > div.layer_popup.jply_modal.premium_review_inform > div > div.premium_modal_header > button").click()
    time.sleep(5)

print('실행 확인')

session = requests.session()
result = []

last_page = 212
for idx in range(1,last_page):
    url = 'url?page='+str(idx)

    res = session.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, 'html.parser')

    count3 = 0
    count4 = 0
    count5 = 0

    try:
        for k in range(5):
            reviewer_info = []
            # 응답자 정보
            position = soup.select('.content_top_ty2 > span.txt1')[0 + count4].text
            status = soup.select('.content_top_ty2 > span.txt1')[1 + count4].text
            loc = soup.select('.content_top_ty2 > span.txt1')[2 + count4].text

            day = soup.select('.content_top_ty2 > span.txt1')[3+ count4].text

            # 점
            star_rating = soup.select('.us_star_m > div.star_score')[0+k]['style'][6:-1]

            # rating 5*5
            promotion = soup.select('.bl_score')[0 + count5]['style'][6:-1]
            welfare = soup.select('.bl_score')[1 + count5]['style'][6:-1]
            balance = soup.select('.bl_score')[2 + count5]['style'][6:-1]
            culture = soup.select('.bl_score')[3 + count5]['style'][6:-1]
            top = soup.select('.bl_score')[4 + count5]['style'][6:-1]
            # 중심 제목
            content = soup.select('h2.us_label')[0+k].text
            # 장단점 경영진 의견
            merit = soup.select('dl.tc_list > dd.df1 > span')[0 + count3].text
            disadvantages = soup.select('dl.tc_list > dd.df1 > span')[1 + count3].text
            df_tit = soup.select('dl.tc_list > dd.df1 > span')[2 + count3].text


            reviewer_info = [position, status, loc, day, star_rating, promotion, welfare, balance, culture, top,clean_str(content),clean_str(merit),clean_str(disadvantages), clean_str(df_tit)]

            result.append(reviewer_info)
            reviewer_info=[]
            count3 += 3
            count4 += 4
            count5 += 5
            print("pass :"+str(idx)+"-"+str(k))
    except :
        print("fail :" + str(idx))
        pass

colname = ['직무','상황','지역','작성일','총점','승진 기회 및 가능성','복지 및 급여','업무와 삶의 균형','사내문화','경영진','총평','장점','단점','바라는점']
df = pd.DataFrame(result,columns=colname)
#저장을 희망하는 파일명으로 저장
df.to_excel("jobplanet_기업명.xlsx")


<<<<<<< HEAD:jobplanet_review.py
print(result)
=======

df = pd.read_excel('/content/jobplanet_기업명.xlsx')
>>>>>>> 0a766fa500ae12b44a4c620794824783316a9e21:jobplanet/jobplanet_review.py
