import re,pprint,os,sys
import string
import NGRAMS
from NGRAMS import *
import nltk
import string
from string import *
from nltk.corpus import wordnet as wn
import StopWords


def TitleExtraction(Fread):
    '''With the Use of Regular Expression Title from the Case is extracted''' 

    First=r'--[a-zA-Z0-9]+--+[A-Za-z0-9#\- ]+\.?|-[a-zA-Z0-9]+-[A-Za-z0-9#\- ]+\.?'
    Second=r'SN/[A-Za-z0-9]*\t?[A-Z0-9a-z\W ]+\t'
    Title=r'-[A-Za-z0-9]+-|--[A-Za-z0-9]+--'
    Third=r'SN/[A-Za-z0-9]*'
    First=re.compile(First)
    Title=re.compile(Title)
    Second=re.compile(Second)
    Third=re.compile(Third)
    CutOne=re.findall(First,Fread)
    CutTwo=re.findall(Second,Fread)
    if CutOne:
            Cut=str(CutOne[0])
            Header=re.split(Title,Cut)
            Header=Header[1]
            Header=re.sub(r'#|\|,|/|\-|\d|\.|\bfax\b','',Header)
            Header=re.sub(r'\b[a-z0-9A-Z]\b|\b[a-zA-Z0-9]{2}\b','',Header)
            Header=re.sub(r'&',' and ',Header)
            Head=''
            Head=' '.join(Header.split())
            Head=UppertoLower(Head)
            if Head:
                return '<Title>'+str(Head)+'</Title>'
    if CutTwo:
            Cut=re.split(Third,str(CutTwo[0]))
            string=str(Cut[1].strip('\t'))
            string=re.sub('#|\|,|/|\-|\d|\.','',string)
            string=re.sub(r'\b[a-z0-9A-Z]\b','',string)
            string=re.sub(r'&',' and ',string)
            Head=''
            Head=' '.join(string.split())
            Head=UppertoLower(Head)
            if Head:
                return '<Title>'+str(Head)+'</Title>'

    return '<Title></Title>'        
            
   
def DocumentID(Fread):
    '''Gives the Case a Document ID'''

    try:
        DocumentID=str(re.search('[\d]+-[\d]+',str(Fread)).group(0))
        return '<DocumentID>'+str(DocumentID)+'</DocumentID>',DocumentID
    except:
        pass
    return '<DocumentID></DocumentID>',None


def Emails(Fread):
    '''Extract Emails from the Text'''

    RegexEmail=re.compile(r'\b[a-zA-Z0-9\.\-\_]+@(?:[a-zA-Z\.]+)+\b')
    Emails=re.findall(RegexEmail,Fread)
    if Emails:
        return Emails
    return None



def EnsureDir(dirname):
    '''Ensure if the Directory Exists'''

    try:
        os.makedirs(dirname)
    except OSError:
        if os.path.exists(dirname):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise                        


