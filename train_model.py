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

def detect_category_from_url(url):
	for kw, cate in g_kw_cate_list:
		if url.find(kw) >= 0:
			return cate
	return None

def seg_word(text):
	res = jieba.analyse.extract_tags(text, topK = 30, withWeight = False)
	return set(res)

def word_idx_stat(file_name):
	N = 0
	cate_dict = {}
	word_cate_dict = {}
	fin = open(file_name, "rb")
	for line in fin:
		line = line.strip("\n\r\t ")
		fields = line.split("\t", 1)
		if len(fields) == 2:
			cate = fields[0]
			content = fields[1]
		else:
			continue
		N += 1
		if cate_dict.has_key(cate):
			cate_dict[cate] += 1
		else:
			cate_dict[cate] = 1
		for word in seg_word(content):
			c_dic = word_cate_dict.setdefault(word, {})
			if c_dic.has_key(cate):
				c_dic[cate] += 1
			else:
				c_dic[cate] = 1
	fin.close()
	#fdebug = open("word_idx_calc.log", "wb")
	fdebug = codecs.open("word_idx_calc.log", "wb", "utf-8")
	word_idx_list = []
	h_c = 0.0
	for cate, n in cate_dict.items():
		p_c = float(n) / float(N)
		h_c -= p_c * math.log(p_c)
		#print cate, n
	#print "N", N
	#print "h_c", h_c
	for word, c_dic in word_cate_dict.items():
		chi = 0.0
		h_c_t = 0.0
		h_c_n_t = 0.0
		cnt_t = sum(c_dic.values())
		for cate, tn in cate_dict.items():
			n = c_dic[cate] if c_dic.has_key(cate) else 0
			p_c_t = float(n) / float(cnt_t)
			p_c_n_t = float(tn - n) / float(N - cnt_t)
			#if word == u"楼兰":
			#	print cate, n, cnt_t, p_c_t
			#	print cate, tn - n, N - cnt_t, p_c_n_t
			if n > 0:
				h_c_t += p_c_t * math.log(p_c_t)
			if tn - n > 0:
				h_c_n_t += p_c_n_t * math.log(p_c_n_t)
			np = float(cnt_t) * float(tn) / float(N)
			chi += (n - np) * (n - np) / np
			np = float(N - cnt_t) * float(tn) / float(N)
			chi += (tn - n - np) * (tn - n - np) / np
		p_t = float(cnt_t) / float(N)
		p_n_t = float(N - cnt_t) / float(N)
		#if word == u"楼兰":
		#	print "p_t", p_t
		#	print "h_c_t", h_c_t
		#	print "p_n_t", p_n_t
		#	print "h_c_n_t", h_c_n_t
		ig = h_c + p_t * h_c_t + p_n_t * h_c_n_t
		idf = math.log(float(N) / float(1 + cnt_t))
		icf = math.log(float(len(cate_dict)) / float(len(c_dic))) + 1
		word_idx_list.append((word, ig, chi, idf, icf))
		tmp_s = None
		for cate, n in cate_dict.items():
			if tmp_s is None:
				tmp_s = "%d %d"%(c_dic[cate] if c_dic.has_key(cate) else 0, n)
			else:
				tmp_s += " %d %d"%(c_dic[cate] if c_dic.has_key(cate) else 0, n)
		print >> fdebug, word, tmp_s, ig, chi, idf, icf
	fdebug.close()
	cate_dict = {}
	word_cate_dict = {}
	#sys.exit(0)
	return word_idx_list

def vectorize_doc(doc_no, doc_text, feature_word_dict):
	rows = []
	cols = []
	vals = []
	for word in seg_word(doc_text):
		if feature_word_dict.has_key(word):
			rows.append(doc_no)
			cols.append(feature_word_dict[word])
			vals.append(1.0)
	return (rows, cols, vals)

def train_model(train_data_file, feature_word_dict):
	rows = []
	cols = []
	vals = []
	labels = []
	fin = open(train_data_file, "rb")
	for line in fin:
		line = line.strip("\n\r\t ")
		fields = line.split("\t", 1)
		if len(fields) == 2:
			cate = fields[0]
			content = fields[1]
		else:
			continue
		cur_rows, cur_cols, cur_vals = vectorize_doc(len(labels), content, feature_word_dict)
		if len(cur_rows) > 0:
			rows.extend(cur_rows)
			cols.extend(cur_cols)
			vals.extend(cur_vals)
			labels.append(cate)
	fin.close()
	clf = MultinomialNB(alpha = 0.01)
	clf.fit(csr_matrix((vals, (rows, cols)), shape=(len(labels), len(feature_word_dict))), np.asarray(labels))
	return clf

def calculate_result(actual,pred):  
	m_precision = metrics.precision_score(actual, pred)
	m_recall = metrics.recall_score(actual, pred) 
	print 'predict info:'  
	print 'precision:{0:.3f}'.format(m_precision)  
	print 'recall:{0:0.3f}'.format(m_recall)
	print 'f1-score:{0:.3f}'.format(metrics.f1_score(actual, pred))

def test(test_data_file, feature_word_dict, model):
	rows = []
	cols = []
	vals = []
	labels = []
	fin = open(test_data_file, "rb")
	for line in fin:
		line = line.strip("\n\r\t ")
		fields = line.split("\t", 1)
		if len(fields) == 2:
			cate = fields[0]
			content = fields[1]
		else:
			continue
		cur_rows, cur_cols, cur_vals = vectorize_doc(len(labels), content, feature_word_dict)
		if len(cur_rows) > 0:
			rows.extend(cur_rows)
			cols.extend(cur_cols)
			vals.extend(cur_vals)
			labels.append(cate)
	fin.close()
	pred = clf.predict(csr_matrix((vals, (rows, cols)), shape=(len(labels), len(feature_word_dict))))
	calculate_result(labels, pred)


if __name__ == "__main__":
	word_idx_lst = word_idx_stat(sys.argv[1])
	
	word_idx_lst.sort(key=lambda x:x[1], reverse = True)
	
	selected_word_dic = {}
	#fword = open("word_idx_list.dat", "wb")
	fword = codecs.open("word_idx_list.dat", "w", "utf-8")
	for word, ig, chi, idf, icf in word_idx_lst:
		if len(selected_word_dic) < 15000:
			selected_word_dic[word] = len(selected_word_dic)
			print >> fword, "%s\t%f\t%f\t%f\t%f"%(word, ig, chi, idf, icf)
	fword.close()

	clf = train_model(sys.argv[1], selected_word_dic)

	joblib.dump(clf, "MultinomialNB_for_text_classification.model", compress = 3)

	test(sys.argv[2], selected_word_dic, clf)
