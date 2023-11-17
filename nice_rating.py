# 나이스 신용평가
# 각 기업 등급 변동 내역 크롤링

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

company_list = pd.read_csv('company_list_final.csv', encoding='utf-8-sig')
company_list['종목코드'] = company_list['종목코드'].astype(str)
company_list['나이스코드'] = company_list['나이스코드'].astype(str)
company_list['종목코드']  = company_list['종목코드'].str.zfill(6)

final_df = pd.DataFrame()

for nice_code in company_list['나이스코드']:
    time.sleep(2)

    url = f'https://www.nicerating.com/disclosure/companyGradeInfo.do?cmpCd={nice_code}'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    name = soup.select_one('tbody td').text.replace('(주)', '')
    code = company_list[company_list['나이스회사명_(주)제외'] == name]['종목코드'].iloc[0]
    stock_name = company_list[company_list['나이스회사명_(주)제외'] == name]['종목명'].iloc[0]

    # 각 행을 리스트에 추가
    rows = []
    for tr in soup.select('div.tbl_type99 > table#tbl4 > tbody > tr'):
        row_data = [td.text.strip() for td in tr.select('td')]
        rows.append(row_data)


    # 데이터프레임 생성
    df = pd.DataFrame(rows)

    if tr.select_one('td.cell_not_find') == None:
        df = df.drop([3,5,6,7,8], axis=1)
        df.columns = ['평정', '등급', '전망', '등급확정일']
        
        df['등급확정일'] = pd.to_datetime(df['등급확정일'])

        df['확정연도'] = df['등급확정일'].dt.year
        df['확정분기'] = df['등급확정일'].dt.quarter
        df['회사명'] = name
        df['종목코드'] = code
        df['종목명'] = stock_name
        df['나이스코드'] = nice_code
        df = df[['종목코드', '종목명', '나이스코드', '회사명', '등급확정일', '확정연도', '확정분기', '평정', '전망', '등급']]
        df = df[df['등급']!='취소']


        # 데이터 병합
        final_df = pd.concat([final_df, df], ignore_index=True)

        # 파일 저장
        # df.to_csv(f'company_rating/rating_{name}.csv', encoding='utf-8-sig', index=False)

    else:
        # print(name, url)
        # print(tr.select_one('td.cell_not_find').text)

# 파일 저장
# final_df.to_csv('company_rating/rating_all.csv', encoding='utf-8-sig', index=False)