def  Replacement(Files,Title):
    '''RegExp for text correction'''
    
    Files=re.sub(r'I>','I',Files)
    Files=re.sub(r'[Aa]\.?[Mm]\.','',Files)
    Files=re.sub(r'[Pp]\.?[Mm]\.','',Files)
    Files=re.sub(r'[Ee]\.[Gg]\.','example',Files)
    Files=re.sub(r'[Ii]\.[Ee]\.|\b[Ii][Ee]\b','.',Files)
    Files=re.sub(r'\b[Ee][Xx][Tt][Nn]\b\.?','Extension',Files)
    Files=re.sub(r'\b[hH][rR][Ss]\b\.?','Hours',Files)
    Files=re.sub(r'\b[Cc][Oo]\b\.?',' co ',Files)
    Files=re.sub(r'\b[Rr][Pp][Mm]\b\.?','rpm',Files)
    Files=re.sub(r'\b[Ss][Ee][Cc]\b\.?|\b[Ss][Ee][Cc][Ss]\b\.?','seconds',Files)
    Files=re.sub(r'\b[Pp][Hh]\b\.?','phone',Files)
    Files=re.sub(r'\b[Ii][Nn][Cc]\b\.?','in-corporated',Files)
    Files=re.sub(r'\b[Aa][Uu][Xx]\b.?','auxillary',Files)
    Files=re.sub(r'\b[eE]quip\b\.?','equipment',Files)
    Files=re.sub(r'\b[gG]en\b\.?','General',Files)
    Files=re.sub(r'\b[Dd][Ww][Gg]\b\.?','drawing',Files)
    Files=re.sub(r'lg\.','lg',Files)
    Files=re.sub(r'[aA]ssoc\.','Associaction',Files)
    Files=re.sub(r'\.pdf','pdf',Files)
    Files=re.sub(r'\.xml','xml',Files)
    Files=re.sub(r'\b[Ww][Dd]\b\.?','wd',Files)
    Files=re.sub(r'\b[sS][Tt]\b\.?','',Files)
    Files=re.sub(r'[Pp]\.[Oo]\.?|\b[Pp][Oo]\b','PO',Files)
    Files=re.sub(r'[sS]erv\.','serves',Files)
    Files=re.sub(r'\b[eE][Xx][Cc]\b\.?','',Files)
    Files=re.sub(r'\b[Rr][Ee][Qq]\b\.?','required',Files)
    Files=re.sub(r'\b[Aa][Vv][Aa][Ii][Ll]\b\.','available',Files)
    Files=re.sub(r'\b[Rr][Ee]\b\.?','reply',Files)
    Files=re.sub(r'\b[mM][Gg][Rr]\b\.?','Manager',Files)
    Files=re.sub(r'[nN][oO]\.','NO',Files)
    Stars=re.findall(r'\*\*\* [A-Za-z]+ [a-zA-Z]*',Files)
    try:
        if Stars:
            for st in Stars:
                lists=list(st)
                lists[:3]='\*\*\*'
                st=''.join(lists)
                Files=re.sub(str(st),'\.',Files)
    except:
        print 'Problem in Stars'
        pass
            
    RegexCrap=re.compile(r'sa Archived')
    RegexCrap2=re.compile(r'removed from SN system\.?|See Activity Log for additional details\.?')
    RegexCrap3=re.compile(r'snrmonitor Problem Description:\-|Please correct and re-Approve\.?')
    RegexCrap4=re.compile(r'SN\.System\.Response SN Request updated in SN system\.?|SN\.System\.Response SN Request rejected by SN system\.?|An SN Request case must have a submitter\.?|SN\.System\.Response\.?')
    Files=re.sub(RegexCrap4,'',Files)
    Files=re.sub(RegexCrap3,'',Files)
    Files=re.sub(RegexCrap,'',Files)
    Files=re.sub(RegexCrap2,'',Files)
    Files=re.sub(r'SN/GEN/?|SN/hist/?|SN/CA/?|SN/IT/?|SN/ST/?|SN/GT/?|SN/MDT/?','',Files)
    Files=re.sub(r'SN/','',Files)
    Replace=re.findall(r'SN information for this case obtained from SN system\] [\d]*',Files)
    
    if Replace:
        Files=re.sub(str(Replace[0]),'',Files)
        
    try: 
        Files=re.sub(str(Title),'',Files)
    except:
        pass
    Files=str(Files).translate(string.maketrans("",""), '\'')
    Files=re.sub(r'\\*','',Files) 
    RegexFarh=r'[\d]+F|\?F'
    Files=re.sub(RegexFarh,' fahrenheit ',Files)
    RegexCel=r'\'C|\?C'
    Files=re.sub(RegexCel,' centigrade ',Files) 
    RegexAND=r'&'
    Files=re.sub(RegexAND,' and ',Files) 
    RegexDegree=r'\b[Dd][Ee][Gg]\b\.?'
    Files=re.sub(RegexDegree,' degree ',Files)
    RegexApprox=r'approx\.'
    Files=re.sub(RegexApprox,' approximately ',Files)
    Files=re.sub(r'temp\.',' temperature ',Files)
    Files=re.sub(r'Mr\.|Ms\.',' Mr ',Files)
    RegexTime=r'[\d]{1,2}(?:\:[\d]+)+'
    RegexAM=r'\b(AM|PM|am|pm|EST|est|CST|cst)\b'
    RegexInitial='[a-zA-Z]+-{1,2}[\w0-9]+-{1,2}'
    try:
        temp=re.search(RegexInitial,Files).group(0)
        Files=re.sub(temp,'',Files)
    except:
        pass
    RegexEmail=re.compile(r'\b[a-zA-Z0-9\.\-\_]+@(?:[a-zA-Z\.]+)+\b')
    Files=re.sub(RegexEmail,'',Files)
    Files=re.sub(r'\b[Gg][Ee]\b\.?','general electric',Files)
    Files=re.sub(RegexAM,'',Files)
    Files=re.sub(RegexTime,'',Files)
    RegexPhone=r'[0-9]+(?:-[0-9]+)+'
    Files=re.sub(RegexPhone,'',Files)
    RegexDate=r'[\d]+(?:[\-/][\d]+)+'
    Files=re.sub(RegexDate,'',Files)
    RegexStars=r'\*\*\* NOTES|\*\*\* COMMIT|\*\*\* EMAIL IN|\*\*\* EMAIL OUT|\*\*\* CASE CLOSE|PHONE|LOG|(?:NOTE|Note)(?:[\d]*):|\.{2,}|EMAIL OUT|BEEPER|FAX|CELL'
    Files=re.sub(RegexStars,'',Files)
    RegexDecimal=r'[\d]*\.[\d]+'
    Decimal=re.findall(RegexDecimal,Files)
    for dec in Decimal:
        temp=re.split('\.',dec)
        Files=re.sub(str(dec),str(temp[0]+' dot '+temp[1]),Files)
    RegexPoint=r'[\d]+\.'
    Points=re.findall(RegexPoint,Files)
    for pnt in Points:
        temp=re.split(r'\.',pnt)
        Files=re.sub(str(pnt),temp[0]+' dot ',Files)
        
    Files=re.sub(r'#|/',' ',Files)
    RegexClean=r'\bCITY\b|\bSTATE\b|\bCOUNTRY\b|\bADDRESS\b|\bPROFILE INFORMATION\b|\bNAME|\bLOCATION\b|BEEPER|\+\.|\*+|\+|:|\(|\)|\-{2,}|\[(?:,*)|\]'
    Files=re.sub(RegexClean,'',Files)
    Files=re.sub('(?:dot)','',Files)
    try:
        Files=re.sub(r'Brief overview description background related to the issue','.',Files)
    except:
        pass
    
    
    Files=' '.join(Files.split())
    return Files

