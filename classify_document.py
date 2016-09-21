#encoding=utf-8

import sys
import jieba
import jieba.posseg
import jieba.analyse
import math
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from sklearn import metrics
import codecs
import chardet
import train_model

def load_word_dict(dict_file):
	word_dic = {}
	fin = open(dict_file, "rb")
	for line in fin:
		line = line.strip("\n\r\t ")
		fields = line.split("\t", 1)
		word_dic[fields[0].decode("utf-8")] = len(word_dic)
	fin.close()
	return word_dic


def predict(content, feature_word_dict, model):
	rows, cols, vals = train_model.vectorize_doc(0, content, feature_word_dict)
	if len(rows) > 0:
		pred = model.predict(csr_matrix((vals, (rows, cols)), shape=(1, len(feature_word_dict))))
		return pred
	else:
		return None

if __name__ == "__main__":
	word_dic = load_word_dict(sys.argv[1])
	clf = joblib.load(sys.argv[2])

	#content = u"所有的中超球队，全部出局，这说明什么？"
	#pred = predict(content, word_dic, clf)
	#print pred[0]

	preds = []
	labels = []
	cnt = 0
	fin = open("test.dat", "rb")
	for line in fin:
		#line = line.decode("utf-8")
		line = line.strip("\n\r\t ")
		fields = line.split("\t", 1)
		cate = fields[0]
		content = fields[1].decode("utf-8")
		pred = predict(content, word_dic, clf)
		if pred is None:
			continue
		preds.append(pred)
		labels.append(cate)
		cnt += 1
		if cnt > 1000000000:
			break
	fin.close()
	train_model.calculate_result(labels, preds)
