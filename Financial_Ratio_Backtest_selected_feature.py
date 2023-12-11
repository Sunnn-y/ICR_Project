### 기존 3년치 파일에서 필요없는 비율 삭제

import pandas as pd

df = pd.read_csv('건설업계_재무비율_신용등급_merge.csv')

df = df.drop(['차입금의존도', '고정장기적합률', '매출액경상이익률', '매출액 증가율', '영업이익 증가율', '매출채권 회전기일(일)', '재고자산 회전기일(일)', '부채상환계수(배)', '총차입금상환능력비율',
              '종목코드', '종목명', '회사명', '연분기'], axis=1)
# print(df)

df.to_csv('건설업계_재무비율_최종_신용등급_merge.csv')


