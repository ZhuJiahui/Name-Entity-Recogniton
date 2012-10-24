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
import InvertedIndex
from InvertedIndex import *




def INITFeatureDictionary(Word):
    
    global FeatureDict
    Feature=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    '''Feature=['Word','0Noun','1Verb','2TitleNoun','3TitleVerb','4Prep-Det-Noun','5Prep-Det-Adj-Noun',
    '6Adj-Noun','7Det-Noun','8HeadVerb','9VerbSubSequence','10EndingwithED','11EndingwithION','12EndingwithING'
    ,'13EndingwithS','14EndingwithAGE','15WordNet','16Adjectives','17Discovered','18Found','19DF','20Freq','FailureMode']
    '''
    for Feat in Feature:
        FeatureDict.setdefault(Word,[]).append(Feat)



def LocateFiles():

    try:
        root=sys.argv[1]
        ListOfFiles=glob.glob(str(root)+'\\\*')
        return ListOfFiles
    except :
        print '''Please Input the Directory Name to read in the Format(Windows): C:\\Python26\\GESearch\\TaggedCorpus'''

    return None        
    

def POSTaggedFileReader():
  global FeatureDict
  global TotalFiles
  FileList=LocateFiles()
  TotalFiles=len(FileList)
  
  for file in FileList :
        print file
        files=open(file,'r').readlines()
        Title=files[0]
        if Title:
            Title=ConvertTitleToNLTK(Title)
            TitleParsing(Title)
        files=files[1:]
        ConvertToNLTK(files)
    

def ConvertToNLTK(Lines):
       for line in Lines:
            WordTagsList=[]
            line=line.strip()
            WordTags=line.split(' ')
            for word in WordTags:
                temp=tuple(word.split('/'))
                WordTagsList.append(temp)
            Chunker(WordTagsList)

            
def ConvertTitleToNLTK(Lines):
      WordTagsList=[]
      Lines=Lines.strip()
      WordTags=Lines.split(' ')
      for word in WordTags:
         temp=tuple(word.split('/'))
         WordTagsList.append(temp)
      return WordTagsList

def Grammar():
  
    grammar = r"""
 NP: {<DT|JJ|NNS|NN>+}          # Chunk sequences of DT, JJ, NN
 PP: {<IN><NP>}               # Chunk prepositions followed by NP
 VP: {<VB.*><NP|PP|CLAUSE>+} # Chunk verbs and their arguments
 CLAUSE: {<NP><VP>}  # Chunk NP, VP
 """
    Parser=nltk.RegexpParser(grammar)
    return Parser


def VBDVBNGrammar():
    '''For the WAS DISCOVERED feature'''
    
    grammar = r"""
 Discovered: {<DT>?<NNS|NN><VBD><VB.?>+}          
 """
    Parser=nltk.RegexpParser(grammar)
    return Parser


def Chunker(WordTags):
           
           Parser=Grammar()
           VbParser=VBDVBNGrammar()
           try: 
                         Parsed=Parser.parse(WordTags)
                         
                         VbParsed=VbParser.parse(WordTags)
                         
                         HeadVerb(Parsed)
                         PrepositionPhrase(Parsed)
                         NounPhrase(Parsed)
                         NounOrVerb(WordTags)
                         VerbSubSequence(WordTags)
                         EndingWords(WordTags)
                         Adjectives(WordTags)
                         Discovered(VbParsed)
                         FrequencyOfWords(WordTags)
                         
                         
           except:
                         print WordTags
                         pass

    
def FrequencyOfWords(WordTags):
    '''Frequency of the Words '''
    
    global WordFrequency
    global StopList
    for words in WordTags:
        words=words[0].strip()
        words=words.lower()
        if words.isalpha():
            if words not in StopList:
               if words in WordFrequency:
                   temp=WordFrequency[words]
                   temp+=1
                   WordFrequency[words]=temp
               else:
                   WordFrequency[words]=1
          

def Adjectives(Chunked):
        global FeatureDict
        global StopList
        Adjective=[]
        
        '''---------------------------------------------------------------Feature 16----------------------------------------------------------'''
        for word in Chunked:
            W=re.match(r'JJ.?',str(word[1]))
            if W:
                    Adjective.append(word[0])
        for J in Adjective:
          J=J.strip()  
          J=J.lower()
          
          if J.isalpha():
           if J not in StopList:  
                if J in FeatureDict:
                    temp=FeatureDict[str(J)][16]
                    temp+=1
                    FeatureDict[str(J)][16]=temp
                else:
                    INITFeatureDictionary(J)
                    FeatureDict[J][16]=1   
      
