"""02. news_ESG_score.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OjW9HYbHNnrRBgIQ8dKUsca5tukGVxsl
"""

# 1. 환경 설정 : 런타임 - 런타임 유형 변경 - GPU
from google.colab import drive
drive.mount('/content/drive')

# Colab 파이썬 버전 확인
import sys
print(sys.version)

# 필요한 라이브러리 설치
!pip install mxnet                    # mxnet: 딥러닝 프레임워크
!pip install gluonnlp pandas tqdm     # gluonnlp: 오픈소스 딥러닝 기반의 자연어 처리 툴킷
!pip install sentencepiece            # sentencepiece: pre-tokenization을 필요로 하지 않는 tokenizer
!pip install transformers             # transformer
!pip install torch                    # torch
!pip install kss                      # kss

# https://github.com/SKTBrain/KoBERT 의 파일을 Colab으로 다운로드
!pip install 'git+https://git@github.com/SKTBrain/KoBERT.git@master'
!pip install 'git+https://github.com/SKTBrain/KoBERT.git#egg=kobert_tokenizer&subdirectory=kobert_hf'

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

# Hugging Face를 통한 모델 및 토크나이저 Import
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertModel
from transformers import AdamW
from transformers.optimization import get_cosine_schedule_with_warmup

import os
import re

# GPU 사용 시
device = torch.device("cuda:0")

# 데이터 준비

df = pd.read_csv('/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/sentences_DB_중복제거.csv', encoding='utf-8-sig')

df['종목코드']  = df['종목코드'].astype(str).str.zfill(6)

df['작성날짜'] = pd.to_datetime(df['작성날짜'])
df['날짜'] = pd.to_datetime(df['날짜'])

df_E = df[df['구분']=='E']
df_S = df[df['구분']=='S']
df_G = df[df['구분']=='G']

# 2. 모델 파인튜닝 및 점수 산출 함수

# 1) E_model

# 학습데이터 불러오기
import pandas as pd
E_sentences = pd.read_csv('/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/E_sentences.csv', encoding='utf-8-sig')

E_sentences = E_sentences.dropna()
E_sentences['score'] = E_sentences['score'].astype(int)
E_sentences = E_sentences[E_sentences['score'] != 9]

# data_list 생성 (tensor 형식)
data_list = []
for review, label in zip(E_sentences['sentence'], E_sentences['score']):
    data = []
    data.append(review)
    data.append(label)
    data_list.append(data)

# train, test 데이터셋으로 나눔
from sklearn.model_selection import train_test_split
dataset_train, dataset_test = train_test_split(data_list, test_size = 0.2, shuffle = True, random_state = 32, stratify=E_sentences['score'])

tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
vocab = nlp.vocab.BERTVocab.from_sentencepiece(tokenizer.vocab_file, padding_token='[PAD]')

# PyTorch의 Dataset 클래스를 상속받아 BERT 모델을 학습하기 위한 데이터셋을 생성하는 클래스인 BERTDataset을 정의
# 이 클래스는 데이터셋을 BERT 모델의 입력 형식으로 변환하는 역할

class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, vocab, max_len, pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, vocab=vocab, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))

"""BERTDataset 클래스의 파라미터  
* dataset: BERT 모델 학습에 사용될 데이터셋
*  sent_idx: 문장(텍스트)이 있는 열의 인덱스입니다.
* label_idx: 레이블이 있는 열의 인덱스입니다.
* bert_tokenizer: BERT 토크나이저입니다.
* vocab: 어휘 사전입니다.
* max_len: 최대 시퀀스 길이입니다.
* pad: 패딩 여부를 나타내는 불리언 값입니다.
* pair: 문장 페어(pair) 여부를 나타내는 불리언 값입니다.

BERTDataset 클래스의 메서드
* __init__(self, ...): 클래스의 초기화 메서드로, 주어진 매개변수들을 사용하여 데이터셋을 BERT 모델의 입력 형식으로 변환할 수 있는 변환 객체를 생성합니다.
* __getitem__(self, i): 주어진 인덱스 i에 해당하는 데이터셋의 항목을 반환. 반환되는 항목은 BERT 모델의 입력으로 사용될 수 있도록 변환된 문장과 해당 문장의 레이블
* __len__(self): 데이터셋의 전체 길이를 반환
"""

