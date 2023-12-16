# 필요한 라이브러리 설치
# pip install mxnet                    # mxnet: 딥러닝 프레임워크
# pip install gluonnlp pandas tqdm     # gluonnlp: 오픈소스 딥러닝 기반의 자연어 처리 툴킷
# pip install sentencepiece            # sentencepiece: pre-tokenization을 필요로 하지 않는 tokenizer
# pip install transformers             # transformer
# pip install torch                    # torch


# https://github.com/SKTBrain/KoBERT 의 파일을 Colab으로 다운로드
# pip install 'git+https://git@github.com/SKTBrain/KoBERT.git@master'
# pip install 'git+https://github.com/SKTBrain/KoBERT.git#egg=kobert_tokenizer&subdirectory=kobert_hf'


# 필요한 라이브러리 import
import pandas as pd
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


# 학습 데이터 불러오기
df = pd.read_csv('학습데이터.csv', index_col=0)

# '감정'이 '중립'인 행 제거
df = df[df['감정'] != '중립']


# 라벨 변경(negative > 0, positive > 1)
def changeTo01(x):
  if x == '부정':
    return 0
  elif x == '긍정':
    return 1

df['감정'] = df['감정'].apply(changeTo01)


# [발화문, 상황] data_list 생성
data_list = []

for review, label in zip(df['문장'], df['감정']):
  data = []
  data.append(review)
  data.append(label)
  data_list.append(data)

# train, test 데이터셋으로 나눔
from sklearn.model_selection import train_test_split
dataset_train, dataset_test = train_test_split(data_list, test_size = 0.2, shuffle = True, random_state = 32, stratify=df['감정'])
print(len(dataset_train), len(dataset_test))

# 데이터셋 토큰화
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

train_dataloader = torch.utils.data.DataLoader(train, batch_size=batch_size, num_workers=5)
test_dataloader = torch.utils.data.DataLoader(test, batch_size=batch_size, num_workers=5)


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


model = BERTClassifier(bertmodel, dr_rate=0.5).to(device)


# Prepare optimizer and schedule (linear warmup and decay)
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
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
    model.train()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(train_dataloader)):
        optimizer.zero_grad()
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = model(token_ids, valid_length, segment_ids)

        loss = loss_fn(out, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()
        scheduler.step()  # Update learning rate schedule
        train_acc += calc_accuracy(out, label)
        if batch_id % log_interval == 0:
            print("epoch {} batch id {} loss {} train acc {}".format(e+1, batch_id+1, loss.data.cpu().numpy(), train_acc / (batch_id+1)))
    print("epoch {} train acc {}".format(e+1, train_acc / (batch_id+1)))

    model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm_notebook(test_dataloader)):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)
        valid_length= valid_length
        label = label.long().to(device)
        out = model(token_ids, valid_length, segment_ids)
        test_acc += calc_accuracy(out, label)
    print("epoch {} test acc {}".format(e+1, test_acc / (batch_id+1)))
    
    
    
    # 모델 state dict만 저장하기
    torch.save(model.state_dict(), "model.pt")
    category = {'부정':0,'긍정':1}



def predict(predict_sentence):
    data = [predict_sentence, '0']
    dataset_another = [data]
    another_test = BERTDataset(dataset_another, 0, 1, tok, vocab, max_len, True, False)
    test_dataloader = torch.utils.data.DataLoader(another_test, batch_size=batch_size, num_workers=2)

    model.eval()
    for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(test_dataloader):
        token_ids = token_ids.long().to(device)
        segment_ids = segment_ids.long().to(device)

        valid_length= valid_length
        label = label.long().to(device)

        out = model(token_ids, valid_length, segment_ids)
        test_eval=[]
        for i in out:
          logits=i
          logits = logits.detach().cpu().numpy()
          # test_eval.append(list(category.keys())[(np.argmax(logits))]) # 원본 데이터
          test_eval.append(logits)
        # print(">> 입력하신 내용은 '" + test_eval[0] + "'의 카테고리로 예측되었습니다.")
        probabilities = F.softmax(torch.tensor(test_eval[0]), dim=0).numpy()
        # print(">> 입력하신 내용에 대한 확률 값은:", probabilities)

    return probabilities[1]




# 리뷰 데이터 불러오기
corp_name = ['DL이앤씨', 'HDC현대산업개발', '한전KPS', 'HJ중공업', '신세계건설', 'KCC건설', '대우건설', '서희건설', '특수건설', '계룡건설산업', '신원종합개발',
             '태영건설', '현대건설', '동부건설', '코오롱글로벌', 'DL건설', '진흥기업', '남광토건', '한신공영', '금호건설', '삼부토건']

for i in corp_name:
  review = pd.read_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_03_실제데이터/jobplanet_{i}_실제데이터.csv')

  # ID 칼럼 타입 변환
  review['ID'] = review['ID'].astype(object)

  # aspect 칼럼 추가
  review['구분'] = '경영진'

  # 점수 추출(소수점 세 번째 자리까지 표시)
  review['점수'] = review['총평'].apply(predict)
  review['점수'] = round(review['점수'],3)

  # 최종 데이터 생성
  result = review[['ID', '종목명', '분기', '총평','구분', '점수']]

  # jobplanet_기업명_경영진.csv 파일로 저장
  result.to_csv(f'/content/drive/MyDrive/ICR_project/잡플래닛_04_ABSA결과/001_경영진/jobplanet_{i}_경영진.csv', encoding = 'utf-8-sig', index=False)