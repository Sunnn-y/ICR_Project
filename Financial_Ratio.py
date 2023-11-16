import OpenDartReader
import pandas as pd
my_api = "e9239b06215e8ff1addd0cc65d1b144a10af6d57"

dart = OpenDartReader(my_api)

corp_name = ['DL이앤씨', 'HDC현대산업개발', '동아지질', '한전KPS', '일진파워', 'HJ중공업', '신세계건설', 'KCC건설', '대우건설', '서희건설', '특수건설', '계룡건설산업', '동원개발', '신원종합개발', '서한', '일성건설', '태영건설', '화성산업', '범양건영', '현대건설', '현대건설', 'GS건설', '동부건설', '코오롱글로벌', 'DL건설', '진흥기업', '남광토건', '한신공영', '금호건설', '삼부토건']
corp_code = ['375500', '294870', '028100', '051600', '094820', '097230', '034300', '021320', '047040', '035890', '026150', '013580', '013120', '017000', '011370', '013360', '009410', '002460', '002410', '000720', '000720', '006360', '005960', '003070', '001880', '002780', '001260', '004960', '002990', '001470']
repr_code = ["11013", "11012", "11014", "11011"] # '11013'=1분기보고서, '11012'=반기보고서, '11014'=3분기보고서, '11011'=사업보고서

all = pd.DataFrame()

for year in range(2019, 2023):
  for co_code in corp_code:
    for code in repr_code:
      corp = dart.finstate_all(co_code, year, code, fs_div="OFS")
      # corp = corp.drop('account_id', axis=1) # 영문 계정과목 삭제
      all = pd.concat([all, corp], ignore_index=True) # 건설업계 모든 기업 2019년~2022년 별도 재무제표 전문


corp_name = []
year_list = []
reprt_code = []
Debt_Ratio = []
Debt_to_Asset_Ratio = []
Fixed_Asset_Turnover_Ratio = []
Return_on_Equity = []
Operating_Profit_Margin = []
Gross_Profit_Margin = []
Interest_Coverage_Ratio =[]
Sales_Growth_Rate = []
Total_Asset_Growth_Rate = []
Operating_Profit_Growth_Rate = []
Equity_Growth_Rate= []
Accounts_Receivable_Turnover = []
Inventory_Turnover = []
Accounts_Payable_Turnover = []
Total_Asset_Turnover_Ratio = []
Debt_Service_Coverage_Ratio = []
Debt_to_Equity_Ratio = []


