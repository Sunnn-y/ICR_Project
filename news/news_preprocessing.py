###########################
# 뉴스데이터 병합 및 전처리 #
###########################

# 1. 전체 기업 뉴스 병합
import os
import pandas as pd

## 해당 디렉토리 경로에 있는 모든 파일 가져오기
directory_path = r"C:\Users\taeho\OneDrive\바탕 화면\김태호\GAHEE\ICR_project\news"
all_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]

## CSV 파일을 읽어서 리스트에 추가
dfs = []
for file_path in all_files:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    df = df.drop_duplicates('title')
    dfs.append(df)

## 데이터프레임들을 행으로 병합
merged_df = pd.concat(dfs, ignore_index=True)
merged_df = merged_df.dropna().reset_index(drop=True)

#################################################################################################################################################

# 2. 뉴스 필터링
news = merged_df.copy()
news = news[~news['title'].str.contains('별세|부고|부음|공시|헤드라인|주요 종목|코스피|코스닥|궂긴|일 알림|득점|시즌|스포츠|배구|골프|주간|종목|위클리|의 경기|vs|인사|연승|기대주')].reset_index(drop=True)

#################################################################################################################################################

# 3. 뉴스 기사 본문 전처리
## 기사 본문(content) 전처리
import re
def remove(text):
    result1 = re.sub(r'\[.*?\]','', text) # [ ] 제거
    result2 = re.sub(r'\<.*?\>','', result1) # < > 제거
    result3 = re.sub(r'[a-zA-Z0-9]+@[a-zA-Z]+(\.[a-z]{2,4}){1,2}','', result2) # 이메일 제거
    result4 = re.sub(r'[가-힣]{2,4}\s?(?:인턴)?기자','', result3) # 기자 이름 제거
    result5 = result4.replace('▶', ' ').replace('◆', ' ').replace('■', '').replace('△', '') # ▶,◆, ■ -> 띄어쓰기로 변경
    result6 = re.sub(r'네이버.*?구독하기','', result5) # 네이버에서 @@@@ 구독하기 제거
    result7 = re.sub(r'[a-z]*\.com','', result6) # 뉴스 매체 url 제거
    result8 = result7.replace('\xa0', ' ').replace('\t', '').replace('/사진제공=dl', '')
    result9 = re.sub(r'([一-鿕]|[㐀-䶵]|[豈-龎])+', '', result8) # 한자 제거
    result10 = result9.replace('현산', '현대산업개발')

    return result10

news['content_pp'] = news['content'].apply(remove)

#################################################################################################################################################

# 4. 최종 데이터
## 컬럼 생성에 필요한 병합용 테이블 준비
rating_list = pd.read_csv('df_rating.csv', encoding='utf-8-sig')
rating_list['종목코드']  = rating_list['종목코드'].astype(str).str.zfill(6)
rating_list = rating_list[['종목명', '종목코드']].drop_duplicates()

df = pd.merge(news, rating_list, left_on='company', right_on='종목명', how='left')
df['date'] = pd.to_datetime(df['date'].str.split(' ').str[0])

## 매 분기 1일을 반환해주는 함수 (날짜 생성 함수)
def quarter_start_date(date):
    quarter_month_starts = [1, 4, 7, 10]
    quarter = (date.month - 1) // 3 + 1
    quarter_start = pd.to_datetime(f"{date.year}-{quarter_month_starts[quarter - 1]:02d}-01")
    return quarter_start

## ID의 분기부분 반환 함수
def convert_to_year_quarter(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1
    return f"{year}{quarter:02d}"

## 함수 적용 및 컬럼 정리
df['date2'] = df['date'].apply(quarter_start_date)
df['quarter'] = df['date'].apply(convert_to_year_quarter)
df['ID'] = 'C' + df['종목코드'] + df['quarter']
df.columns = ['기업명', '제목', '작성날짜', '매체', '기사', 'url', '기사_전처리', '종목명', '종목코드', '날짜', '연분기', 'ID']
df = df[['ID', '기업명', '종목명', '종목코드', '작성날짜', '날짜', '연분기', '매체', '제목', '기사', '기사_전처리', 'url']]
print(df.head())

## 파일 저장
df.to_csv('news_DB_중복제거.csv', encoding='utf-8-sig', index=False)
