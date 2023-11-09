from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
import math

options = Options()
options.add_experimental_option('detach', True) # 브라우저 바로꺼짐 방지

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get('https://www.jobplanet.co.kr/users/sign_in?_nav=gb')
driver.implicitly_wait(10)

# 로그인 정보 및 검색할 회사 미리 정의
usr = "harpny49@hufs.ac.kr"
pwd = "jobplanet13579"
query = "삼성물산(주) 건설부문"

# 아이디 입력
login_id = driver.find_element(By.ID, "user_email")
login_id.send_keys(usr)

# 비밀번호 입력
login_pwd = driver.find_element(By.ID, "user_password")
login_pwd.send_keys(pwd)

# 로그인 버튼 클릭
driver.find_element(By.CSS_SELECTOR, ".btn_sign_up").click()
time.sleep(3)

# 검색창에 회사명 입력
driver.find_element(By.CSS_SELECTOR, ".input_search").click()
time.sleep(4)
driver.find_element(By.CSS_SELECTOR, ".input_search").send_keys(query)
time.sleep(4)
driver.find_element(By.CSS_SELECTOR, ".schbar_btn_search").click()
time.sleep(3)

# 회사명 클릭
driver.find_element(By.CLASS_NAME,  "tit").click()
time.sleep(5)

# 팝업창 제거
driver.find_element(By.CLASS_NAME, "btn_close_x_ty1").click()
time.sleep(3)

print(driver.find_element(By.CSS_SELECTOR, ".content_top_ty2 > span.txt1").text)