# 하이퍼파라미터
max_len = 64
batch_size = 64
warmup_ratio = 0.1
num_epochs = 5
max_grad_norm = 1
log_interval = 200
learning_rate =  5e-5

tok = tokenizer.tokenize

train = BERTDataset(dataset_train, 0, 1, tok, vocab, max_len, True, False)
test = BERTDataset(dataset_test, 0, 1, tok, vocab, max_len, True, False)

train_dataloader = torch.utils.data.DataLoader(train, batch_size=batch_size, num_workers=2)
test_dataloader = torch.utils.data.DataLoader(test, batch_size=batch_size, num_workers=2)

class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size=768, num_classes=3, dr_rate=None, params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler
        return self.classifier(out)

# import os
# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
E_model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)

# Prepare optimizer and schedule (linear warmup and decay)
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in E_model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in E_model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate)
loss_fn = nn.CrossEntropyLoss()

t_total = len(train_dataloader) * num_epochs
warmup_step = int(t_total * warmup_ratio)

scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_step, num_training_steps=t_total)

def calc_accuracy(X,Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().data.cpu().numpy()/max_indices.size()[0]
    return train_acc

for e in range(num_epochs):
    train_acc = 0.0
    test_acc = 0.0
    E_model.train()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(train_dataloader)):
        optimizer.zero_grad()
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = E_model(token_ids, valid_length, segment_ids)
        loss = loss_fn(out, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(E_model.parameters(), max_grad_norm)
        optimizer.step()
        scheduler.step()  # Update learning rate schedule
        train_acc += calc_accuracy(out, label)
        if batch_id % log_interval == 0:
            print("epoch {} batch id {} loss {} train acc {}".format(e+1, batch_id+1, loss.data.cpu().numpy(), train_acc / (batch_id+1)))
    print("epoch {} train acc {}".format(e+1, train_acc / (batch_id+1)))

    E_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(test_dataloader)):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = E_model(token_ids, valid_length, segment_ids)
        test_acc += calc_accuracy(out, label)
    print("epoch {} test acc {}".format(e+1, test_acc / (batch_id+1)))

    print("E_model 학습 완료")

# 모델 저장
# torch.save(E_model, "/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/E_model.pt")

def E_score_predict(predict_sentence):
    data = [predict_sentence, '0']
    dataset_another = [data]
    another_test = BERTDataset(dataset_another, 0, 1, tok, vocab, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=2)

    E_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length= valid_length
        label = label.long().to(device)

        out = E_model(token_ids, valid_length, segment_ids)
        test_eval=[]
        for i in out:
          logits=i
          logits = logits.detach().cpu().numpy()
          test_eval.append(logits)
        probabilities = F.softmax(torch.tensor(test_eval[0]), dim=0).numpy()
        # print(">> 입력하신 내용에 대한 확률 값은:", probabilities)


    return probabilities[0], probabilities[1], probabilities[2]


# 2) S_model

# 학습데이터 불러오기
import pandas as pd
S_sentences = pd.read_csv('/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/S_sentences.csv', encoding='utf-8-sig')

S_sentences = S_sentences.dropna()
S_sentences['score'] = S_sentences['score'].astype(int)
S_sentences = S_sentences[S_sentences['score'] != 9]

# data_list 생성 (tensor 형식)
data_list = []
for review, label in zip(S_sentences['sentence'], S_sentences['score']):
    data = []
    data.append(review)
    data.append(label)
    data_list.append(data)

