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
    '''Create A 2 dimensional Hash Table eg : Dictionary['Cars']['Toyota_Camry']=1'''    
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)
    
def INITFeatureDictionary(Word):
    '''For every Word the Feature Values stored eg FeatureDict['Vibration'].[0,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1]'''

    global FeatureDict
    Feature=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for Feat in Feature:
        FeatureDict.setdefault(Word,[]).append(Feat)
        
    
    

def LocateFiles():
    '''Locates the XML flies in the Directory specified as the System Argument'''

    try:
        root=sys.argv[1]
        ListOfFiles=glob.glob(str(root)+'\\\*.xml')
        
        return ListOfFiles
    except :
        print '''Please Input the Directory Name to read in the Format(Windows): C:\PacCases7000
                 Check the Extension Its in XML Format'''

    return None

def EnsureDirectory(root):
     '''Ensures whether the Directory Specified as System Argument exists'''

     global FeatureDict
     if os.path.exists(root):
            return 1
     else:
         print 'The Directory Doesnt Exists ,Please Check the Input Once Again'

     return 0

def ExtractContents():
    '''Reads  the XML tags from the List of Cases from the Directory specified as System Argument'''

    from xml.dom.minidom import parseString
    global FLAG
    global FeatureDict
    List=LocateFiles()
    
    Counter=0
    for FileName in List:
        try:
           
            file=open(FileName,'r')
            data = file.read()
            file.close()
            dom = parseString(data)
            XMLTag = dom.getElementsByTagName('Content')[0].toxml()
            XMLData=XMLTag.replace('<Content>','').replace('</Content>','')
            XMLTitle = dom.getElementsByTagName('Title')[0].toxml()
            XMLTitleData=XMLTitle.replace('<Title>','').replace('</Title>','')
            Data=Text2Lines(XMLData)
        
            if Data:
                if FLAG==0:
                    TitleParsing(XMLTitleData)
                    '''FrequencyCalculator(Data)'''
                    
                if FLAG==1:
                    Counter+=1
                    print Counter
                    Chunker(Data)
                    VerbSubSequence(Data)
                    EndingWords(Data)
            
        except:
              print file,'No Content'
              pass
            

def Text2Lines(Data):
    '''Recognizes the Sentence boundary in the given unstructured text'''

    global FeatureDict
    try:
        
        SentencePattern= re.compile(r'([a-zA-Z][^\.!?]*[\.!?])', re.M)
        Lines=re.findall(SentencePattern,str(Data))
        return Lines
    except:
        print 'Error in Splitting the Text in Lines'

    return None    
    
def Grammar():
    ''' Regular Expression Grammar used for Chunking the Text'''

    global FeatureDict
    grammar = r"""
 NP: {<DT|JJ|NNS|NN>+}          # Chunk sequences of DT, JJ, NN
 PP: {<IN><NP>}               # Chunk prepositions followed by NP
 VP: {<VB.*><NP|PP|CLAUSE>+} # Chunk verbs and their arguments
 CLAUSE: {<NP><VP>}  # Chunk NP, VP
 """
    Parser=nltk.RegexpParser(grammar)
    return Parser

        
def Chunker(DataList):
           '''The Sentences are POS tagged , Chunked and sent for feature detection'''

           Parser=Grammar()
           t=Grammar()
           global FeatureDict
           for line in DataList:
                     PreChunked=nltk.pos_tag(nltk.word_tokenize(str(line).lower()))
                     
                     try: 
                         Parsed=Parser.parse(PreChunked)
                         VerbNounFilter(Parsed)
                         PrepositionPhrase(Parsed)
                         NounOrVerb(PreChunked)
                         NounPhrase(Parsed)                        
                         
                         
                     except:
                            print 'No Parsing Possible'
                            pass

'''-----------------Feature Generation ----------------------------------------------------------------'''


def EndingWords(Words):
    '''Feature : Words Ending with ED,ION,ING,S,AGE'''    

    '''-------------------------------Feature 10 to 14 -----------------------------------'''
    global FeatureDict
    global StopList
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
        

def WORDNET(Words):
    '''Whether the Word is present in the WORDNET'''

    '''-------------------------------Feature 15------------------------------'''  
    global Featuredict
    global StopList
    for wrd in Words:
        if wrd.isalpha():
            lem=wn.lemmas(str(wrd))
            if len(lem)>0:
                    temp=wrd
                    temp=temp.lower()
                    temp=temp.rstrip()
                    temp=temp.lstrip()
                    if temp not in StopList:
                       wrd=wrd.lower() 
                       if wrd in FeatureDict:
                        FeatureDict[str(wrd)][15]=1
                       else:
                        INITFeatureDictionary(str(wrd))
                        FeatureDict[str(wrd)][15]=1 
                    



