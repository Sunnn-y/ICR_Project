## 재무비율 데이터 합치기

import os
import glob
import pandas as pd

def concat_all_csv_files(folder_path, output_path=None):
    file_paths = glob.glob(os.path.join(folder_path, '*.csv'))

    if not file_paths:
        raise ValueError("No CSV files found in the specified folder.")

    result_df = pd.concat(map(pd.read_csv, file_paths), ignore_index=True)

    if output_path:
        result_df.to_csv(output_path, index=False)

    return result_df


folder_path = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project"
output_path = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\건설업계_재무비율_백테스트_임시.csv"
result_df = concat_all_csv_files(folder_path, output_path)


## 재무비율에 신용등급 merge
result_df = result_df.rename(columns={'아이디': 'ID'})
result_df.to_csv('C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Projec\건설업계_재무비율_백테스트.csv')

result_df.set_index('ID', inplace=True)

def merge_csv_files(file_a, file_b, common_column, output_path=None):
    df_FR = pd.read_csv(file_a)
    df_ICR = pd.read_csv(file_b)
    # 두 데이터프레임을 공통 열을 기준으로 병합
    merged_df = pd.merge(df_FR, df_ICR, how='left', on=common_column)

    if output_path:
        merged_df.to_csv(output_path, index=False)

    return merged_df


file_a = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\건설업계_재무비율_백테스트.csv"
file_b = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\df_rating.csv"
common_column = "ID"
output_path = "merged_result.csv"
result_df_merge = merge_csv_files(file_a, file_b, common_column, output_path)

result_df_merge.set_index('ID', inplace=True)
result_df_merge.to_csv('C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\건설업계_재무비율_백테스트_신용등급_merge.csv')

#정규화
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)

result_df_merge
result_df_merge.info()

# 무한대 값을 NaN으로 대체
import math
result_df_merge.replace(float(math.inf), float(1.5), inplace=True)

result_df_merge.fillna(result_df_merge.median(numeric_only=True), inplace=True)

from sklearn.preprocessing import MinMaxScaler

minmax_scaler = MinMaxScaler()

# 정규화할 열 선택
columns_to_normalize = result_df_merge[['부채비율', '차입금의존도', '고정장기적합률', '자기자본순이익률', '매출액영업이익률', '매출액경상이익률', '이자보상배율(배)',
                                        '매출액 증가율', '총자산 증가율', '영업이익 증가율', '자기자본 증가율', '매출채권 회전기일(일)', '재고자산 회전기일(일)', '매입채무 회전기일(일)',
                                        '총자산 회전율', '부채상환계수(배)','총차입금상환능력비율']]

minmax_scaled = minmax_scaler.fit_transform(columns_to_normalize)

# 정규화된 값으로 열을 대체
result_df_merge[['부채비율', '차입금의존도', '고정장기적합률', '자기자본순이익률', '매출액영업이익률', '매출액경상이익률', '이자보상배율(배)',
                 '매출액 증가율', '총자산 증가율', '영업이익 증가율', '자기자본 증가율', '매출채권 회전기일(일)', '재고자산 회전기일(일)', '매입채무 회전기일(일)',
                 '총자산 회전율', '부채상환계수(배)','총차입금상환능력비율']] = minmax_scaled

pd.DataFrame(result_df_merge)
result_df_merge

## Feature Selection
## RFECV
from sklearn.model_selection import train_test_split

X = result_df_merge.iloc[:, -22:-6]
y = result_df_merge['등급']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 1)

from sklearn.feature_selection import RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE

estimator = LogisticRegression() # 학습시킬 모델 지정
selector = RFECV(estimator, step=1, cv = 3) # 한 step에 제거할 featrue 개수 및 cross validation fold 수 지정
selector = selector.fit(X_train, y_train) # feature selection 진행

from sklearn.metrics import f1_score

selected_columns = X_train.columns[selector.support_]
X_train_selected = X_train[selected_columns]

estimator.fit(X_train_selected, y_train)

X_test_selected = X_test[selected_columns]

y_pred = estimator.predict(X_test_selected)

f1 = f1_score(y_test, y_pred, average='weighted') # F1 Score 계산

print("Selected features:", selected_columns)
print("F1 Score (Weighted Average):", f1)
     
## SelectBest
from sklearn.feature_selection import f_classif, SelectKBest

selector = SelectKBest(score_func=f_classif, k=6)

X_train_selected = selector.fit_transform(X_train, y_train) ## 학습데이터에 fit_transform

X_test_selected = selector.transform(X_test) ## 테스트 데이터는 transform

X_train_selected.shape, X_test_selected.shape

all_names = X_train.columns

selected_mask = selector.get_support()
selected_names = all_names[selected_mask] ## 선택된 특성(변수)들
unselected_names = all_names[~selected_mask] ## 선택되지 않은 특성(변수)들

print('Selected names: ', selected_names)
print('Unselected names: ', unselected_names)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

model = LogisticRegression()

model.fit(X_train_selected, y_train)

X_test_selected = selector.transform(X_test)

y_pred = model.predict(X_test_selected)

f1 = f1_score(y_test, y_pred, average='weighted') # F1 Score 계산

print("Selected features:", selected_names)
print("F1 Score (Weighted Average):", f1)