# train, test 데이터셋으로 나눔
from sklearn.model_selection import train_test_split
dataset_train, dataset_test = train_test_split(data_list, test_size = 0.2, shuffle = True, random_state = 32, stratify=S_sentences['score'])

tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
vocab = nlp.vocab.BERTVocab.from_sentencepiece(tokenizer.vocab_file, padding_token='[PAD]')

# PyTorch의 Dataset 클래스를 상속받아 BERT 모델을 학습하기 위한 데이터셋을 생성하는 클래스인 BERTDataset을 정의
# 이 클래스는 데이터셋을 BERT 모델의 입력 형식으로 변환하는 역할

class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, vocab, max_len, pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, vocab=vocab, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))

"""BERTDataset 클래스의 파라미터  
* dataset: BERT 모델 학습에 사용될 데이터셋
*  sent_idx: 문장(텍스트)이 있는 열의 인덱스입니다.
* label_idx: 레이블이 있는 열의 인덱스입니다.
* bert_tokenizer: BERT 토크나이저입니다.
* vocab: 어휘 사전입니다.
* max_len: 최대 시퀀스 길이입니다.
* pad: 패딩 여부를 나타내는 불리언 값입니다.
* pair: 문장 페어(pair) 여부를 나타내는 불리언 값입니다.

BERTDataset 클래스의 메서드
* __init__(self, ...): 클래스의 초기화 메서드로, 주어진 매개변수들을 사용하여 데이터셋을 BERT 모델의 입력 형식으로 변환할 수 있는 변환 객체를 생성합니다.
* __getitem__(self, i): 주어진 인덱스 i에 해당하는 데이터셋의 항목을 반환. 반환되는 항목은 BERT 모델의 입력으로 사용될 수 있도록 변환된 문장과 해당 문장의 레이블
* __len__(self): 데이터셋의 전체 길이를 반환
"""

# 하이퍼파라미터
max_len = 64
batch_size = 64
warmup_ratio = 0.1
num_epochs = 5
max_grad_norm = 1
log_interval = 200
learning_rate =  5e-5

tok = tokenizer.tokenize

train = BERTDataset(dataset_train, 0, 1, tok, vocab, max_len, True, False)
test = BERTDataset(dataset_test, 0, 1, tok, vocab, max_len, True, False)

train_dataloader = torch.utils.data.DataLoader(train, batch_size=batch_size, num_workers=2)
test_dataloader = torch.utils.data.DataLoader(test, batch_size=batch_size, num_workers=2)

class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size=768, num_classes=3, dr_rate=None, params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler
        return self.classifier(out)

# import os
# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
S_model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)

# Prepare optimizer and schedule (linear warmup and decay)
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in S_model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in S_model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate)
loss_fn = nn.CrossEntropyLoss()

t_total = len(train_dataloader) * num_epochs
warmup_step = int(t_total * warmup_ratio)

scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_step, num_training_steps=t_total)

def calc_accuracy(X,Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().data.cpu().numpy()/max_indices.size()[0]
    return train_acc

for e in range(num_epochs):
    train_acc = 0.0
    test_acc = 0.0
    S_model.train()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(train_dataloader)):
        optimizer.zero_grad()
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = S_model(token_ids, valid_length, segment_ids)
        loss = loss_fn(out, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(S_model.parameters(), max_grad_norm)
        optimizer.step()
        scheduler.step()  # Update learning rate schedule
        train_acc += calc_accuracy(out, label)
        if batch_id % log_interval == 0:
            print("epoch {} batch id {} loss {} train acc {}".format(e+1, batch_id+1, loss.data.cpu().numpy(), train_acc / (batch_id+1)))
    print("epoch {} train acc {}".format(e+1, train_acc / (batch_id+1)))

    S_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(test_dataloader)):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = S_model(token_ids, valid_length, segment_ids)
        test_acc += calc_accuracy(out, label)
    print("epoch {} test acc {}".format(e+1, test_acc / (batch_id+1)))

    print("S_model 학습 완료")

