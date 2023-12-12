### 기존 3년치 파일에서 필요없는 비율 삭제

import pandas as pd

df = pd.read_csv('건설업계_재무비율_신용등급_merge.csv')

df = df.drop(['차입금의존도', '고정장기적합률', '매출액경상이익률', '매출액 증가율', '영업이익 증가율', '매출채권 회전기일(일)', '재고자산 회전기일(일)', '부채상환계수(배)', '총차입금상환능력비율',
              '종목코드', '종목명', '회사명', '연분기'], axis=1)
# print(df)

df.to_csv('건설업계_재무비율_최종_신용등급_merge.csv')



### 건설업계 백테스트 데이터 수집

import math
import OpenDartReader

my_api = "e9239b06215e8ff1addd0cc65d1b144a10af6d57"
dart = OpenDartReader(my_api)

corp_name = ['DL이앤씨', 'HDC현대산업개발', '한전KPS', 'HJ중공업', '신세계건설', 'KCC건설', '대우건설', '서희건설', '특수건설', '계룡건설산업', '신원종합개발',
             '서한', '태영건설', '현대건설', 'GS건설', '동부건설', '코오롱글로벌', 'DL건설', '진흥기업', '남광토건', '한신공영', '금호건설', '삼부토건']
corp_code = ['375500', '294870', '051600', '097230', '034300', '021320', '047040', '035890', '026150', '013580', '017000',
             '011370', '009410', '000720', '006360', '005960', '003070', '001880', '002780', '001260', '004960', '002990', '001470']
report_code = ["11013", "11012", "11014"] # '11013'=1분기보고서, '11012'=반기보고서, '11014'=3분기보고서, '11011'=사업보고서

corp_name_p = corp_name[22]
corp_code_p = corp_code[22]

all = pd.DataFrame()

for year in range(2022, 2024):
  for code in report_code:
    corp = dart.finstate_all(corp_code_p, year, code, fs_div="OFS")
    # corp = corp.drop('account_id', axis=1)
    all = pd.concat([all, corp], ignore_index=True) # 2019년~2022년 별도 재무제표 전문(분기보고서+반기보고서+사업보고서)

# print(all)

Quarter = [] # 분기
cor_year = [] # 연도
ID_list = [] # 기업코드
corp_name_list = [] # 기업명
year_list = [] # 수집 연도
report_code_list = [] # 보고서 종류
Debt_Ratio = [] # 부채비율
Return_on_Equity = [] # 자기자본순이익률
Operating_Profit_Margin = [] # 매출액영업이익률
Interest_Coverage_Ratio =[] # 이자보상배율(배)
Total_Asset_Growth_Rate = [] # 총자산 증가율
Equity_Growth_Rate= [] # 자기자본 증가율
Accounts_Payable_Turnover = [] # 매입채무회전기일(일)
Total_Asset_Turnover_Ratio = [] # 총자산 회전율

