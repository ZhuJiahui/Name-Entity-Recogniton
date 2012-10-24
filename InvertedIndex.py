import nltk,pprint,re,fnmatch,os,sys
from nltk.corpus import wordnet as wn
import operator,math
from os import listdir
from os.path import isfile, join
import itertools,glob
import xml.dom.minidom
from xml.dom.minidom import parseString
import StopWords
from StopWords import *
import csv


class Ddict(dict):
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)


def LocateFiles(taggedfolder):

    try:
        root=taggedfolder
        ListOfFiles=glob.glob(str(root)+'\\\*')
        return ListOfFiles
    except :
        print '''Please Input the Directory Name to read in the Format(Windows): C:\\Python26\\GESearch\\TaggedCorpus'''

    return None        
    

def POSTaggedFileReader(taggedfolder):
  
  
  for file in LocateFiles(taggedfolder):
      
        files=open(file,'r').readlines()
        ConvertToNLTK(files,file)
    

def ConvertToNLTK(Lines,Fname):
       global Index
       for line in Lines:
            WordTagsList=[]
            line=line.strip()
            WordTags=line.split(' ')
            for word in WordTags:
                temp=tuple(word.split('/'))
                WordTagsList.append(temp)
            FillIndex(WordTagsList,Fname)

    

def DocIndex():
    
  global Index
  try:  
    path=os.getcwd()
    path+='\\FeatureWords.txt'
    files=open(path,'r').readlines()
    for f in files:
        word=f.strip()
        Index[str(word)]['NULL']=0
  except:
      print 'Feature Words file not found'
      raise

def FillIndex(LinesRead,FileName):
       global Index
       for Word in LinesRead:
           Word=Word[0].strip()
           Word=Word.lower()
           if Word in Index:
               if FileName in Index[Word]:
                   temp=Index[Word][FileName]
                   temp+=1
                   Index[Word][FileName]=temp
                   
               else:
                   Index[Word][FileName]=1
                   

def WriteIndex():
    global Index
    import os
    try:
        path=os.getcwd()
        path+='\\IndexDocument.txt'
        file=open(path,'w')
        for key1 in Index:
            count=0  
            for key2 in Index[key1]:
                if key2!='NULL':
                    count+=1
            file.write(str(key1)+" "+str(count)+'\n')
    except:
        print 'Error in File Creation '
        raise

                    
               
def main(taggedfolder):
    global Index
    Index=Ddict(dict)
    DocIndex()
    POSTaggedFileReader(taggedfolder)
    WriteIndex()
    
