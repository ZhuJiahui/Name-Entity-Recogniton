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


    
def INITFeatureDictionary(Word):
    '''For every Word the Feature Values stored eg FeatureDict['Vibration'].[0,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1]'''
    global FeatureDict
    Feature=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    '''Feature=['Word','0Noun','1Verb','2TitleNoun','3TitleVerb','4Prep-Det-Noun','5Prep-Det-Adj-Noun',
    '6Adj-Noun','7Det-Noun','8HeadVerb','9VerbSubSequence','10EndingwithED','11EndingwithION','12EndingwithING'
    ,'13EndingwithS','14EndingwithAGE','15WordNet','16Adjectives','FailureMode']
    '''
    for Feat in Feature:
        FeatureDict.setdefault(Word,[]).append(Feat)


def LocateFiles():
    '''Locates the XML flies in the Directory specified as the System Argument'''
    try:
        root=sys.argv[1]
        
        ListOfFiles=glob.glob(str(root)+'\\\*')
        return ListOfFiles
    except :
        print '''Please Input the Directory Name Where the Tagged Corpus is Present'''

    return None        
    

def POSTaggedFileReader():
  '''Reads the POS tagged Files'''
  
  for file in LocateFiles():
        files=open(file,'r').readlines()
        print file
        Title=files[0]
        
        if Title:
            Title=ConvertTitleToNLTK(Title)
            TitleParsing(Title)
        files=files[1:]
        ConvertToNLTK(files)
    

def ConvertToNLTK(Lines):
       '''Converts the POS tags turbine/NN to tuple ('turbine','NN')'''
       
       for line in Lines:
            WordTagsList=[]
            line=line.strip()
            WordTags=line.split(' ')
            for word in WordTags:
                temp=tuple(word.split('/'))
                WordTagsList.append(temp)
            Chunker(WordTagsList)

            
def ConvertTitleToNLTK(Lines):
      '''Converts the POS tags turbine/NN to tuple ('turbine','NN')'''
      
      WordTagsList=[]
      Lines=Lines.strip()
      WordTags=Lines.split(' ')
      for word in WordTags:
         temp=tuple(word.split('/'))
         WordTagsList.append(temp)
      return WordTagsList   
                            
         
def Grammar():
    '''Regex Grammar for Chunking '''
    
    global FeatureDict
    grammar = r"""
 NP: {<DT|JJ|NNS|NN>+}          # Chunk sequences of DT, JJ, NN
 PP: {<IN><NP>}               # Chunk prepositions followed by NP
 VP: {<VB.*><NP|PP|CLAUSE>+} # Chunk verbs and their arguments
 CLAUSE: {<NP><VP>}  # Chunk NP, VP
 """
    Parser=nltk.RegexpParser(grammar)
    return Parser

def TempGrammar():
    
    global FeatureDict
    grammar = r"""
 Failure: {<NNS|NN|NNP><VB.*>+}          # Chunk sequences of DT, JJ, NN
 """
    Parser=nltk.RegexpParser(grammar)
    return Parser

def Chunker(WordTags):
           '''Chunking of the Sentences after POS tagging'''
           
           
           Parser=Grammar()
           try: 
                         Parsed=Parser.parse(WordTags)
                         VerbNounFilter(Parsed)
                         PrepositionPhrase(Parsed)
                         NounPhrase(Parsed)
                         NounOrVerb(WordTags)
                         VerbSubSequence(WordTags)
                         EndingWords(WordTags)
                         Adjectives(WordTags)
                         
                         
                         
           except:
                         print 'No Parsing Possible'
                         pass


def TitleParsing(TitleChunked):
    '''Feature to Detect the Word is Noun or Verb in Title'''
    
    global StopList
    global FeatureDict
    TitleNoun=[]
    TitleVerb=[]
    try:
        
        for Title in TitleChunked:
            if Title[1]=='NN' or Title[1]=='NNS':
                    TitleNoun.append(Title[0])
            temp=re.match(r'VB.',str(Title[1]))
            if temp:
                TitleVerb.append(Title[0])
        '''-------------------------------------Feature 2-------------------------------------------------------'''
        for N in TitleNoun:
              N=N.lower()
              if N.isalpha():
               if N not in StopList:    
                    if N in FeatureDict:
                        FeatureDict[str(N)][2]=1
                        
                    else:
                        INITFeatureDictionary(str(N))            
                        FeatureDict[str(N)][2]=1
        '''-------------------------------------Feature 3---------------------------------------------------------'''            
        for V in TitleVerb:
              V=V.lower()
              if V.isalpha():
               if V not in StopList:
                    if V in FeatureDict:
                        FeatureDict[str(V)][3]=1
                    else:
                        INITFeatureDictionary(str(V))            
                        FeatureDict[str(V)][3]=1    
                                           
                                      
    except:
              raise





