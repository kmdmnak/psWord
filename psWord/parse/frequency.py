from . import language
import MeCab
from collections import defaultdict

def getWordOwakati(documents,language_sign='ja'):
    """
    return how many times each word appear in documents.
    if allword is false , return 

    Args
    ____
        documents(one-D str list):
        language(str):ja,en
        allword(boolean): whether it return each frequency of each document
    ____
    
    Returns
    ____
        frequency :
        nostopword_documents :
    ____
    
    """
    handler=language.getHandler(language_sign,tagger=MeCab.Tagger("-Owakati"))
    #this contain word list of each document without stop words.
    nonstop_words_documents=[]
    for document in documents:
        nonstop_words_sentences=[]
        sentences=handler.extractSentences(document)
        for sentence in sentences:
            # extracting words depend on language
            words=handler.extractWords(sentence)
            nonstop_words_sentences.append(handler.extractNonStopWords(words))
        nonstop_words_documents.append(nonstop_words_sentences)
    #frequency=getFrequency(nonstop_words_documents,allword)
    return nonstop_words_documents

def getFrequency(nonstop_words_documents,allword=True):
    """
        USED in getWordFrequency
    """
    frequency=[defaultdict(int) for w in range(len(nonstop_words_documents))]
    for nostopword_document,each_frequency in zip(nonstop_words_documents,frequency):
        for sentence in nostopword_document:
            for word in sentence:
                each_frequency[word]+=1
    if(allword):
        frequency=convert2AllWordsFrequency(frequency)
        frequency=sorted(frequency.items(),key=lambda x:-x[1])
    return frequency

def convert2AllWordsFrequency(frequencies):
    """
        this convert each document's frequency into all word frequency
        
        Args
        _____
            each_frequency (2-D dict list)
        _____
        
    """
    #{word1:count(int),word2:count(int)...}
    frequency={}
    for each_frequency in frequencies:
        for each_key in each_frequency.keys():
            isEmpty=(frequency.get(each_key)==None)
            if(isEmpty):
                frequency[each_key]=each_frequency[each_key]
                continue
            frequency[each_key]+=each_frequency[each_key]
    return frequency
