import pandas as pd

# 파일 불러오기
ESG_score = pd.read_csv('ESG_score.csv')
ESG_score['종목코드'] = ESG_score['종목코드'].astype(str).str.zfill(6)
ESG_score = ESG_score.rename(columns={'score':'점수'})

# 기업명별, 분기별 데이터 groupby
result = ESG_score.groupby(['기업명', '날짜', 'ID', '구분']).mean()[['점수']]
result = result.unstack('구분').reset_index()
result.columns = result.columns.get_level_values(0)
result.columns = ['기업명', '날짜', 'ID', 'E', 'G', 'S']
result = result[['기업명', '날짜', 'ID', 'E', 'S', 'G']]

# 평균, 합계열 추가
result['ESG_평균'] = result[['E', 'S', 'G']].mean(axis=1)
result['ESG_합계'] = result[['E', 'S', 'G']].sum(axis=1)

# 반올림
result = result.round(3)

# 파일 저장
result.to_csv('ESG_score_건설업계_분기별.csv')