def ReplaceSegmentedWords(Text,NotSegmentedWords):
    '''Find and Replace the Segmented Words in the Case '''
    
    for word in NotSegmentedWords:
        word=word.strip()
        OrgWord=word
        word=word.lower()
        try:
           if word not in StopWords.StopWordList(): 
            SegWords=NGRAMS.segment(word)
            if SegWords:
                TempList=[]
                for SegWord in SegWords:
                    SearchWord=re.search(SegWord,OrgWord,re.IGNORECASE)
                    TempList.append(SearchWord.group())
                for case in range(len(TempList)):
                    if len(TempList[case])>1:
                        rest=list(TempList[case][1:])
                        FirstChar=TempList[case][0]
                        for ind in range(len(rest)):
                            if not rest[ind].islower():
                                rest[ind]=rest[ind].lower()
                        rest="".join(rest)
                        TempList[case]=FirstChar+rest
            
            NewWord=' '.join(TempList)
            
            gold='\\b'+OrgWord+'\\b'
            regex=re.compile(gold)
            Text=re.sub(regex,str(NewWord),Text)
                                 
        except:
            print word
            pass
    return Text

def WordNet(Data):
    '''Check if the Word is in WORDNET'''
    dicts={}
    Lines=Text2Lines(Data)
    for line in Lines:
        words=nltk.word_tokenize(line)
        for wrd in words:
            if wrd.isalpha():
                lem=wn.lemmas(str(wrd))
                if len(lem)==0:
                    temp=wrd
                    temp=temp.lower()
                    temp=temp.strip()
                    if temp not in StopWords.StopWordList():
                        dicts[wrd]=1
    try:
        Lists=[]
        for keys in dicts.keys():
            Lists.append(str(keys))
        Text=ReplaceSegmentedWords(Data,Lists)
        return Text
    except:
        raise
    return None 
    

                    
