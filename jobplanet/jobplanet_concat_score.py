import glob
import os
import pandas as pd

def concat_all_csv_files(folder_path, output_path=None):

    file_paths = glob.glob(os.path.join(folder_path, '*.csv'))

    if not file_paths:
        raise ValueError("No CSV files found in the specified folder.")

    result_df = pd.concat(map(pd.read_csv, file_paths), ignore_index=True)

    if output_path:
        result_df.to_csv(output_path, index=False)

    return result_df

folder_path = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\jobplanet"
output_path = "C:\Users\USER\통합 문서\핀테크 데이터분석\ICR_Project\jobplanet\jobplanet_건설업계_분기별점수.csv"
result_df = concat_all_csv_files(folder_path, output_path)