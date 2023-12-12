# 필요한 라이브러리 설치
pip install mxnet                    # mxnet: 딥러닝 프레임워크
pip install gluonnlp pandas tqdm     # gluonnlp: 오픈소스 딥러닝 기반의 자연어 처리 툴킷
pip install sentencepiece            # sentencepiece: pre-tokenization을 필요로 하지 않는 tokenizer
pip install transformers             # transformer
pip install torch                    # torch


# https://github.com/SKTBrain/KoBERT 의 파일을 Colab으로 다운로드
pip install 'git+https://git@github.com/SKTBrain/KoBERT.git@master'
pip install 'git+https://github.com/SKTBrain/KoBERT.git#egg=kobert_tokenizer&subdirectory=kobert_hf'


# 필요한 라이브러리 import
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np
from tqdm import tqdm, tqdm_notebook
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore')


# Hugging Face를 통한 모델 및 토크나이저 Import
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertModel
from transformers import AdamW
from transformers.optimization import get_cosine_schedule_with_warmup


# GPU 사용 시
device = torch.device("cuda:0")


tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
vocab = nlp.vocab.BERTVocab.from_sentencepiece(tokenizer.vocab_file, padding_token='[PAD]')