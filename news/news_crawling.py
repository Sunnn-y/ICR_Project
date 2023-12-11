import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# 개별 뉴스 크롤링
def get_news(URL) :
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    date = ""
    media = ""
    content = ""

    if soup.select_one('h2#title_area') != None:
        title = soup.select_one("h2#title_area").text #제목
        date = soup.select_one("span.media_end_head_info_datestamp_time").text #기사작성일시
        media = soup.select_one("a.media_end_head_top_logo img")['title'] #매체명 (예.한국경제)
        content = soup.select_one("div#newsct_article").text.replace("\n","").replace('\t', '') #기사원문
    elif soup.select_one('h4.title') != None:
        title = soup.select_one('h4.title').text #제목
        date = soup.select_one("div.info > span").text.replace('기사입력 ', '') #기사작성일시
        media = soup.select_one("a.link > img")['alt']#매체명 (예.한국경제)
        content = soup.select_one("div#newsEndContents").text.replace('\n', '') #기사원문
    elif soup.select_one('h2.end_tit') != None:
        title = soup.select_one("h2.end_tit").text.replace('\t', '').replace('\n', '') #제목
        date = soup.select_one("span.author em").text #기사작성일시
        media = soup.select_one("a img")['alt'] #매체명 (예.한국경제)
        content = soup.select_one("div#articeBody").text.replace('\n', '') #기사원문

    return (title, date, media, content, URL)


# 키워드, 기간 입력받아서 크롤링
def get_news_list(keyword, startdate, enddate, sleep_time=1) :
    li = []
    h = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
         'Referer' : 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query=%22%EC%82%BC%EC%84%B1%EB%AC%BC%EC%82%B0+%EB%8C%80%ED%91%9C%22&oquery=%EC%82%BC%EC%84%B1%EB%AC%BC%EC%82%B0|%EB%8C%80%ED%91%9C&tqi=iRoHnlqo1SCssnN21Ndssssst1R-489512',
         'cookie':'NNB=P5AEYQTCF36WI; nid_inf=-1557441483; NID_AUT=Z+rs7GSn4oPM1wy3zzzmba5/7N6EH6pfHntsX3kB0O0QU1mfWMgk44i30TnI3J7V; NID_JKL=f0HWg69Tr5hTkuwYiuAJksh4lYiMfusSsrn3BRObu8o=; nx_ssl=2; NID_SES=AAABnfg9qUe9oa21oCbJL46dVoxEy+D+Ixl6l0jFWOZlNw0ObyFav7NMvBr0FgDL3Xju9eiBgEhqOjytDG+mpuKgso8p6C2ogTnnol6j0uA7tuD2ijKVcgzwVUaBdkmk/MzF58LAIy7o1wzurcki3r9UP8r3x+UxZYXumhYykqVdlfwYpO34ymkleNsC12mkZG4yP3UPFBYej37fIWDuGIXriZbPFJJ0Bseh0EW+bPYtlnwKdiW8tGs/EbvCvE3O+GDVEzrQidSzWCsCptI/lFPD1t4DKOSFp8Q+gdmzgRr8518GV4wbKRiAYQJ/ownKkPZ2/JKuOSU8Ye9mAekFmK8GltjurlFDSAJrqlULXYzvfps+IgNd9DaaCxdGU1XsZeOMWIjXVxvvSreVvcaSX2/IzDDruJigc+6P65yQQPg441vcIJ83FY/5lhswuExCirV50mlqUx+lo1EaYy25P1cG4mlfmMiYDOvnYjtJyH1zgbo0ODhpl2fN7GyWWFhs/72Y6VtlserIl/zzdUrfuHRYn8Wdy3m/iHAzUyZvCgJf3iTh; _naver_usersession_=ToXtfjDjM1XUMlD0lI1Hx9Iw; page_uid=iRoHkdqo1LVssOtENEKssssstHN-364466; N_SES=28b1cc29-16e3-4daa-848c-5a9a597385fb; VISIT_LOG_CLEAN=1'
         }
         
    for d in pd.date_range(startdate, enddate) :
        str_d = d.strftime("%Y.%m.%d")
        page = 1
        print(str_d)

        while True:
            start = (page-1)*10 + 1
            print(page)
            URL = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query={0}&sort=0&photo=0&field=0&pd=3&ds={1}&de={2}&cluster_rank=42&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:r,p:from{3}to{4},a:all&start={5}".format(keyword, str_d, str_d, str_d.replace(".",""), str_d.replace(".",""), start)
            response = requests.get(URL, headers=h)
            soup = BeautifulSoup(response.text, "html.parser")

            if soup.select_one(".api_noresult_wrap") :
                break

            news_list = soup.select("ul.list_news li")

            for item in news_list :
                if len(item.select("div.info_group a")) == 2 :
                    li.append(get_news(item.select("div.info_group a")[1]['href']))
                    
            page = page + 1
            time.sleep(random.uniform(2,5))

    return pd.DataFrame(li, columns=['title','date','media','content','url'])