def VerbSubSequence(Data):
    '''Feature checks the LAST verb in the consecutive sequence of Verbs'''

    global FeatureDict
    global StopList
    grammar='''Verb:{<VB.?>+}'''
    Parser=nltk.RegexpParser(grammar)
    
    for line in Data:
        Words=nltk.word_tokenize(str(line).lower())
        EndingWords(Words)#Calling Features from 10 to 14'''
        #WORDNET(Words)#Calling Feature 15'''
        PreChunked=nltk.pos_tag(Words)
        Parsed=Parser.parse(PreChunked)
        for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'Verb'):
            '''---------------------------Feature 9------------------------------------------'''
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
     

def NounPhrase(Parsed):
    '''Feature Checks the Below(immediate below) patterns in the chunked Noun Phrases'''    
    
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
                      
    
def TitleParsing(Data):
    '''Feature detects the Word in the Title is a NOUN or a Verb'''

    global StopList
    global FeatureDict
    TitleNoun=[]
    TitleVerb=[]
   
    try:
        TitleChunked=nltk.pos_tag(nltk.word_tokenize(str(Data).lower()))
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
              print 'Error in TitleParsing'
              pass


def VerbNounFilter(Parsed):
     '''Checks for the Head Verb in the Verb Phrases'''

     global FeatureDict
     global StopList
     Verb=[]
     Noun=[]
     
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
         
     
     for subtree in Parsed.subtrees(filter=lambda Parsed: Parsed.node == 'NP'):
         #Later Tune it to Length more than 2 leaves in the Phrase to eliminate the Junk
         for Leaves in subtree.leaves():
              Leaves=re.sub(RemoveNPTags,'',str(Leaves))
              tempNoun=re.split(',',str(Leaves))
              tag=tempNoun[1]
              tag=tag.rstrip()
              tag=tag.lstrip()
              tempNoun=str(tempNoun[0])
              
              if tag not in ['IN','JJ','DT']:
                  tempNoun=str(tempNoun.lstrip())
                  if tempNoun.isalpha():
                            if str(tempNoun) not in StopList:
                                    Noun.append(str(tempNoun))


     '''The Below Methods are to check the Affinity between the Machine Parts and the Failure Modes'''                                    
    
     '''if FLAG==1:
          Coccurrence(Verb,Noun)         '''
