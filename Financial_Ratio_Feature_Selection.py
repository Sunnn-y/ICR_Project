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

