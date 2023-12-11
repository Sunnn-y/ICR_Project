import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 필요한 기업 리스트 불러오기
company_list = pd.read_csv('company_list_final.csv', encoding='utf-8-sig')
company_list['종목코드'] = company_list['종목코드'].astype(str)
company_list['나이스코드'] = company_list['나이스코드'].astype(str)
company_list['종목코드']  = company_list['종목코드'].str.zfill(6)


# 나이스 신용등급 크롤링
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

    # 결과 확인
    if tr.select_one('td.cell_not_find') == None:
        df = df.drop([3,5,6,7,8], axis=1)
        df.columns = ['평정', '등급', '전망', '등급확정일']
        
        df['등급확정일'] = pd.to_datetime(df['등급확정일'])

        df['확정연도'] = df['등급확정일'].dt.year
        df['확정분기'] = df['등급확정일'].dt.quarter
        df['기업명'] = name
        df['종목코드'] = code
        df['종목명'] = stock_name
        df['나이스코드'] = nice_code
        df = df[['종목코드', '종목명', '나이스코드', '기업명', '등급확정일', '확정연도', '확정분기', '평정', '전망', '등급']]
        df = df[df['등급']!='취소']

        # 데이터 병합
        final_df = pd.concat([final_df, df], ignore_index=True)
        # 타입 변환
        rating_list = final_df.copy()
        to_string = ['종목코드', '나이스코드', '확정연도', '확정분기']
        rating_list[to_string] = rating_list[to_string].astype(str)

        rating_list['등급확정일'] = pd.to_datetime(rating_list['등급확정일'])

        # 종목코드 여섯글자 맞추기
        rating_list['종목코드']  = rating_list['종목코드'].str.zfill(6)
        rating_list['연도분기'] = rating_list['확정연도'] + rating_list['확정분기'].str.zfill(2)
        rating_list['연도분기'] = rating_list['연도분기'].astype(int)

        # 파일 저장
        # df.to_csv(f'company_rating/rating_{name}.csv', encoding='utf-8-sig', index=False)
        # final_df.to_csv(f'rating_all.csv', encoding='utf-8-sig', index=False)
 
    else:
        print(name, url)
        print(tr.select_one('td.cell_not_find').text)

##############################################################################

# 기업의 분기별 신용등급 테이블

cd = rating_list['종목코드'].unique().repeat(16).tolist()
nm1 = rating_list['종목명'].unique().repeat(16).tolist()
nm2 = rating_list['기업명'].unique().repeat(16).tolist()
qt = [f"{year}{month:02d}" for year in range(2020, 2024) for month in range(1, 5)] * len(rating_list['종목코드'].unique())

data = {'종목코드': cd, '종목명': nm1, '기업명': nm2, '연분기' : qt}
rating = pd.DataFrame(data)

rating['연분기'] = rating['연분기'].astype(int)

# rating 에 등급 컬럼 생성
rating['등급'] = None

for name in rating_list['종목명'].unique():
    ss = rating_list[rating_list['종목명']==name]

    for idx, row in ss[::-1].iterrows():
        qt = row['연도분기']
        value = row['등급']
        rating.loc[(rating['종목명'] == name) & (rating['연분기'] >= qt), '등급'] = value

rating = rating.dropna()
rating['연분기'] = rating['연분기'].astype(str)
rating['ID'] = 'C' + rating['종목코드']+rating['연분기']
rating = rating[['ID', '종목코드', '종목명', '기업명', '등급', '연분기']]

# 최종 파일 저장
print(rating)
# rating.to_csv('df_rating.csv', encoding='utf-8-sig', index=False)