year = 2023
str_year = str(year)
report_code_list.extend(['1분기보고서' if code == '11013' else '반기보고서' if code == '11012' else '사업보고서' for code in report_code])
Quarter.extend(['01' if code == '11013' else '02' if code == '11012' else '03' if code == '11014' else '04' for code in report_code])
for code in report_code:
  BS1 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and (row['account_nm'] == '자산총계' or row['account_nm'] == '자산 총계') and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 자산총계
  BS2 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and (row['account_nm'] == '부채총계' or row['account_nm'] == '부채 총계') and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 부채총계
  BS3 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and (row['account_nm'] == '자본총계' or row['account_nm'] == '자본 총계' or '기말자본' in row['account_nm'] or '기말 자본' in row['account_nm']) and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 자본총계
  BS10 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '자산총계' and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 자산총계
  BS12 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and (row['account_nm'] == '자본총계'  or '기말자본' in row['account_nm'] or '기말 자본' in row['account_nm']) and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 자본총계
  BS14 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and '매입채무' in row['account_nm'] and '장기' not in row['account_nm'] and '비유동' not in row['account_nm'] and 'LongTerm' not in row['account_id'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 매입채무

  IS1 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '기순' in row['account_nm'] and '영업' not in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 당기순이익
  IS2 = [(row['thstrm_amount']) for index, row in all.iterrows() if (row['sj_nm'] == '포괄손익계산서' or row['sj_nm'] == '손익계산서') and '영업이익' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 영업이익
  IS3 = [(row['thstrm_amount']) for index, row in all.iterrows() if (row['sj_nm'] == '포괄손익계산서' or row['sj_nm'] == '손익계산서') and row['account_nm'] == '수익(매출액)' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 수익(매출액)
  IS5 = [(row['thstrm_amount']) for index, row in all.iterrows() if (row['sj_nm'] == '포괄손익계산서' or row['sj_nm'] == '손익계산서') and (row['account_nm'] == '금융비용' or row['account_nm'] == '금융원가') and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 금융비용
  IS6 = [(row['thstrm_amount']) for index, row in all.iterrows() if (row['sj_nm'] == '포괄손익계산서' or row['sj_nm'] == '손익계산서') and row['account_nm'] == '수익(매출액)' and '제품' not in row['account_nm'] and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기 수익(매출액) # 분기 보고서만 해당

  print("자산총계:", BS1, "부채총계:", BS2, "자본총계:", BS3, "전기말 자산총계:", BS10,
        "전기말 자본총계:", BS12, "매입채무:", BS14, "당기순이익:", IS1, "영업이익:", IS2, "수익(매출액):", IS3,
        "금융비용:", IS5, "전기 수익(매출액):", IS6)

  if IS3 == []:
    IS3


  if year != 2020:
    if code == "11013":
      accounting_period = 90
    elif code == "11012":
      accounting_period = 181
    elif code == "11014":
      accounting_period = 273
    elif code == "11011":
      accounting_period = 365
  else: # 2020년은 윤년
    if code == "11013":
      accounting_period = 91
    elif code == "11012":
      accounting_period = 182
    elif code == "11014":
      accounting_period = 274
    elif code == "11011":
      accounting_period = 366

  cor_year.extend([f"{corp_code_p}{str_year}"])
  corp_name_list.append(str(corp_name_p))
  year_list.append(str_year)
  Debt_Ratio.extend([int(BS2)/int(BS3)*100 for BS2, BS3 in zip(BS2, BS3)])
  Return_on_Equity.extend([int(IS1)/((int(BS12)+int(BS3))/2) for IS1, BS12, BS3 in zip(IS1, BS12, BS3)])
  Operating_Profit_Margin.extend([int(IS2)/int(IS3) for IS2, IS3 in zip(IS2, IS3)])
  Interest_Coverage_Ratio.extend([int(IS2)/int(IS5) for IS2, IS5 in zip(IS2, IS5)])
  Total_Asset_Growth_Rate.extend([(int(BS1)-int(BS10))/int(BS10) for BS1, BS10 in zip(BS1, BS10)])
  Equity_Growth_Rate.extend([(int(BS3)-int(BS12))/int(BS12) for BS3, BS12 in zip(BS3, BS12)])
  Accounts_Payable_Turnover.extend([int(BS14)/int(IS3)*accounting_period for BS14, IS3 in zip(BS14, IS3)])
  Total_Asset_Turnover_Ratio.extend([int(IS3)/int(BS1) for IS3, BS1 in zip(IS3, BS1)])

ID_list.extend([x+y for x,y in zip(cor_year,Quarter)])

financial_ratio = {
      'ID':ID_list,
      '기업명':corp_name_list,
      '연도':year_list,
      '보고서 코드':report_code_list,
      '부채비율' : Debt_Ratio,
      '자기자본순이익률':Return_on_Equity,
      '매출액영업이익률':Operating_Profit_Margin,
      '이자보상배율(배)':Interest_Coverage_Ratio,
      '총자산 증가율':Total_Asset_Growth_Rate,
      '자기자본 증가율':Equity_Growth_Rate,
      '매입채무 회전기일(일)':Accounts_Payable_Turnover,
      '총자산 회전율':Total_Asset_Turnover_Ratio
                    }

df_fr = pd.DataFrame(financial_ratio)
df_fr.set_index('ID', inplace=True)

# print(df_fr)

df_fr.to_csv(f'{corp_name_p}_재무비율_백테스트_최종.csv')

## 코오롱 글로벌 2023년 3분기 값 이상해서 행 자체를 빼버림