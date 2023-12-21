import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')

# 리뷰 데이터 불러오기
corp_name = ['DL이앤씨', 'HDC현대산업개발', '한전KPS', 'HJ중공업', '신세계건설', 'KCC건설', '대우건설', '서희건설', '특수건설', '계룡건설산업', '신원종합개발',
             '태영건설', '현대건설', 'GS건설', '동부건설', '코오롱글로벌', 'DL건설', '진흥기업', '남광토건', '한신공영', '금호건설', '삼부토건']

for i in corp_name:
  # ABSA 결과 합친 파일 넣어야 함
  df1 = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/001_경영진/jobplanet_{i}_경영진.csv', encoding='utf-8', index_col=0)
  df2 = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/002_발전가능성/jobplanet_{i}_발전가능성.csv', encoding='utf-8', index_col=0)
  df3 = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/003_복지및급여/jobplanet_{i}_복지및급여.csv', encoding='utf-8', index_col=0)
  df4 = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/004_사내문화/jobplanet_{i}_사내문화.csv', encoding='utf-8', index_col=0)
  df5 = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/005_워라밸/jobplanet_{i}_워라밸.csv', encoding='utf-8', index_col=0)

  df = pd.concat([df1, df2, df3, df4, df5], axis=0, ignore_index=True)

  # csv 파일로 저장하고
  # df.to_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_05_최종결과물/001_개별점수/jobplanet_{i}_개별점수.csv', encoding = 'utf-8-sig', index=False)