# 모델 저장
# torch.save(S_model, "/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/S_model.pt")

def S_score_predict(predict_sentence):
    data = [predict_sentence, '0']
    dataset_another = [data]
    another_test = BERTDataset(dataset_another, 0, 1, tok, vocab, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=2)

    S_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length= valid_length
        label = label.long().to(device)

        out = S_model(token_ids, valid_length, segment_ids)
        test_eval=[]
        for i in out:
          logits=i
          logits = logits.detach().cpu().numpy()
          test_eval.append(logits)
        probabilities = F.softmax(torch.tensor(test_eval[0]), dim=0).numpy()
        # print(">> 입력하신 내용에 대한 확률 값은:", probabilities)


    return probabilities[0], probabilities[1], probabilities[2]

# 3) G_model

# 학습데이터 불러오기
import pandas as pd
G_sentences = pd.read_csv('/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/G_sentences.csv', encoding='utf-8-sig')

G_sentences = G_sentences.dropna()
G_sentences['score'] = G_sentences['score'].astype(int)
G_sentences = G_sentences[G_sentences['score'] != 9]
print(G_sentences['score'].value_counts())

# data_list 생성 (tensor 형식)
data_list = []
for review, label in zip(G_sentences['sentence'], G_sentences['score']):
    data = []
    data.append(review)
    data.append(label)
    data_list.append(data)

# train, test 데이터셋으로 나눔
from sklearn.model_selection import train_test_split
dataset_train, dataset_test = train_test_split(data_list, test_size = 0.2, shuffle = True, random_state = 32, stratify=G_sentences['score'])
print(len(dataset_train), len(dataset_test))

tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
vocab = nlp.vocab.BERTVocab.from_sentencepiece(tokenizer.vocab_file, padding_token='[PAD]')

# PyTorch의 Dataset 클래스를 상속받아 BERT 모델을 학습하기 위한 데이터셋을 생성하는 클래스인 BERTDataset을 정의
# 이 클래스는 데이터셋을 BERT 모델의 입력 형식으로 변환하는 역할

class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, vocab, max_len, pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, vocab=vocab, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))

"""BERTDataset 클래스의 파라미터  
* dataset: BERT 모델 학습에 사용될 데이터셋
*  sent_idx: 문장(텍스트)이 있는 열의 인덱스입니다.
* label_idx: 레이블이 있는 열의 인덱스입니다.
* bert_tokenizer: BERT 토크나이저입니다.
* vocab: 어휘 사전입니다.
* max_len: 최대 시퀀스 길이입니다.
* pad: 패딩 여부를 나타내는 불리언 값입니다.
* pair: 문장 페어(pair) 여부를 나타내는 불리언 값입니다.

BERTDataset 클래스의 메서드
* __init__(self, ...): 클래스의 초기화 메서드로, 주어진 매개변수들을 사용하여 데이터셋을 BERT 모델의 입력 형식으로 변환할 수 있는 변환 객체를 생성합니다.
* __getitem__(self, i): 주어진 인덱스 i에 해당하는 데이터셋의 항목을 반환. 반환되는 항목은 BERT 모델의 입력으로 사용될 수 있도록 변환된 문장과 해당 문장의 레이블
* __len__(self): 데이터셋의 전체 길이를 반환
"""

# 하이퍼파라미터
max_len = 64
batch_size = 64
warmup_ratio = 0.1
num_epochs = 5
max_grad_norm = 1
log_interval = 200
learning_rate =  5e-5

tok = tokenizer.tokenize

train = BERTDataset(dataset_train, 0, 1, tok, vocab, max_len, True, False)
test = BERTDataset(dataset_test, 0, 1, tok, vocab, max_len, True, False)

train_dataloader = torch.utils.data.DataLoader(train, batch_size=batch_size, num_workers=2)
test_dataloader = torch.utils.data.DataLoader(test, batch_size=batch_size, num_workers=2)

