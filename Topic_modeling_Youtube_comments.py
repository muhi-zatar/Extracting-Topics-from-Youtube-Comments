# importing libraries and packages
from apiclient.discovery import build
import re
import numpy as np
import pandas as pd
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
# spacy for lemmatization
import spacy
from nltk.corpus import stopwords
# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
%matplotlib inline

def get_videos(query, api_key):
  youtube = build('youtube', 'v3', developerKey=api_key)
  videos_list = [] #storing the videos IDs in a list
  videos = youtube.search().list(part='id',
                            q=query,
                            order = 'relevance',
                            type='video',
                            maxResults=50).execute()
  
  for i in range(50):
  #storing the results in a list
  #5o is the maxResults value
    videos_list.append(videos['items'][i]['id']['videoId'])
  
  i = 0 #number of pages to navigate through
  #the following lines is to navigate through multiple pages, as the search request return nextPageToken if exists
  while 'nextPageToken' in videos and i < 20:
    videos = youtube.search().list(part='id',
                            q=query, #the topic we want
                            order = 'relevance', #ranked on relevance
                            type='video',
                            maxResults=50,
                            pageToken = res['nextPageToken']).execute()
    
    for j in range(50):
      try:
      #stroing the results in a list
      #for error handling in case of index is out of range
        videos_list.append(videos['items'][j]['id']['videoId'])
      except:
        break
    i = i+1
    #so far, we have the video Ids now let get the comments from all the political videos we got  
  return videos_list

def get_comments(videosId_list):
  comment_list = [] # initially, let's store the comments in a list 

  for i in videosId_list:
    #getting the video ids
    try:
      # in case of disabled comments on the video, we need to handle this error
      comments = youtube.commentThreads().list(
                    part = 'snippet',
                    videoId = str(i),
                    maxResults = 100, # Only take top 100 comments
                    order = 'relevance', #ranked on relevance
                    textFormat = 'plainText',
                    ).execute()
    except:
      continue
    
    for j in range(99):
      try:
        comment_list.append(comments['items'][j]['snippet']['topLevelComment']['snippet']['textDisplay'])
      except:
        continue
  return comment_list

stop_words = stopwords.words('english')
# we can also extend our stopwords
stop_words.extend(['hello', '.com'])
!python3 -m spacy download en
nlp = spacy.load('en', disable=['parser', 'ner'])


def prepare_data(data): 
  data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]

# Remove new line characters
  data = [re.sub('\s+', ' ', sent) for sent in data]

# Remove distracting single quotes
  data = [re.sub("\'", "", sent) for sent in data]

  print(data[:1])
  return data

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

data_words = list(sent_to_words(data))

bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
bigram_mod = gensim.models.phrases.Phraser(bigram)

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out