def NounOrVerb(Chunked):

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
          N=N.strip()  
          N=N.lower()
          
          if N.isalpha():
           if N not in StopList:  
                if N in FeatureDict:
                    temp=FeatureDict[str(N)][0]
                    temp+=1
                    FeatureDict[str(N)][0]=temp
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
          V=V.strip()
          if V.isalpha():
           if V not in StopList:  
                if V in FeatureDict:
                    temp=FeatureDict[str(V)][1]
                    temp+=1
                    FeatureDict[str(V)][1]=temp
                else:
                    INITFeatureDictionary(str(V))            
                    FeatureDict[str(V)][1]=1                         




def TitleParsing(TitleChunked):

    global FeatureDict
    global StopList
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
                        temp=FeatureDict[str(N)][2]
                        temp+=1
                        FeatureDict[str(N)][2]=temp
                        '''temp=FeatureDict[str(N)][0]
                        temp+=1
                        FeatureDict[str(N)][0]=temp'''
                        
                        
                    else:
                        INITFeatureDictionary(str(N))            
                        FeatureDict[str(N)][2]=1
                        #FeatureDict[str(N)][0]=1
        '''-------------------------------------Feature 3---------------------------------------------------------'''            
        for V in TitleVerb:
              V=V.lower()
              if V.isalpha():
               if V not in StopList:
                    if V in FeatureDict:
                        temp=FeatureDict[str(V)][3]
                        temp+=1
                        FeatureDict[str(V)][3]=temp
                        '''temp=FeatureDict[str(V)][1]
                        temp+=1
                        FeatureDict[str(V)][1]=temp'''
                        
                    else:
                        INITFeatureDictionary(str(V))            
                        FeatureDict[str(V)][3]=1    
                        #FeatureDict[str(V)][1]=1                                               
                                      
    except:
              pass

def PrepositionPhrase(Parsed):
    
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
                   temp=FeatureDict[str(WordsComparator[3].lower())][5]
                   temp+=1
                   FeatureDict[str(WordsComparator[3].lower())][5]=temp
               else:
                   INITFeatureDictionary(str(WordsComparator[3].lower()))
                   FeatureDict[str(WordsComparator[3].lower())][5]=1
       '''----------------------------------------------------------------Feature 4---------------------------------------------------------------------------------'''    
       if TagComparator1==Pattern1 or TagComparator1==Pattern2:
           if WordsComparator[2].lower() not in StopList:
                   if WordsComparator[2].lower() in FeatureDict:
                       temp=FeatureDict[str(WordsComparator[2].lower())][4]
                       temp+=1
                       FeatureDict[str(WordsComparator[2].lower())][4]=temp
                   else:
                       INITFeatureDictionary(str(WordsComparator[2].lower()))
                       FeatureDict[str(WordsComparator[2].lower())][4]=1
     

def NounPhrase(Parsed):
    
    Pattern1=['JJ','NNS']
    Pattern2=['JJ','NN']
    Pattern3=['DT','NN']
    Pattern4=['DT','NNS']
    TagComparator=[]
    
           
    global FeatureDict
    global StopList
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
                                        temp=FeatureDict[str(WordsComparator[tag+1].lower())][6]
                                        temp+=1
                                        FeatureDict[str(WordsComparator[tag+1].lower())][6]=temp
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
                                        temp=FeatureDict[str(WordsComparator[tag+1].lower())][7]
                                        temp+=1
                                        FeatureDict[str(WordsComparator[tag+1].lower())][7]=temp
                                   else:
                                        INITFeatureDictionary(str(WordsComparator[tag+1].lower()))
                                        FeatureDict[str(WordsComparator[tag+1].lower())][7]=1
               except:
                   pass
                
def EndingWords(WordTags):

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


def WordsOnly(WordTags):

    List=[]
    for words in WordTags:
        List.append(words[0])
    return List

def HeadVerb(Parsed):
    
     global FeatureDict
     global StopList
     Verb=[]
     Noun=[]
     
     
     for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'VP'):
            flag=0    
            for v in subtree.leaves():
                if flag==0:
                   v=v[0] 
                   v=v.lower()
                   v=v.strip()
                   if v.isalpha():
                     if v not in StopList:      
                        if v in FeatureDict:
                            temp=FeatureDict[str(v)][8]
                            temp+=1
                            FeatureDict[str(v)][8]=temp
                        else:
                            INITFeatureDictionary(str(v))
                            FeatureDict[str(v)][8]=1 
                   flag=1
                   
def VerbSubSequence(PreChunked):

    global FeatureDict
    global StopList
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
                    temp=FeatureDict[str(Verb)][9]
                    temp+=1
                    FeatureDict[str(Verb)][9]=temp
                else:
                    INITFeatureDictionary(str(Verb))
                    FeatureDict[str(Verb)][9]=1

            