def UppertoLower(Text):
    '''Restore the segmented word in Proper Case'''
    
    try:
        Data=Text2Lines(Text)
        for line in Data:
            Words=nltk.word_tokenize(line)
            for wrd in Words:
                if wrd.isalpha():
                 if len(wrd)>1:
                    if not wrd[0].islower() and not wrd[-1].islower():
                        NewWord=wrd.lower()
                        Text=re.sub(wrd,NewWord,Text)
                        
        Data=WordNet(Text)                
        return Data                               
    except:
        raise

    return None
                
    


def Text2Lines(Data):
    
    '''Check the Sentence Boundaries'''
    
    global FeatureDict
    try:
        
        SentencePattern= re.compile(r'([a-zA-Z][^\.!?]*[\.!?])', re.M)
        Lines=re.findall(SentencePattern,str(Data))
        return Lines
    except:
        print 'Error in Splitting the Text in Lines'
        raise
    return None    
    

    


def WordSegment(Files):
    '''Segment the Words'''
    
    Words=nltk.word_tokenize(str(Files))
    
    for pos in range(len(Words)):
               
                    Oldword=Words[pos]
                    word=Words[pos].lstrip()
                    word=word.rstrip()
                    word=word.lower()
                    word=re.sub(r'\A\'','',word)
                    try:
                        Lists=NGRAMS.segment(str(word))
                    except:
                        print Lists
                        Lists=''
                        pass
                        
                    Phrase=' '.join(Lists)
                    Words[pos]=Phrase
                        
                        
    Files=' '.join(Words)                  
    return Files                
    

def CreateFiles(Title,Fread,DocumentID,Emails,ID):
          '''Create XML Format Files'''
          
          DirectoryName=str(sys.argv[1])
          FileName=DirectoryName+'\\'+str(ID)+'.xml'
          FileWrite=open(FileName,'a+')
          XMLFormat='<?xml version="1.0" encoding="UTF-8"?>'          
          HeadStart='\n<Head>\n'
          HeadFinish='\n</Head>'
          FileWrite.write(XMLFormat)
          FileWrite.write(HeadStart)
          FileWrite.write('\t'+DocumentID+'\n')
          FileWrite.write('\t'+Title+'\n')
          FileWrite.write('\t'+Emails+'\n')
          FileWrite.write('\t'+Fread+'\n')
          FileWrite.write(HeadFinish)
          
def CreatingIndividualFiles():
  '''Start of the Program'''
  
  try:
    Files=open(sys.argv[1],'r').readlines()
    EnsureDir(sys.argv[2])
    for files in Files:
        Document,ID=DocumentID(files)
        print ID
        Title=TitleExtraction(files)
        Email=Emails(files)
        EmailNames=''
        if Email:
            for email in Email:
                EmailNames+=str(email)
            EmailNames='<Email>'+' '+str(EmailNames)+' '+'</Email>'
        else:
            EmailNames='<Email></Email>'
      
        try:
            CleanedContent=UppertoLower(str(Replacement(str(files),Title)))
            Fread='<Content>'+str(CleanedContent)+'</Content>'
        except:
            print 'Problem with the Upper to Lower'
            print 'Doc ID ',ID
            raise
        try:
            
            CreateFiles(Title,Fread,Document,EmailNames,ID)
        except:
            print 'Error in Creating Files'
            raise
            
  except:
       print 'Please Input in the Sequence : Paccases_file XML_Folder'
        
        
            
if __name__=='__main__':
      
      CreatingIndividualFiles()
      
