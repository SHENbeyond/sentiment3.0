#coding:utf8
import urllib2
import json
import os,sys
import re
import copy
from pyltp import Segmentor, Postagger, Parser
ROOTDIR = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.append(os.path.join(ROOTDIR, "lib"))
MODELDIR=os.path.join(ROOTDIR, "ltp_data")

path = os.path.abspath(os.path.dirname(sys.argv[0]))
print path

path_corpus = open(path+"/match_result_all_V2_sentence.txt",'r')
path_model1 = open(path+"/count_pro_sen_pmi.txt",'r')
# path_model2 = open(path+"/count_sen_deg.txt",'r')

path_property = open(path+"/car_entity_property.txt",'r')
path_sentiment = open(path+"/car_sentiment_dic.txt",'r')
path_degree = open(path+"/car_degree_dic.txt",'r')

path_out = open(path+'/jieguo3_long_70_new1_pmi.txt','w')
# path_corpus = open("/data0/shenyanjun/lexicon/car_review_split.txt")

#读取模板
def read_model(path,n):
    path_lab = []
    canditate_pro = []
    canditate_sen = []
    aa = 0
    while aa < n:
        print aa
        line_list = path.readline().strip().split('\t')
        if len(line_list) > 3 and len(line_list)<7:
            path_lab.append(line_list[1:])
            canditate_pro.append(line_list[1])
            canditate_sen.append(line_list[-1])
        else:
            pass
        aa+=1
    return path_lab,list(set(canditate_pro)),list(set(canditate_sen))

#属性词\程度词\情感词
def fun_dic_set(path):
    property_set = []
    for line in path.readlines():
        property_set.append((line.strip().split('\t')[0]))
    return property_set

#读取语料
def read_corpus(path):
    aa = 0
    corpus = []
    while aa < 100:
        line = path.readline().strip().split('\001')
        if len(line)>1 and line[1] and line[1] not in corpus:
            corpus.append(line[1])
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
    # print content
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
    # line  = re.sub('！|。|#|\?|？|!|；|;|，|,', ' ', line) #short sentence
    line  = re.sub('！|。|#|\?|？|!|；|;|【|】', ' ', line) #long sentence
    #line = re.sub(',')
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
        k1 = 0
        k2 = 0
        while max(k1,k2) < max(len(path1),len(path2)):
            if path1[k1] == path2[k2] and sum([k1,k2]) > 2:
                path_after_zuhe = path2[:k2+1]
                nixu = path1[:k1][::-1]
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
        k1 = 0
        k2 = 0
        while max(k1, k2) < max(len(path1), len(path2)):
            if path1[k1] == path2[k2]:
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

def find_all_index(arr,item):
    return [i for i,a in enumerate(arr) if a == item]

# def rule_abab(paths):
#     if len(paths)>3:
#         first = []
#         last = []
#         for path in paths:
#             first.append(path[0])
#             last.append(path[-1])
#这种情况先放着在调整

def guize_check(sentence_pro,sentence_sen):
    path_sen_pro = []
    if len(sentence_pro) > 0 and len(sentence_sen) > 0:
        for path2_pro in sentence_pro:
            for path2_sen in sentence_sen:
                path_zuhe2_after = path_zuhe2(path2_pro,path2_sen)
                if path_zuhe2_after:
                    path_sen_pro.append(path_zuhe2_after)
    else:
        pass
    return path_sen_pro

#筛选句法结构、词性的模板
def select_patten(parse_sentence,canditate_pro,canditate_sen):
    sentence_pro = []
    sentence_sen = []
    canditate_pro_sen = list(set(canditate_pro).intersection(set(canditate_sen)))
    for parse_word in parse_sentence:
        patten=[]
        if parse_word['pos'] in canditate_pro_sen:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_pro.append(patten)
            sentence_sen.append(patten)
        elif parse_word['pos'] in canditate_pro:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_pro.append(patten)
        elif parse_word['pos'] in canditate_sen:
            patten = digui(parse_sentence,parse_word,patten)
            sentence_sen.append(patten)
        else:
            pass
    location_sen = [kk[0] for kk in sentence_sen]
    location_pro = [jj[0] for jj in sentence_pro]
    return sentence_pro, sentence_sen, location_sen, location_pro

def check_out(path_X,model_X,parse_sentence,path):
    sentence_path_x = []
    for path_one in path_X:
        path_x_one = []
        path_one_copy = copy.deepcopy(path_one)
        for index1,element_1 in enumerate(path_one):
            if isinstance(element_1,int):
                path_one[index1] = parse_sentence[element_1]['pos']

        if path_one in model_X:
            print path_one
            path.write('\t\t'+'\t'.join(path_one)+'\n')
            path_x_one.append(parse_sentence[path_one_copy[0]]['cont'])
            path_x_one.append(parse_sentence[path_one_copy[-1]]['cont'])
        if path_x_one:
            sentence_path_x.append(path_x_one)
    return sentence_path_x

if __name__ == '__main__':
    model_1,canditate_pro,canditate_sen = read_model(path_model1,70)
    # model_2,aa_sen,bb_deg= read_model(path_model2,70)
    print "model has been read!"
    canditate_sen = ['a','i']
    property_list = fun_dic_set(path_property)
    sentiment_list = fun_dic_set(path_sentiment)
    degree_list = fun_dic_set(path_degree)
    print "dict has been read!"

    corpus = read_corpus(path_corpus)
    print "corpus ok!"
    patten_1 = []
    patten_2 = []
    patten_3 = []
    jieguo_count = 0
    for aa,line in enumerate(corpus):
        print aa
        parse_line = parse(line.strip())
        path_line_out = []
        for parse_sentence in parse_line:
            path_sentence_out = []
            juzi_pro,juzi_sen,location_sen,location_pro = select_patten(parse_sentence, canditate_pro, canditate_sen)

            path_pro_sen = guize_check(juzi_pro,juzi_sen)
            path_1_out = check_out(path_pro_sen,model_1,parse_sentence,path_out)
            if path_1_out and path_1_out not in path_sentence_out:
                path_sentence_out.extend(path_1_out)
            # if path_2_out and path_2_out not in path_sentence_out:
            #     path_sentence_out.extend(path_2_out)

            if path_sentence_out:
                path_line_out.extend(path_sentence_out)
        if path_line_out:
            path_out.write(line+'\n')
            print line
            jieguo_count += 1

            print '----result------'
            path_out.write('\n')
            for hh in path_line_out:
                print  '\t'.join(hh)
                path_out.write('\t\t')
                path_out.write('\t'.join(hh)+'\n')
            print '\n'
            path_out.write('\n')
    print 'jieguo_count:',jieguo_count
    path_out.write("call_back:"+str(jieguo_count))
    path_model1.close()
    # path_model2.close()
    path_property.close()
    path_sentiment.close()
    path_degree.close()
    path_out.close()
