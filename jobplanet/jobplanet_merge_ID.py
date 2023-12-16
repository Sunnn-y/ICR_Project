import pandas as pd

## 잡플래닛 결과물에 ID merge

rating_list = pd.read_csv('df_rating.csv', encoding='utf-8-sig')
rating_list['종목코드']  = rating_list['종목코드'].astype(str).str.zfill(6)
rating_list = rating_list[['종목명', '종목코드']].drop_duplicates()

def merge_csv_files(file_a, file_b, common_column, output_path=None):

    df_FR = pd.read_csv(file_a, encoding='utf-8-sig')
    df_ICR = pd.read_csv(file_b, encoding='utf-8-sig')

    merged_df = pd.merge(df_FR, df_ICR, how='left', on=common_column) # 두 데이터프레임을 공통 열을 기준으로 병합

    if output_path:
        merged_df.to_csv(output_path, index=False)

    return merged_df

# file_a = 'jobplanet_건설업계_개별점수.csv'
# file_b = 'df_rating.csv'
# common_column = "ID"
# output_path = "jobplanet_건설업계_개별점수_IDmerge.csv"
# result_df_merge = merge_csv_files(file_a, file_b, common_column, output_path)

file_a = 'jobplanet_건설업계_분기별점수.csv'
file_b = 'df_rating.csv'
common_column = "ID"
output_path = "jobplanet_건설업계_분기별점수_IDmerge.csv"
result_df_merge = merge_csv_files(file_a, file_b, common_column, output_path)