def VerbSubSequence(PreChunked):
    '''Feature checks the LAST verb in the consecutive sequence of Verbs'''
    
    global StopList
    global FeatureDict
    grammar='''Verb:{<VB.?>+}'''
    Parser=nltk.RegexpParser(grammar)
    Parsed=Parser.parse(PreChunked)
    '''---------------------------Feature 9------------------------------------------'''
    for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'Verb'):
        List=[]
        if len(subtree.leaves())>1:
            List=subtree.leaves()
            Verb=List[-1][0]
            Verb=Verb.lstrip()
            Verb=Verb.rstrip()
            Verb=Verb.lower()
            if Verb not in StopList:
                if Verb in FeatureDict:
                    FeatureDict[str(Verb)][9]=1
                else:
                    INITFeatureDictionary(str(Verb))
                    FeatureDict[str(Verb)][9]=1
            
               

def PrepositionPhrase(Parsed):
    '''Feature Checks the Below(immediate below) patterns in the chunked Prepositional Phrases'''
    
    Pattern1=['IN','DT','NN']
    Pattern2=['IN','DT','NNS']
    Pattern3=['IN','DT','JJ','NN',]
    Pattern4=['IN','DT','JJ','NNS']
    TagComparator=[]
    global FeatureDict
    global StopList
    for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'PP'):
       WordsComparator=[]
       TagComparator=[]
       for tags in subtree.leaves():
           tag=tags[1].rstrip()
           tag=tag.lstrip()
           word=tags[0].rstrip()
           word=word.lstrip()
           TagComparator.append(tag)
           WordsComparator.append(word)
       TagComparator1=TagComparator[:3]
       TagComparator2=TagComparator[:4]
       '''----------------------------------------------------------------Feature 5---------------------------------------------------------------------------------'''
       if TagComparator2==Pattern3 or TagComparator2==Pattern4:
           if WordsComparator[3].lower() not in StopList:
               
               if WordsComparator[3].lower() in FeatureDict:
                   FeatureDict[str(WordsComparator[3].lower())][5]=1
               else:
                   INITFeatureDictionary(str(WordsComparator[3].lower()))
                   FeatureDict[str(WordsComparator[3].lower())][5]=1
       '''----------------------------------------------------------------Feature 4---------------------------------------------------------------------------------'''    
       if TagComparator1==Pattern1 or TagComparator1==Pattern2:
           if WordsComparator[2].lower() not in StopList:
                   if WordsComparator[2].lower() in FeatureDict:
                       FeatureDict[str(WordsComparator[2].lower())][4]=1
                   else:
                       INITFeatureDictionary(str(WordsComparator[2].lower()))
                       FeatureDict[str(WordsComparator[2].lower())][4]=1
     
def VerbNounFilter(Parsed):
     '''Feature for detection of the Head Verb'''
     
     global StopList
     global FeatureDict
     Verb=[]
     Noun=[]
     StopList=StopList
     RemoveNPTags=re.compile(r'\(|\)|\'')
     for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'VP'):
         RemoveExtraTags=re.compile(r'NP|PP|VP|\-\>|\(|\)|\'')
         for NounsVerbs in subtree.productions():
               VerbPhrase=re.findall(r'VP.*',str(NounsVerbs))
               for phrase in VerbPhrase:
                    phrase=re.sub(RemoveExtraTags,'',str(phrase))
                    tempVerb=re.split(',',phrase)[0]
                    tempVerb=tempVerb.lstrip()
                    if tempVerb.isalpha():
                        if str(tempVerb) not in StopList:
                            Verb.append(str(tempVerb))
         '''--------------------------Feature 8-----------------------------'''                   
         if len(Verb)>0:
            for v in Verb:
                v=v.lower()
                if v.isalpha():
                 if v not in StopList:      
                   if v in FeatureDict:
                        FeatureDict[str(v)][8]=1
                   else:
                        INITFeatureDictionary(str(v))
                        FeatureDict[str(v)][8]=1 