class BERTClassifier(nn.Module):
    def __init__(self, bert, hidden_size=768, num_classes=3, dr_rate=None, params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate

        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)

    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        else:
            out = pooler
        return self.classifier(out)

# import os
# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
G_model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)

# Prepare optimizer and schedule (linear warmup and decay)
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in G_model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in G_model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

optimizer = AdamW(optimizer_grouped_parameters, lr=learning_rate)
loss_fn = nn.CrossEntropyLoss()

t_total = len(train_dataloader) * num_epochs
warmup_step = int(t_total * warmup_ratio)

scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup_step, num_training_steps=t_total)

def calc_accuracy(X,Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().data.cpu().numpy()/max_indices.size()[0]
    return train_acc

for e in range(num_epochs):
    train_acc = 0.0
    test_acc = 0.0
    G_model.train()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(train_dataloader)):
        optimizer.zero_grad()
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = G_model(token_ids, valid_length, segment_ids)
        loss = loss_fn(out, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(G_model.parameters(), max_grad_norm)
        optimizer.step()
        scheduler.step()  # Update learning rate schedule
        train_acc += calc_accuracy(out, label)
        if batch_id % log_interval == 0:
            print("epoch {} batch id {} loss {} train acc {}".format(e+1, batch_id+1, loss.data.cpu().numpy(), train_acc / (batch_id+1)))
    print("epoch {} train acc {}".format(e+1, train_acc / (batch_id+1)))

    G_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(test_dataloader)):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = G_model(token_ids, valid_length, segment_ids)
        test_acc += calc_accuracy(out, label)
    print("epoch {} test acc {}".format(e+1, test_acc / (batch_id+1)))

    print("G_model 학습 완료")

# 모델 저장
# torch.save(G_model, "/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/G_model.pt")

def G_score_predict(predict_sentence):
    data = [predict_sentence, '0']
    dataset_another = [data]
    another_test = BERTDataset(dataset_another, 0, 1, tok, vocab, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=2)

    G_model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length= valid_length
        label = label.long().to(device)

        out = G_model(token_ids, valid_length, segment_ids)
        test_eval=[]
        for i in out:
          logits=i
          logits = logits.detach().cpu().numpy()
          test_eval.append(logits)
        probabilities = F.softmax(torch.tensor(test_eval[0]), dim=0).numpy()
        # print(">> 입력하신 내용에 대한 확률 값은:", probabilities)

    return probabilities[0], probabilities[1], probabilities[2]


# 3. 파일 머지

# 점수 뽑을 데이터
df = pd.read_csv(f'/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/sentences_DB_중복제거.csv', encoding='utf-8-sig')

df['날짜'] = pd.to_datetime(df['날짜'])
df['작성날짜'] = pd.to_dateti

# E, S, G df 분할
df_E = df[df['구분']=='E']
df_S = df[df['구분']=='S']
df_G = df[df['구분']=='G']

E_score = df_E['문장'].copy().apply(E_score_predict).apply(lambda x: x[2])
df_E['score'] = E_score
df_E.to_csv(f'/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/E_score.csv', encoding='utf-8-sig', index=False)

S_score = df_S['문장'].copy().apply(S_score_predict).apply(lambda x: x[2])
df_S['score'] = S_score
df_S.to_csv(f'/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/S_score.csv', encoding='utf-8-sig', index=False)

G_score = df_G['문장'].copy().apply(G_score_predict).apply(lambda x: x[2])
df_G['score'] = G_score
df_G.to_csv(f'/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/G_score.csv', encoding='utf-8-sig', index=False)

# 파일 병합
df_ESG = pd.concat([df_E, df_S, df_G])
df_ESG.to_csv(f'/content/drive/MyDrive/ICR_project/네이버뉴스 텍스트마이닝/ESG_result/ESG_score.csv', encoding='utf-8-sig', index=False)