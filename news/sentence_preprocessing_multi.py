###############
# 문장 DB 구축 #
###############

import kss
import pandas as pd
from multiprocessing import Pool, cpu_count
import numpy as np

# 1. 문장 split
## 문장 split 함수 정의
def split_sentences(content):
    return kss.split_sentences(content)

def process_chunk(chunk):
    # 각 청크에 대해 문장 split 함수 적용
    chunk['문장'] = chunk['기사_전처리'].apply(split_sentences)
    return chunk

if __name__ == "__main__":
    
    # 코어 수 설정
    num_cores = 6

    # 데이터 불러오기
    news = pd.read_csv('news_DB.csv', encoding='utf-8-sig')

    # 데이터를 청크로 나누기
    chunks = np.array_split(news, num_cores)

    with Pool(processes=num_cores) as pool:
        # 멀티프로세싱을 사용하여 각 청크 병렬 처리
        processed_chunks = pool.map(process_chunk, chunks)

    # 결과 병합
    news_processed = pd.concat(processed_chunks, ignore_index=True)

    # 행 단위를 문장으로 변경
    sentences = news_processed.explode('문장', ignore_index=True)

    E_aspect_term = '기후변화|기후 변화|수자원|재생에너지|탄소|수소|오염|폐기물|재활용|지구온난화|원자력|우라늄|카본|배출|파괴'
    S_aspect_term = '노동자|안전보건|산업재해|노동조합|현장|중대재해법'
    G_aspect_term = '주주|이사회|경영진|대표이사|관계사|사업보고서|간담회|총회|사명'

    sentences['구분'] = None  # 기본값은 none

    aspect_terms = {
        'E': E_aspect_term.split('|'),
        'S': S_aspect_term.split('|'),
        'G': G_aspect_term.split('|'),
    }

    sentences['구분'] = sentences['문장'].apply(
        lambda x: [aspect for aspect, terms in aspect_terms.items() if any(term in x for term in terms)]
    )

    sentences = sentences[sentences['구분'].apply(len) > 0] # 어느 asepct에도 해당하지 않는 경우 제외
    sentences = sentences.explode('구분', ignore_index=True)

    
    # 컬럼 정리 및 파일 저장
    sentences = sentences.drop(['기사', '기사_전처리'], axis=1)
    print(sentences)
    sentences.to_csv('sentences_DBcsv', encoding='utf-8-sig', index=False)
