import MeCab
#import gensim
#import numpy as np
from collections import defaultdict
import requests as req
from scraping_tools import tag_search as xml

dictionary_location="-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"

#sorted(frequency.items(),key=lambda x:-x[1])
JAPANESE=["ja","jp","JP","jpn","JPN","japan","japanese","Japan","Japanese","JAPANESE","JAPAN"]
ENGLISH=["en","EN","english","eng","ENG","ENGLISH"]

def get_wordfrequency(documents,allword=True,language='ja'):
    """
    各文書中に出現する各単語の出現回数を数える.
    
    
    Args
    ____
        documents(single text list):
        language(str):ja,en
        allword(boolean): whether return the word frequency of all documents or each frequency of documents
    ____
    """
    
    stop_words = set('は を に へ です する から たり ながら れる られ など ます いる こと ため なぜ べき よう まで たち まし ある として さん なり について'.split())|set([w for w in [
        "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    ]])if(language=='ja') else set('at in on and or this that'.split())
    
    tagger=MeCab.Tagger("-Owakati "+dictionary_location)#(-"Owakati")
    nostopword_documents=[]
    for document in documents:
        nostopword_sentences=[]
        sentences=document2sentences(document,language)
        for sentence in sentences:
            nostop_words=[]
            for word in tagger.parse(sentence).split(" ") if(language=='ja') else sentence.split(" "):
            #whether word isn't single Kanji
                if(((len(word)>1)|(re.search('[\u4E00-\u9FD0]',word)!=None))&(not word in stop_words)):
                    nostop_words.append(word)
            nostopword_sentences.append(nostop_words)
        nostopword_documents.append(nostopword_sentences)
        
    frequency=[defaultdict(int) for w in range(len(documents))]
    for nostopword_document,each_frequency in zip(nostopword_documents,frequency):
        for sentence in nostopword_document:
            for word in sentence:
                each_frequency[word]+=1
    #frequency=sorted(frequency.items(),key=lambda x:-x[1])
    if(allword):
        frequency=convert_wordfrequency(frequency)
        frequency=sorted(frequency.items(),key=lambda x:-x[1])
    return frequency,nostopword_documents

def get_frequency(ochasened_documents,allword=True,language='ja'):
    """
    """
    frequency=[defaultdict(int) for w in range(len(ochasened_documents))]
    for nostopword_document,each_frequency in zip(ochasened_documents,frequency):
        for sentence in nostopword_document:
            for word in sentence:
                each_frequency[word]+=1
    if(allword):
        frequency=convert_wordfrequency(frequency)
        frequency=sorted(frequency.items(),key=lambda x:-x[1])
    return frequency

def document2sentences(document,language):
    """
        split document to each sentences
    """
    if(language in JAPANESE):
        sentences=re.split(r'。|\n',document)
        
        """#括弧内の。では区切らないようにする必要がある.!!!後で!!!
        #if(document.find("「")!=-1):
        kakko=0
        for w in range(len(sentences)):
            if("「" in sentences[w]):
                if(kakko==0):
                    start_index=w
                kakko+=1
            if("」" in sentences[w]):
                kakko-=1
                end_index=w
                if((kakko==0)&(start_index!=end_index)):
                    str_=""
                    for index in range(start_index+1,end_index+1):
                        str_+="。"+sentences[w]
                        del(sentences[w])
                    sentences[start_index]+=str_"""
    elif(language in ENGLISH):
        sentences=re.split(".",document)
    return sentences

def convert_wordfrequency(each_frequency):
    """
        this convert each documents frequency into all word frequency
        
        Args
        _____
            each_frequency (double dict list)
        _____
        
    """
    allword_frequency={}
    for frequency in each_frequency:
        for key in frequency.keys():
            if(key in allword_frequency.keys()):
                allword_frequency[key]+=frequency[key]
            else:
                allword_frequency[key]=frequency[key]
    return allword_frequency

import re
def get_ochasen(documents,language="jp",lorgd=True):
    """
        return each sentence's ochasen(word property)
    """
    ochasen_lists=[]
    tagger_container=""#"-Ochasen"
    if(lorgd):
        tagger_container=dictionary_location+" {0}".format(tagger_container)
    print(tagger_container)
    tagger= MeCab.Tagger(tagger_container)
    
    for document in documents:
        ochasen_list=[]
        sentences=document2sentences(document,language)
        for sentence in sentences:
            content=sentence_ochasen(sentence,tagger)
            if(content==[]):
                continue
            ochasen_list.append(content)
        ochasen_lists.append(ochasen_list)
    return ochasen_lists

def sentence_ochasen(sentence,tagger):
    """
        return splited MeCab owakati list
    """
    ochasen_sentence=tagger.parse(sentence)
    ochasen_list=[]
    for each_owakati in re.split(r'\n',ochasen_sentence):
        splited=each_owakati.split("\t")
        if(len(splited)<2):
            continue
        each_item=[splited[0]]
        each_item.extend(re.split(r',',splited[1]))
        ochasen_list.append(each_item)#re.split(r',',each_owakati))
    return ochasen_list

def get_specificword(document_ochasen,pattern,negative):
    """
        助詞以外のwordを取得する.
        単語は活用前を取得する.(index-2)
        品詞:index-3
    """
    documents=[]
    for document in document_ochasen:
        sentences=[]
        for sentence in document:
            words=[]
            for word in sentence:
                hinshi=re.search(pattern,word[3])
                if(negative&(hinshi!=None)):
                    continue
                elif((not negative)&(hinshi==None)):
                    continue
                words.append(word[3])
            sentences.append(words)
        documents.append(sentences)
    return documents

def get_pronoun(document_ochasen):
    return get_specificword(document_ochasen,r'名詞-一般|固有名詞|名詞-.*?接続',negative=False)
def get_nojoshi(document_ochasen):
    return get_specificword(document_ochasen,r'助.*?詞|連体詞|非自立|記号|数',negative=True)

import googletrans
def get_transtext(text,dest):
    """
        dest in ["ja","en"]
    """
    translator=googletrans.Translator()
    return translator.translate(text,dest=dest).text

def owakati_rss(url,language='ja'):
    """
    Args
    ____
        language 'ja','en'
    ____
    """
    
    get=req.get(url)
    get.encoding=get.apparent_encoding
    html=get.text
    del(get)
    
    item=xml.get_eachtag(html,"item",["title"],only_text=False)
    check,list_num=item,0#n重リストかを判定する.
    """while(type(check)==list):
        list_num+=1
        check=check[-1]
    for w in list_num:
        pass
    """
    for w in range(len(item)):
        item[w]=item[w][0]
    
    print(item)
    return get_list(item,language=language)

def dependency_parse(documents):
    ochasen_documents=get_ochasen(documents)
    for ochasen_sentences in ochasen_documents:
        for ochasen_sentence in ochasen_sentences:
            dependency_sentence(ochasen_sentence)
            
def dependency_sentence(ochasened_sentence):
    """助詞だけをまず抜き出す."""
    
    print("dep:",ochasened_sentence)
    str_=""
    for w in ochasened_sentence:
        str_+=w[0]
    print(str_)
    connected_word=""
    for w in range(len(ochasened_sentence)):
        if("助詞" in ochasened_sentence[w][3]):
            print(connected_word)
            print(ochasened_sentence[w][0])
            connected_word=""
        else:
            connected_word+=ochasened_sentence[w][0]
    print(connected_word)
    
    input_=input("まずは一次群を選択")
    
    """
        (0-1)-2 (((4-5-6-7-8)-9)-10-11)-12
        (0-)
    """