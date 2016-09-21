#encoding=utf-8

import sys
import jieba
import jieba.posseg
import jieba.analyse
import random
import chardet

g_kw_cate_list = [("auto." , "汽车"), ( "business." , "财经"), ( "finance." , "财经"), ( "money." , "财经"), ( "//it." , "IT"), ( "tech." , "IT"), ( "/it/" , "IT"), ( "health." , "健康"), ( ".kangq." , "健康"), ( "/health/" , "健康"), ( "sports." , "体育"), ( "/sports/" , "体育"), ( "travel." , "旅游"), ( "tour." , "旅游"), ( "/travel/" , "旅游"), ( "learning." , "教育"), ( "edu." , "教育"), ( "career." , "教育"), ( "//cul." , "文化"), ( "//culture." , "文化"), ( "//mil." , "军事"), ( "//war." , "军事"), ( "/mil/" , "军事"), ( "shehuixinwen." , "社会"), ( "society" , "社会"), ( "/shehui/" , "社会"), ( "guoneixinwen." , "国内"), ( "china" , "国内"), ( "/domestic/" , "国内"), ( "guojixinwen." , "国际"), ( "/world/" , "国际"), ( "house." , "房产"), ( "yule." , "娱乐"), ( "//ent." , "娱乐"), ( "media." , "传媒"), ( "/media/" , "传媒"), ( "gongyi." , "公益"), ( "women." , "时尚"), ( "eladies." , "时尚"), ( "//lady.", "时尚"), ( "//luxury." , "时尚"), ( "//fashion." , "时尚")]

def detect_category_from_url(url):
	for kw, cate in g_kw_cate_list:
		if url.find(kw) >= 0:
			return cate
	return None

def split_data(file_name, train_file, test_file):
	#lst = []
	selected_cates = set(["娱乐", "体育", "财经", "IT", "汽车", "教育", "健康"])
	ftrain = open(train_file, "wb")
	ftest = open(test_file, "wb")
	fin = open(file_name, "rb")
	url = None
	title = None
	content = None
	for line in fin:
		line = line.decode("gb2312", "ignore").encode("utf-8")
		line = line.strip("\n\r\t ")
		if line[0 : 5] == "<url>":
			url = line[5 : len(line) - 6]
		elif line[0 : 9] == "<content>":
			content = line[9 : len(line) - 10]
		elif line[0 : 5] == "<doc>":
			if url is not None and title is not None and content is not None:
				cate = detect_category_from_url(url)
				#print None if cate is None else cate.encode("gb2312"), url
				#lst.append((cate, 1))  #, content))
				if cate in selected_cates:
					#print type(cate), chardet.detect(cate), type(title), chardet.detect(title)
					if random.random() < 0.8:
						print >> ftrain, "%s\t%s"%(cate, title)
					else:
						print >> ftest, "%s\t%s"%(cate, title)
			url = None
			title = None
			content = None
		elif line[0 : 14] == "<contenttitle>":
			title = line[14 : len(line) - 15]
		else:
			pass
	fin.close()
	ftrain.close()
	ftest.close()
	#return lst

if __name__ == "__main__":
	samples = split_data(sys.argv[1], sys.argv[2], sys.argv[3])
	#dic = {}
	#for cate, url in samples:
	#	if not dic.has_key(cate):
	#		dic[cate] = 0
	#	dic[cate] += 1
	#for k, v in dic.items():
	#	print k, v