for year in range(2020, 2023):
  str_year = str(year)
  try:
    reprt_code.extend([ '1분기보고서' if code == '11013' else '반기보고서' if code == '11012' else '3분기보고서' if code == '11014' else '사업보고서' for code in repr_code])
    for code in repr_code:
      BS1 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '자산총계' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 자산총계
      BS2 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '부채총계' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 부채총계
      BS3 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '자본총계' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 자본총계
      BS4 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '단기차입금' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 단기차입금
      BS5 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '유동성장기부채' or row['account_nm'] == '유동성장기채무' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 유동성장기부채
      BS6 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and '사채' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 사채
      BS7 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and '장기차입금' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 장기차입금
      BS8 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '비유동자산' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 비유동자산
      BS9 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '비유동부채' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 비유동부채
      BS10 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '자산총계' and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 자산총계
      BS11 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '부채총계' and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 부채총계
      BS12 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '자본총계' and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 자본총계
      BS13 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and '매출채권' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == code] # 매출채권
      BS14 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '매입채무' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 매입채무
      BS15 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '기타자본' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 기타자본
      BS16 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '재무상태표' and row['account_nm'] == '기타자본' and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기말 기타자본
      
      IS1 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '당기순이익' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 당기순이익
      IS2 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '영업이익' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 영업이익
      IS3 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '매출액' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 수익(매출액)
      IS4 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '법인세' in row['account_nm'] and '차감전' in row['account_nm'] and '순이익' in row['account_nm'] and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 법인세비용차감전순이익(손실)
      IS5 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and row['account_nm'] == '금융비용' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 금융비용
      IS6 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '매출액' in row['account_nm'] and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기 수익(매출액) # 분기 보고서만 해당
      IS7 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '포괄손익계산서' and '영업이익' in row['account_nm'] and row['bsns_year'] == str(year-1) and row['reprt_code'] == str(code)] # 전기 영업이익 # 분기 보고서만 해당

      CF1 = [(row['thstrm_amount']) for index, row in all.iterrows() if row['sj_nm'] == '현금흐름표' and row['account_nm'] == '영업활동으로 인한 현금흐름' and row['bsns_year'] == str(year) and row['reprt_code'] == str(code)] # 영업활동으로 인한 현금흐름

      if BS6 == BS7: # '사채 및 장기차입금'으로 계정과목 하나만 쓰는 회사는 합침(어차피 사채는 차입금 의존도에서만 사용해서 하나 0으로 만들어도 상관없음)
        BS6[0] = '0'

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


      corp_name.append("삼성물산")
      year_list.append(str_year)
      Debt_Ratio.extend([int(BS2)/int(BS3)*100 for BS2, BS3 in zip(BS2, BS3)])
      Debt_to_Asset_Ratio.extend([((int(BS4[i]) + int(BS5[i]) + int(BS6[i]) + int(BS7[i])) / int(BS1[i]) * 100) for i in range(len(BS4))])
      Fixed_Asset_Turnover_Ratio.extend([int(BS8)/(int(BS9)+int(BS3))*100 for BS8, BS9, BS3 in zip(BS8, BS9, BS3)]),
      Return_on_Equity.extend([int(IS1)/((int(BS12)-int(BS15)+int(BS3)-int(BS16))/2) for IS1, BS12, BS3, BS15, BS16 in zip(IS1, BS12, BS3, BS15, BS16)])
      Operating_Profit_Margin.extend([int(IS2)/int(IS3) for IS2, IS3 in zip(IS2, IS3)])
      Gross_Profit_Margin.extend([int(IS4)/int(IS3) for IS4, IS3 in zip(IS4, IS3)])
      Interest_Coverage_Ratio.extend([int(IS2)/int(IS5) for IS2, IS5 in zip(IS2, IS5)])
      Sales_Growth_Rate.extend([(int(IS3)-int(IS6))/int(IS6) for IS3, IS6 in zip(IS3, IS6)])
      Total_Asset_Growth_Rate.extend([(int(BS1)-int(BS10))/int(BS10) for BS1, BS10 in zip(BS1, BS10)])
      Operating_Profit_Growth_Rate.extend([(int(IS2)-int(IS7))/int(IS7) for IS2, IS7 in zip(IS2, IS7)])
      Equity_Growth_Rate.extend([(int(BS3)-int(BS12))/int(BS12) for BS3, BS12 in zip(BS3, BS12)])
      Accounts_Receivable_Turnover.extend([int(BS13)/int(IS3)*accounting_period for BS13, IS3 in zip(BS13, IS3)])
      Inventory_Turnover.extend([int(BS15)/int(IS3)*accounting_period for BS15, IS3 in zip(BS15, IS3)])
      Accounts_Payable_Turnover.extend([int(BS14)/int(IS3)*accounting_period for BS14, IS3 in zip(BS14, IS3)])
      Total_Asset_Turnover_Ratio.extend([int(IS3)/int(BS1) for IS3, BS1 in zip(IS3, BS1)])
      Debt_Service_Coverage_Ratio.extend([(int(CF1)+int(IS5))/(int(BS4)+int(BS5)+int(IS5)) for CF1, IS5, BS4, BS5 in zip(CF1, IS5, BS4, BS5)])
      Debt_to_Equity_Ratio.extend([int(CF1)/(int(BS4)+int(BS7)) for CF1, BS4, BS7 in zip(CF1, BS4, BS7)])
  except:
    pass


financial_ratio = {
      '기업명':corp_name,
      '연도':year_list,
      '보고서 코드':reprt_code,
      '부채비율' : Debt_Ratio,
      '차입금의존도' : Debt_to_Asset_Ratio,
      '고정장기적합률':Fixed_Asset_Turnover_Ratio,
      '자기자본순이익률':Return_on_Equity,
      '매출액영업이익률':Operating_Profit_Margin,
      '매출액경상이익률':Gross_Profit_Margin,
      '이자보상배율(배)':Interest_Coverage_Ratio,
      '매출액 증가율':Sales_Growth_Rate,
      '총자산 증가율':Total_Asset_Growth_Rate,
      '영업이익 증가율':Operating_Profit_Growth_Rate,
      '자기자본 증가율':Equity_Growth_Rate,
      '매출채권 회전기일(일)':Equity_Growth_Rate,
      '재고자산 회전기일(일)':Accounts_Receivable_Turnover, 
      '매입채무 회전기일(일)':Accounts_Payable_Turnover, 
      '총자산 회전율':Total_Asset_Turnover_Ratio,
      '부채상환계수(배)':Debt_Service_Coverage_Ratio,
      '총차입금상환능력비율':Debt_to_Equity_Ratio
                     }

df = pd.DataFrame(financial_ratio)
print(df)