'''
def Combinations(Verb,Noun):
    
         global FeatureDict
         return itertools.product(Verb,Noun)


def Coccurrence(Verb,Noun):
     global BiWords
     global FeatureDict
     for Word in Combinations(Verb,Noun):
        
         try:
             if str(Word[0]) in BiWords.keys():
                 if Word[1] in BiWords[str(Word[0])]:
                     temp=BiWords[Word[0]][Word[1]]
                     BiWords[Word[0]][Word[1]]=str(float(temp)+1.0)
                 else:
                     BiWords[Word[0]][Word[1]]=str(1.0)
             else:
                     BiWords[Word[0]][Word[1]]=str(1.0)
         except:
             raise
    


      
def FrequencyCalculator(Data):
      global FeatureDict
      global WordProbability
      global WordFreqDist
      tempWords=nltk.word_tokenize(str(Data))
      Words=[wrd.lower() for wrd in tempWords if wrd.isalpha()]
      tempFreqDistribution=nltk.FreqDist(Words)
      for word in tempFreqDistribution.keys():
          word=word.rstrip()
          word=word.lstrip()
          Freq=float(tempFreqDistribution[word])
          if word in WordFreqDist.keys():
                  gFreq=float(WordFreqDist[word])
                  WordFreqDist[word]=str(float(gFreq)+float(Freq))
          else:
                  WordFreqDist[word]=str(Freq)
                  
def Correction():
    global WordFreqDist
    global BiWords
    global FeatureDict
    Catch=[]
    for verb in BiWords:
       for noun in BiWords[verb]:
           try:
               temp=WordFreqDist[noun]
           except:
               Catch.append(str(noun))
    CatchFreq=nltk.FreqDist(Catch)
    WordFreqDist= dict(itertools.chain(WordFreqDist.iteritems(), CatchFreq.iteritems()))
    

def NounVerbAffinity():
    
    global BiWords
    global WordFreqDist
    global BiGram

    for verbs in BiWords:
        try:
           
           for nouns in BiWords[verbs]:
                NounFreq=float(WordFreqDist[nouns])
                BiFreq=float(BiWords[verbs][nouns])
                BiGram[verbs][nouns]=str(float(BiFreq)/float(NounFreq))
            
        except:
            raise
            


def  VerbNounAffinity():
    
    global BiWords
    global WordFreqDist
    global FeatureDict
    for verbs in BiWords:
        try:
            if verbs in WordFreqDist:
                freq=float(WordFreqDist[verbs])

            denominator=0.0
            for nouns in BiWords[verbs]:
                temp=float(BiWords[verbs][nouns])
                denominator=float(denominator)+float(temp)
                
            for nouns in BiWords[verbs]:
                temp=float(BiWords[verbs][nouns])
                BiWords[verbs][nouns]=str(float(temp)/float(denominator))
        except:
            raise


def CSVFileWriter():
    
    #HAS ERROR!!    
    global FeatureDict
    FileName=open('C:\FeatureDetection.csv','wb')
    Feature=['Word','Noun','Verb','TitleNoun','TitleVerb','Prep-Det-Noun','Prep-Det-Adj-Noun','Adj-Noun','Det-Noun','HeadVerb','VerbSubSequence','EndingED','EndingION','EndingING','EndingS','EndingAGE','WordNet','FailureMode']
    Writer = csv.writer(FileName,lineterminator='\n')
    Writer.writerows(Feature)
              
    for KEY in FeatureDict:
        if KEY not in StopList:
            print KEY
            Writer.writerows({'Word':KEY,'Noun':FeatureDict[KEY][0],'Verb':FeatureDict[KEY][1],'TitleNoun':FeatureDict[KEY][2],'TitleVerb':FeatureDict[KEY][3],'Prep-Det-Noun':FeatureDict[KEY][4],'Prep-Det-Adj-Noun':FeatureDict[KEY][5],'Adj-Noun':FeatureDict[KEY][6],'Det-Noun':FeatureDict[KEY][7],'HeadVerb':FeatureDict[KEY][8],'VerbSubSequence':FeatureDict[KEY][9],'EndingED':FeatureDict[KEY][10],'EndingION':FeatureDict[KEY][11],'EndingING':FeatureDict[KEY][12],'EndingS':FeatureDict[KEY][13],'EndingAGE':FeatureDict[KEY][14],'WordNet':FeatureDict[KEY][15],'FailureMode':0})
                        
    FileName.close()
'''
def FilteringBeforeWriting():
    '''Remove the Unwanted Words '''
    global FeatureDict
    for word in FeatureDict.keys():
      if FeatureDict[word][0]==1:  
        if FeatureDict[word][1:]==[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
           del FeatureDict[word]
              
    

def ArffFileWriter():
    '''Create the Arff File for  the WEKA'''

    global FeatureDict
    path=os.getcwd()
    path+='\\FeatureDetection.arff'
    FileName=open(path,'w')
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
    FileName.write('@attribute FailureMode {0,1}'+'\n')
    FileName.write('@data'+'\n')
    for Key in FeatureDict:
        FileName.write(Key+','+str(FeatureDict[Key][0])+','+str(FeatureDict[Key][1])+','+str(FeatureDict[Key][2])+','+str(FeatureDict[Key][3])+','+str(FeatureDict[Key][4])+','+str(FeatureDict[Key][5])+','+str(FeatureDict[Key][6])+','+str(FeatureDict[Key][7])+','+str(FeatureDict[Key][8])+','+str(FeatureDict[Key][9])+','+str(FeatureDict[Key][10])+','+str(FeatureDict[Key][11])+','+str(FeatureDict[Key][12])+','+str(FeatureDict[Key][13])+','+str(FeatureDict[Key][14])+','+str(FeatureDict[Key][15])+','+'0'+'\n')
                         
    FileName.close()
    
def main():
    global WordProbability
    global WordFreqDist
    global TempStore
    global BiWords
    global BiGram
    global FLAG
    global FeatureDict
    global TEMP
    global StopList
    StopList={}
    StopList=StopList
    TEMP=[]
    FeatureDict={}
    FLAG=0
    TempStore={}
    WordProbability={}
    WordFreqDist={}
    BiWords=Ddict( dict )
    BiGram=Ddict( dict )
   
    
    if len(sys.argv)<2:
        print 'Please Enter the Directory required for Parsing the XML files'
        exit()
    
    Ensurance=EnsureDirectory(sys.argv[1])

    if Ensurance==1:
         ExtractContents()
         print 'Done!! with Titles'
         FLAG=1
         if FLAG==1:
             ExtractContents()
         FilteringBeforeWriting()
         ArffFileWriter()
         

            
if __name__=='__main__':
    from datetime import datetime 
    startTime=datetime.now()
    main()
    print (datetime.now()-startTime)
    
    
  
