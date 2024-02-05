import pandas as pd

review = pd.read_csv(f'/content/drive/MyDrive/ICR_project/최종데이터/잡플래닛_건설업계_score.csv')
result = review.groupby(['기업명','날짜', '구분']).mean()[['점수']]
result = result.unstack(['구분']).reset_index()
result.columns = result.columns.get_level_values(0)
result.set_axis(['기업명', '날짜', '경영진', '발전가능성', '복지및급여', '사내문화', '워라밸'], axis=1, inplace=True)
result['잡플래닛_평균'] = result[['경영진', '발전가능성', '복지및급여', '사내문화', '워라밸']].mean(axis=1)
result['잡플래닛_합계'] = result[['경영진', '발전가능성', '복지및급여', '사내문화', '워라밸']].sum(axis=1)
result_rounded = result.round(3)
result_rounded.to_csv(f'/content/drive/MyDrive/ICR_project/최종데이터/잡플래닛_건설업계_분기별.csv', encoding = 'utf-8-sig', index=False)
