__author__ = 'syj'
import os
import sys
path = os.path.abspath(os.path.dirname(sys.argv[0]))
from collections import Counter
#from operator import 
path_in1 = open(path+"/shuchu_pro_sen_pmi.txt",'r')
path_in2 = open(path+"/shuchu_sen_deg_pmi.txt",'r')

path_out1 = open(path+"/count_pro_sen_pmi.txt",'w')
path_out2 = open(path+"/count_sen_deg_pmi.txt",'w')

def read_model(path):
    aa = path.read().strip().split('\n')
    return aa

def write_counter(module,path):
    module_list = []
    for kk in module.keys():
        module_list.append((kk,module[kk]))
    aa = sorted(module_list,key = lambda x:x[1],reverse = True)
    for key in aa:
        path.write(str(key[1])+'\t'+key[0]+'\n')
    path.close()


if __name__  == "__main__":
    module1 = Counter(read_model(path_in1))
    module2 = Counter(read_model(path_in2))
    write_counter(module1,path_out1)
    write_counter(module2,path_out2)
