# -*- coding:utf8 -*-
import urllib2
import json
import os,sys
import re
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
ROOTDIR = os.path.join(os.path.dirname(__file__), os.pardir)
# sys.path.append(os.path.join(ROOTDIR, "lib"))
# 设置模型文件的路径
MODELDIR=os.path.join(ROOTDIR, "ltp_data")

path = os.path.abspath(os.path.dirname(sys.argv[0]))
path_property = open(path+"/car_entity_property.txt",'r')
path_sentiment = open(path+"/car_sentiment_dic.txt",'r')
path_degree = open(path+"/car_degree_dic.txt",'r')
path_out1 = open(path+"/shuchu_pro_sen.txt",'w')
path_out2 = open(path+"/shuchu_sen_deg.txt",'w')
path_corpus = open(path+"/car_review_split_unique.txt",'r')
print "ok"
#属性词
def fun_property_set(path):
    property_set = []
    for line in path.readlines():
        property_set.append((line.strip().split('\t')[0]))
    return property_set

#程度词
def fun_degree_set(path):
    degree_set = []
    for line in path.readlines():
        degree_set.append((line.strip().split('\t')[0]))
    return degree_set

#情感词
def fun_emotion_set(path):
    emotion_set = []
    for line in path.readlines():
        emotion_set.append((line.strip().split('\t')[0]))
    return emotion_set

#读取语料
def read_corpus(path):
    aa = 0
    corpus = []
    while aa< 100000:
        # line = path.readline().strip().split('\001')[1]
        line = path.readline().strip()
        if line not in corpus:
            corpus.append(line)
        else:
            pass
        aa+=1
    path.close()
    return corpus

#分析每行
def parse1(line):
    if len(line) > 1:
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
        api_key = 'z4I4d0X6YULu7XljSjhQbSgCXI8fry7YyQ2n2soH'
        text = re.sub('\s','。',line)
        format = 'json'
        pattern = 'all'
        result = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s" % (url_get_base,api_key,text,format,pattern))
        content = result.read().strip()
        return json.loads(content)[0]
    else:
        aa= []
        return aa


segmentor = Segmentor()
segmentor.load_with_lexicon(os.path.join(MODELDIR,"cws.model"),"/data0/dm/dict/dict.txt")
postagger = Postagger()
postagger.load(os.path.join(MODELDIR, "pos.model"))
parser = Parser()
parser.load(os.path.join(MODELDIR, "parser.model"))
print 'ok2'


#分析每句
def callLTP(sentence):
    words = segmentor.segment(sentence)
    postags = postagger.postag(words)
    arcs = parser.parse(words, postags)
    resultJson=[]
    for index in range(len(words)):
        resultJson.append({'id':index,'cont':words[index],'pos':postags[index],'relate':arcs[index].relation,'parent':arcs[index].head - 1})
    return resultJson

#分析每行，调用callLTP
def parse(line):
    line_parse = []
    line = re.sub('【|】',' ',line)
    line  = re.sub('！|。|#|\?|？|!|；|;', ' ', line)
    #line  = re.sub('！|。|#|？|\?|!|；|;|.', ' ', line)
    line  = re.sub('[\s]+', '。',line)
    line_split = line.split('。')
    for sentence_one in line_split:
        if len(sentence_one) > 5 and len(sentence_one) < 300:
            sentence_parse = callLTP(sentence_one)
            line_parse.append(sentence_parse)
    return line_parse

#输出每个词的句法path
def digui(parse_sentence,parse_word,patten):
    kk = 0
    while kk<10:
        patten.append(parse_word["id"]),patten.append(parse_word["relate"])
        if parse_word["parent"] == -1:
            break
        else:
            parse_word = parse_sentence[parse_word["parent"]]
            kk+=1
    return patten

#组合给定的两个句子path,path为不同类型词的路径
def path_zuhe3(path1,path2,location_sen):
    path_after_zuhe = []
    if abs(path1[0]-path2[0]) > 30:
        return path_after_zuhe
    else:
        print "chuli_zuhe_3:"
        print path1,path2
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2] and sum([k1,k2]) > 2:
                path_after_zuhe = path1[:k1+1]
                nixu = path2[:k2][::-1]
                path_after_zuhe.extend(nixu)
                break
            elif path1[k1] == path2[k2] and sum([k1,k2]) < 3:
                if k1 > k2 and path1[k1+2] in location_sen:
                    path_after_zuhe = path1[:k1+3]
                elif k1 < k2 and path2[k2+2] in location_sen:
                    path_after_zuhe = path2[:k2+3]
                else:
                    pass
                break
            elif len(path1)-k1 > len(path2)-k2:
                k1 += 2
            elif len(path1)-k1 < len(path2)-k2:
                k2 += 2
            else:
                k1 += 2
                k2 += 2
        return path_after_zuhe