def Discovered(Parsed):
    '''Checks for the sentences like The crack was discovered at the inner casing of the rod'''
    
    global WordFrequency
    global FeatureDict
    global StopList
    global DiscoveredSyn
    for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node =='Discovered'):
        Leaves=subtree.leaves()
        if Leaves[0][1]=='DT':
            if Leaves[-1][1]=='VB' or Leaves[-1][1]=='VBN' or Leaves[-1][1]=='VBG' or Leaves[-1][1]=='VBD':
               Word=Leaves[1][0].strip()
               Word=Word.lower()
               if Leaves[0][1]=='NNS' or Leaves[0][1]=='NN':
                    Verb=Leaves[-1][0].strip()
                    Verb=Verb.lower()
                    if Verb in DiscoveredSyn:
                      if Word.isalpha(): 
                        if Word not in StopList:
                            if Word in FeatureDict:
                                temp=FeatureDict[Word][17]
                                temp+=1
                                FeatureDict[Word][17]=temp
                                
                            else:
                                INITFeatureDictionary(Word)
                                FeatureDict[Word][17]=1
                    else:
                       if Verb=='found':
                        Word=Leaves[1][0].strip()
                        Word=Word.lower()
                        if Word.isalpha():  
                         if Word not in StopList:
                           if Word in FeatureDict:
                                temp=FeatureDict[Word][18]
                                temp+=1
                                FeatureDict[Word][18]=temp
                                
                           else:
                                INITFeatureDictionary(Word)
                                FeatureDict[Word][18]=1
                                
                
              
                                
            
        if Leaves[0][1]!='DT':
            if Leaves[-1][1]=='VB' or Leaves[-1][1]=='VBN' or Leaves[-1][1]=='VBG' or Leaves[-1][1]=='VBD':
                if Leaves[0][1]=='NNS' or Leaves[0][1]=='NN':
                    Verb=Leaves[-1][0].strip()
                    Verb=Verb.lower()
                    if Verb in DiscoveredSyn:
                        Word=Leaves[0][0].strip()
                        Word=Word.lower()
                        if Word.isalpha():   
                         if Word not in StopList:
                           if Word in FeatureDict:
                                temp=FeatureDict[Word][17]
                                temp+=1
                                FeatureDict[Word][17]=temp
                                
                           else:
                                INITFeatureDictionary(Word)
                                FeatureDict[Word][17]=1
                                

                    else:
                       if Verb=='found':
                        Word=Leaves[0][0].strip()
                        Word=Word.lower()
                        if Word.isalpha():  
                         if Word not in StopList:
                           if Word in FeatureDict:
                                temp=FeatureDict[Word][18]
                                temp+=1
                                FeatureDict[Word][18]=temp
                                
                           else:
                                INITFeatureDictionary(Word)
                                FeatureDict[Word][18]=1


def WordFreqFeature():
    
    global WordFrequency
    global FeatureDict
    for word in FeatureDict:
        if word in WordFrequency:
            Tfreq=WordFrequency[word]
            temp1=FeatureDict[word][2]
            temp2=FeatureDict[word][3]
            Tfreq+=temp1+temp2
            FeatureDict[word][20]=Tfreq
            WordFrequency[word]=Tfreq
            if int(temp1)!=0:
                FeatureDict[word][2]=1
                
            if int(temp2)!=0:
                FeatureDict[word][3]=1
            
            
            


def DocIndex():
    '''Imports Inverted Index file and finds the number of documents the word has occurred'''
    
    global TotalFiles
    global FeatureDict
    TempDict={}

    try:
        
        
        FeatureWordPath=os.getcwd()
        FeatureWordPath+='\\FeatureWords.txt'
        featurefile=open(FeatureWordPath,'w')

        for wrd in FeatureDict:
            wrd=wrd.strip()
            featurefile.write(wrd+'\n')

        try:
            InvertedIndex.main(sys.argv[1])
        except:
            print 'Error in the Inverted Index File'
            raise
        
        path=os.getcwd()    
        path+='\\IndexDocument.txt'
        files=open(path,'r').readlines()

        for Line in files:
            temp=re.split(' ',Line)
            Word=str(temp[0])
            Freq=float(temp[1].strip())
            TempDict[Word]=Freq
        
        for word in TempDict:
            if word in FeatureDict:
                try:
                    idf=float(math.log(float(TotalFiles)/float(TempDict[word])))
                    FeatureDict[word][19]=str(idf)
                except:
                    print word
                    pass
    except:
        print 'File Not Found'
        raise
    
