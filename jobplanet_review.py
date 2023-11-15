import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

login_url = 'https://www.jobplanet.co.kr/users/sign_in'

email = 'email'
password = 'password'

LOGIN_INFO ={
    'user[email]' : email,
    'user[password]' : password,
    'commit' : '로그인'
}

session = requests.session()

res = session.post(login_url, data = LOGIN_INFO, verify = False)

res.raise_for_status()
result = []


def clean_str(text):
    pattern = '([ㄱ-ㅎㅏ-ㅣ]+)'  # 한글 자음, 모음 제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '<[^>]*>'         # HTML 태그 제거
    text = re.sub(pattern=pattern, repl='', string=text)
    pattern = '[^\w\s]'         # 특수기호제거
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.replace('\r','. ')
    return text


# url은 보고싶은 기업의 리뷰 URL이며 마지막은 ?page= 형태로 해야함
# last_page는 해당 기업 리뷰의 마지막 페이지 입력
last_page = 2
for idx in range(1,last_page):
    url = 'https://www.jobplanet.co.kr/companies/96621/reviews/%EC%82%BC%EC%84%B1%EB%AC%BC%EC%82%B0-%EA%B1%B4%EC%84%A4%EB%B6%80%EB%AC%B8?page='+str(idx)

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
            position = soup.select('.content_top_ty2 > span.txt1')[0 + count4].text # 직무
            status = soup.select('.content_top_ty2 > span.txt1')[1 + count4].text   # 재직 여부
            loc = soup.select('.content_top_ty2 > span.txt1')[2 + count4].text      # 지역
            date = soup.select('.content_top_ty2 > span.txt1')[3+ count4].text      # 작성일

            # 점
            star_rating = soup.select('.us_star_m > div.star_score')[0+k]['style'][6:-1] # 별점

            # rating 5*5
            promotion = soup.select('.bl_score')[0 + count5]['style'][6:-1]   # 승진 기회 및 가능성
            welfare = soup.select('.bl_score')[1 + count5]['style'][6:-1]     # 복지 및 급여
            balance = soup.select('.bl_score')[2 + count5]['style'][6:-1]     # 업무와 삶의 균형
            culture = soup.select('.bl_score')[3 + count5]['style'][6:-1]     # 사내문화
            top = soup.select('.bl_score')[4 + count5]['style'][6:-1]         # 경영진
            
            # 중심 제목
            content = soup.select('h2.us_label')[0+k].text
            
            # 장단점 경영진 의견
            merit = soup.select('dl.tc_list > dd.df1 > span')[0 + count3].text          # 장점
            disadvantages = soup.select('dl.tc_list > dd.df1 > span')[1 + count3].text  # 단점
            df_tit = soup.select('dl.tc_list > dd.df1 > span')[2 + count3].text         # 경영진에게 바라는 점


            review = [date, position, status, loc, star_rating, promotion, welfare, balance, culture, top,clean_str(content),clean_str(merit),clean_str(disadvantages), clean_str(df_tit)]

            result.append(review)
            review = []
            count3 += 3
            count4 += 4
            count5 += 5
            print("pass :"+str(idx)+"-"+str(k))
    
    except :
        print("fail :" + str(idx))
        pass

colname = ['작성일', '직무','재직 여부','지역','총점','승진 기회 및 가능성','복지 및 급여','업무와 삶의 균형','사내문화','경영진','총평','장점','단점','바라는점']
df = pd.DataFrame(result,columns=colname)

# 저장을 희망하는 파일명으로 저장
df.to_excel("jobplanet_기업명.xlsx")

print(result)


df = pd.read_excel('/content/jobplanet_기업명.xlsx')