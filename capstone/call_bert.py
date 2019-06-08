import numpy as np
import pandas as pd
from bert_serving.client import BertClient
bc = BertClient(ip="bert_as_a_service", check_length=False, check_version=False)

lc_dict = pd.read_excel('./data/LC_data/LCDataDictionary.xlsx')

# clean data
lc_dict = lc_dict[pd.notnull(lc_dict['Description'])]
lc_dict = lc_dict.iloc[:-1, :]

lc_column_desc = lc_dict['Description'].tolist()

lc_column_vecs = bc.encode(lc_column_desc)

def rankSimilarity(input_str, n=10):

    prosper_str_vec = bc.encode([input_str])[0]
    # compute normalized dot product as score
    score = np.sum(prosper_str_vec * lc_column_vecs, axis=1) / np.linalg.norm(lc_column_vecs, axis=1)
    topk_idx = np.argsort(score)[::-1][:10]
    print('top {n} lc columns similar to {input_str}'.format(n=n, input_str=input_str))
    
    result = {}
    for i, idx in enumerate(topk_idx, start=1):
    	#print((score[idx], lc_dict['LoanStatNew'][idx], lc_column_desc[idx]))
    	result[lc_dict['LoanStatNew'][idx]] = {'desc':lc_column_desc[idx], 'score': str(score[idx]), 'rank': i}

    return result