def CalculateProbability():
    '''Calculates the Likelihood factor of all the Words'''
    
    global FeatureDict
    global StopList
    for Word in FeatureDict:
     try:
        Noun=float(FeatureDict[Word][0])
        Verb=float(FeatureDict[Word][1])
        if float(Verb)!=0.0:
            Nine=str(float(FeatureDict[Word][9])/float(Verb))
            Eight=str(float(FeatureDict[Word][8])/float(Verb))
            FeatureDict[Word][9]=Nine
            FeatureDict[Word][8]=Eight
        if float(Noun)!=0.0:
            Seven=str(float(FeatureDict[Word][7])/float(Noun))
            Six=str(float(FeatureDict[Word][6])/float(Noun))
            Five=str(float(FeatureDict[Word][5])/float(Noun))
            Four=str(float(FeatureDict[Word][4])/float(Noun))
            FeatureDict[Word][7]=Seven
            FeatureDict[Word][6]=Six
            FeatureDict[Word][5]=Five
            FeatureDict[Word][4]=Four
     except:
         raise

def POSLikelihood():
    '''POS tagging Likelihood'''
    
    global FeatureDict
    global WordFrequency
    try:
        for Word in FeatureDict:
            if Word in WordFrequency:
                Fnoun=str(float(FeatureDict[Word][0])/float(WordFrequency[Word]))
                Fverb=str(float(FeatureDict[Word][1])/float(WordFrequency[Word]))
                FAdj=str(float(FeatureDict[Word][16])/float(WordFrequency[Word]))
                FeatureDict[Word][0]=Fnoun
                FeatureDict[Word][1]=Fverb
                FeatureDict[Word][16]=FAdj
    except:
      raise




def ArffFileWriter():
                         
    global FeatureDict
    path=os.getcwd()
    path+='\\StanfordProbablisticFeatureDetection.arff'
    FileName=open(path,'w')
    FileName.write('@relation StanfordProbablisticFeatureDetection'+'\n')
    FileName.write('@attribute Word string'+'\n')
    FileName.write('@attribute Noun numeric'+'\n')
    FileName.write('@attribute Verb numeric'+'\n')
    FileName.write('@attribute TitleNoun {0,1}'+'\n')
    FileName.write('@attribute TitleVerb {0,1}'+'\n')
    FileName.write('@attribute Prep_Det_Noun numeric'+'\n')
    FileName.write('@attribute Prep_Det_Adj_Noun numeric'+'\n')
    FileName.write('@attribute Adj_Noun numeric'+'\n')
    FileName.write('@attribute Det_Noun numeric'+'\n')
    FileName.write('@attribute HeadVerb numeric'+'\n')
    FileName.write('@attribute VerbSubSequence numeric'+'\n')
    FileName.write('@attribute EndingED {0,1}'+'\n')
    FileName.write('@attribute EndingION {0,1}'+'\n')
    FileName.write('@attribute EndingING {0,1}'+'\n')
    FileName.write('@attribute EndingS {0,1}'+'\n')
    FileName.write('@attribute EndingAGE {0,1}'+'\n')
    FileName.write('@attribute WordNet {0,1}'+'\n')
    FileName.write('@attribute Adjective numeric'+'\n')
    FileName.write('@attribute Discovered numeric'+'\n')
    FileName.write('@attribute Found numeric'+'\n')
    FileName.write('@attribute IDF numeric'+'\n')
    FileName.write('@attribute Frequency numeric'+'\n')
    FileName.write('@attribute FailureMode {0,1}'+'\n')
    FileName.write('@data'+'\n')
    for Key in FeatureDict:
        FileName.write(' '+Key+' ,'+str(FeatureDict[Key][0])+','+str(FeatureDict[Key][1])+','+str(FeatureDict[Key][2])+','+str(FeatureDict[Key][3])+','+str(FeatureDict[Key][4])+','+str(FeatureDict[Key][5])+','+str(FeatureDict[Key][6])+','+str(FeatureDict[Key][7])+','+str(FeatureDict[Key][8])+','+str(FeatureDict[Key][9])+','+str(FeatureDict[Key][10])+','+str(FeatureDict[Key][11])+','+str(FeatureDict[Key][12])+','+str(FeatureDict[Key][13])+','+str(FeatureDict[Key][14])+','+str(FeatureDict[Key][15])+','+str(FeatureDict[Key][16])+','+str(FeatureDict[Key][17])+','+str(FeatureDict[Key][18])+','+str(FeatureDict[Key][19])+','+str(FeatureDict[Key][20])+','+'0'+'\n')
                         
    FileName.close()           
     


    
    
def main():
    
    global WordFrequency
    global FeatureDict
    global StopList
    global DiscoveredSyn
    global TotalFiles
    DiscoveredSyn={}
    StopList={}
    StopList=StopWords.StopWordList()
    Noted=['discovered','observed','noticed','detected','noted','caused','identified','occurred','watched','viewed','scrutinized','monitored']
    for l in Noted:
        DiscoveredSyn[l]=1
    
    FeatureDict={}
    WordFrequency={}
    POSTaggedFileReader()
    WordFreqFeature()
    DocIndex()
    CalculateProbability()
    POSLikelihood()
    ArffFileWriter()
    
if __name__=='__main__':
    main()
    
    
##