#组合给定的两个句子path,path为不同类型词的路径
def path_zuhe2(path1,path2):
    path_after_zuhe = []
    if abs(path1[0]-path2[0]) > 30:
        return path_after_zuhe
    else:
        # print path1,path2
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2] :
                path_after_zuhe = path1[:k1+1]
                nixu = path2[:k2][::-1]
                path_after_zuhe.extend(nixu)
                break
            elif len(path1)-k1 > len(path2)-k2:
                k1 += 2
            elif len(path1)-k1 < len(path2)-k2:
                k2 += 2
            else:
                k1 += 2
                k2 += 2
    return path_after_zuhe

def path_zishai(paths):
    paths_new = paths
    if len(paths) < 2:
        pass
    else:
        for index,path_one in enumerate(paths):
            if len(paths[index+1:]) > 0:
                for path_two in paths[index+1:]:
                    if len(path_one) > len(path_two) and path_two in paths_new and path_two == path_one[-len(path_two):]:
                        paths_new.remove(path_two)
                    elif len(path_one) < len(path_two) and path_one in paths_new and  path_one == path_two[-len(path_one):]:
                        paths_new.remove(path_one)
                    else:
                        pass
            else:
                pass
    return paths_new

#属性词到情感词路径
def parse_sen_pro(sentence_pro,sentence_sen):
    path_sen_pro = []
    if len(sentence_sen) > 0 and len(sentence_pro) > 0:
        for path3_pro in sentence_pro:
            for path3_sen in sentence_sen:
                path_zuhe3_after = path_zuhe2(path3_pro,path3_sen)
                if path_zuhe3_after:
                    path_sen_pro.append(path_zuhe3_after)
                else:
                    pass
    else:
        pass
    return path_sen_pro

#情感词到程度词路径
def parse_sen_deg(sentence_sen,sentence_deg):
    path_sen_deg = []
    if len(sentence_sen) > 0 and len(sentence_deg) > 0:
        for path1_sen in sentence_sen:
            for path1_deg in sentence_deg:
                path_zuhe1_after = path_zuhe2(path1_sen,path1_deg)
                if path_zuhe1_after:
                    path_sen_deg.append(path_zuhe1_after)
                else:
                    pass
    else:
        pass
    return path_sen_deg

#筛选句法结构、词性的模板
def select_patten(property_list,sentiment_list,degree_list,parse_sentence):
    sentence_pro = []
    sentence_sen = []
    sentence_deg = []
    for parse_word in parse_sentence:
        patten=[]
        if parse_word['cont'] in property_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_pro.append(patten)
        elif parse_word['cont'] in sentiment_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_sen.append(patten)
        elif parse_word['cont'] in degree_list:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_deg.append(patten)
        else:
            pass
    return sentence_pro,sentence_sen,sentence_deg

if __name__ == '__main__':
    property_list = fun_property_set(path_property)
    sentiment_list = fun_emotion_set(path_sentiment)
    degree_list = fun_degree_set(path_degree)
    corpus = read_corpus(path_corpus)
    patten_1 = []
    patten_2 = []
    for next,line in enumerate(corpus):
        print next,':',line
        parse_line = parse(line)
        for parse_sentence in parse_line:
            juzi_pro,juzi_sen,juzi_deg = select_patten(property_list,sentiment_list,degree_list,parse_sentence)
            # juzi_pro = path_zishai(juzi_pro)
            # juzi_sen = path_zishai(juzi_sen)
            # juzi_deg = path_zishai(juzi_deg)
            path_sen_pro = parse_sen_deg(juzi_pro,juzi_sen)
            path_sen_deg = parse_sen_deg(juzi_sen,juzi_deg)
            for path_sen_pro_one in path_sen_pro:
                for index1,element_1 in enumerate(path_sen_pro_one):
                    if isinstance(element_1,int):
                        path_sen_pro_one[index1] = parse_sentence[element_1]['pos']
                patten_1.append(path_sen_pro_one)
                s1 = '\t'.join(path_sen_pro_one)
                path_out1.write(s1+'\n')
            for path_sen_deg_one in path_sen_deg:
                for index2,element_2 in enumerate(path_sen_deg_one):
                    if isinstance(element_2,int):
                        path_sen_deg_one[index2] = parse_sentence[element_2]['pos']
                patten_2.append(path_sen_deg_one)
                s2 = '\t'.join(path_sen_deg_one)
                path_out2.write(s2+'\n')
    print "path_sen_pro:",patten_1
    print "path_sen_deg:",patten_2
    path_out1.close()
    path_out2.close()