def NounPhrase(Parsed):
    '''Feature Checks the Below(immediate below) patterns in the chunked Noun Phrases'''
    
    Pattern1=['JJ','NNS']
    Pattern2=['JJ','NN']
    Pattern3=['DT','NN']
    Pattern4=['DT','NNS']
    TagComparator=[]
   
    global StopList       
    global FeatureDict
    
    for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'NP'):
       WordsComparator=[]
       TagComparator=[]
       for tags in subtree.leaves():
           
           tag=tags[1].rstrip()
           tag=tag.lstrip()
           word=tags[0].rstrip()
           word=word.lstrip()
           TagComparator.append(tag)
           WordsComparator.append(word)
       '''----------------------------------------------------------------Feature 6---------------------------------------------------------------------------------'''
       for tag in range(len(TagComparator)):
           if TagComparator[tag]==Pattern1[0]:
               try:
                   if TagComparator[tag+1]==Pattern1[1] or TagComparator[tag+1]==Pattern2[1]:
                      if WordsComparator[tag+1].isalpha():  
                       if WordsComparator[tag+1].lower() not in StopList:
                                if WordsComparator[tag+1].lower() in FeatureDict:
                                        FeatureDict[str(WordsComparator[tag+1].lower())][6]=1
                                else:
                                        INITFeatureDictionary(str(WordsComparator[tag+1].lower()))
                                        FeatureDict[str(WordsComparator[tag+1].lower())][6]=1
               except:
                   pass
       '''----------------------------------------------------------------Feature 7---------------------------------------------------------------------------------'''               
       for tag in range(len(TagComparator)):
           if TagComparator[tag]==Pattern3[0]:
               try:
                   if TagComparator[tag+1]==Pattern3[1] or TagComparator[tag+1]==Pattern4[1]:
                     if WordsComparator[tag+1].isalpha(): 
                       if WordsComparator[tag+1].lower() not in StopList:
                                   if WordsComparator[tag+1].lower() in FeatureDict:
                                        FeatureDict[str(WordsComparator[tag+1].lower())][7]=1
                                   else:
                                        INITFeatureDictionary(str(WordsComparator[tag+1].lower()))
                                        FeatureDict[str(WordsComparator[tag+1].lower())][7]=1
               except:
                   pass
       
def Adjectives(Chunked):
        '''Feature to check if the word is Adjective JJ,JJS,JJR'''
        
        global FeatureDict
        global StopList
        Adjective=[]
        
        '''---------------------------------------------------------------Feature 16----------------------------------------------------------'''
        for word in Chunked:
            W=re.match(r'JJ.?',str(word[1]))
            if W:
                    Adjective.append(word[0])
        for J in Adjective:
          J=J.lower()
          
          if J.isalpha():
           if J not in StopList:  
                if J in FeatureDict:
                    FeatureDict[str(J)][16]=1
                else:
                    INITFeatureDictionary(J)
                    FeatureDict[J][16]=1   
      
def NounOrVerb(Chunked):
        '''Simplest of all the Features-Checks whether the Word is Noun or a Verb'''
        
        global FeatureDict
        global StopList
        Noun=[]
        Verb=[]
        '''---------------------------------------------------------------Feature 0----------------------------------------------------------'''
        for word in Chunked:
            W=re.match(r'NN.?',str(word[1]))
            if W:
                    Noun.append(word[0])
        for N in Noun:
          N=N.lower()
          
          if N.isalpha():
           if N not in StopList:  
                if N in FeatureDict:
                    FeatureDict[str(N)][0]=1
                else:
                    INITFeatureDictionary(N)
                    FeatureDict[N][0]=1            
        '''---------------------------------------------------------------Feature 1----------------------------------------------------------'''
        for word in Chunked:
           V=re.match(r'VB.?',str(word[1]))
           if V:
                      Verb.append(word[0])
        for V in Verb:
          V=V.lower()
          if V.isalpha():
           if V not in StopList:  
                if V in FeatureDict:
                    FeatureDict[str(V)][1]=1
                else:
                    INITFeatureDictionary(str(V))            
                    FeatureDict[str(V)][1]=1                         


def WordsOnly(WordTags):
    '''Read the Words from the Word/Tag tuple'''
    
    global StopList
    List=[]
    for words in WordTags:
        List.append(words[0])
    return List

def EndingWords(WordTags):
    '''Feature : Words Ending with ED,ION,ING,S,AGE'''   
    '''-------------------------------Feature 10 to 14 -----------------------------------'''
    global FeatureDict
    global StopList
    Words=WordsOnly(WordTags)
    for wrd in Words:
       if wrd.isalpha():
         wrd=wrd.lower()  
         if wrd[-2:]=='ed':
                if wrd not in StopList:
                    if wrd in FeatureDict:
                        FeatureDict[str(wrd)][10]=1
                    else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][10]=1
         if wrd[-3:]=='ion':
                if wrd not in StopList:
                    if wrd in FeatureDict:
                        FeatureDict[str(wrd)][11]=1
                    else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][11]=1
         if wrd[-3:]=='ing':
                if wrd not in StopList:
                    if wrd in FeatureDict:
                        FeatureDict[str(wrd)][12]=1
                    else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][12]=1
         if wrd[-1:]=='s':
                if wrd not in StopList:
                    if wrd in FeatureDict:
                        FeatureDict[str(wrd)][13]=1
                    else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][13]=1             
                        
         if wrd[-3:]=='age':
                if wrd not in StopList:
                    if wrd in FeatureDict:
                        FeatureDict[str(wrd)][14]=1
                    else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][14]=1

def FilteringBeforeWriting():
    '''Remove the Unwanted Words '''
    global FeatureDict
    global StopList
    for word in FeatureDict.keys():
      if FeatureDict[word][0]==1:  
        if FeatureDict[word][1:]==[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
           del FeatureDict[word]
              
    

                                             
def ArffFileWriter():
    '''Arff File Writer'''
    
    global FeatureDict
    global StopList
    FileName=open('C:\\Python26\\GESearch\\Stanford_FeatureDetection_3rdAugust.arff','w')
    FileName.write('@relation FeatureDetection'+'\n')
    FileName.write('@attribute Word string'+'\n')
    FileName.write('@attribute Noun {0,1}'+'\n')                    
    FileName.write('@attribute Verb {0,1}'+'\n')
    FileName.write('@attribute TitleNoun {0,1}'+'\n')
    FileName.write('@attribute TitleVerb {0,1}'+'\n')
    FileName.write('@attribute Prep-Det-Noun {0,1}'+'\n')
    FileName.write('@attribute Prep-Det-Adj-Noun {0,1}'+'\n')
    FileName.write('@attribute Adj-Noun {0,1}'+'\n')
    FileName.write('@attribute Det-Noun {0,1}'+'\n')
    FileName.write('@attribute HeadVerb {0,1}'+'\n')
    FileName.write('@attribute VerbSubSequence {0,1}'+'\n')
    FileName.write('@attribute EndingED {0,1}'+'\n')
    FileName.write('@attribute EndingION {0,1}'+'\n')
    FileName.write('@attribute EndingING {0,1}'+'\n')
    FileName.write('@attribute EndingS {0,1}'+'\n')
    FileName.write('@attribute EndingAGE {0,1}'+'\n')
    FileName.write('@attribute WordNet {0,1}'+'\n')
    FileName.write('@attribute Adjective {0,1}'+'\n')
    FileName.write('@attribute FailureMode {0,1}'+'\n')
    FileName.write('@data'+'\n')
    for Key in FeatureDict:
        FileName.write(Key+','+str(FeatureDict[Key][0])+','+str(FeatureDict[Key][1])+','+str(FeatureDict[Key][2])+','+str(FeatureDict[Key][3])+','+str(FeatureDict[Key][4])+','+str(FeatureDict[Key][5])+','+str(FeatureDict[Key][6])+','+str(FeatureDict[Key][7])+','+str(FeatureDict[Key][8])+','+str(FeatureDict[Key][9])+','+str(FeatureDict[Key][10])+','+str(FeatureDict[Key][11])+','+str(FeatureDict[Key][12])+','+str(FeatureDict[Key][13])+','+str(FeatureDict[Key][14])+','+str(FeatureDict[Key][15])+','+str(FeatureDict[Key][16])+','+'0'+'\n')
                         
    FileName.close()           
     



if __name__=='__main__':
    global FeatureDict
    global StopList
    StopList={}
    StopList=StopWords.StopWordList()
    FeatureDict={}
    POSTaggedFileReader()
    FilteringBeforeWriting()
    ArffFileWriter()
    
    
