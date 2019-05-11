# importing libraries and packages
from apiclient.discovery import build
import re
import nltk
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
#import pyLDAvis
#import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
%matplotlib inline
nltk.download('stopwords')

def get_videos(query):
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
  while 'nextPageToken' in videos and i < 2:
    videos = youtube.search().list(part='id',
                            q=query, #the topic we want
                            order = 'relevance', #ranked on relevance
                            type='video',
                            maxResults=50,
                            pageToken = videos['nextPageToken']).execute()
    
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

!python3 -m spacy download en

def prepare_data(data): 
  data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]
# Remove new line characters
  data = [re.sub('\s+', ' ', sent) for sent in data]
# Remove distracting single quotes
  data = [re.sub("\'", "", sent) for sent in data]

  return data

def sent_to_words(sentences):
  for sentence in sentences:
    yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def remove_stopwords(texts):
  stop_words = stopwords.words('english')
  # we can also extend our stopwords
  stop_words.extend(['hello', '.com'])
  return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts, data_words):
  bigram = gensim.models.Phrases(data_words, min_count=1, threshold=10) # higher threshold fewer phrases.
  bigram_mod = gensim.models.phrases.Phraser(bigram)
  return [bigram_mod[doc] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
  texts_out = []
  # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
  nlp = spacy.load('en', disable=['parser', 'ner'])
  for sent in texts:
      doc = nlp(" ".join(sent)) 
      texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
  return texts_out

def word2id(data_lemmatized):
  # Create Dictionary
  id2word = corpora.Dictionary(data_lemmatized)
  # Create Corpus
  texts = data_lemmatized
  # Term Document Frequency
  corpus = [id2word.doc2bow(text) for text in texts]
  return corpus, id2word
  
def build_LDA(topics_num, corpus, id2word):
  lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=topics_num, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)
  
  print(lda_model.print_topics())
  
  if __name__== "__main__":
    api_key = "AIzaSyB9u9kWqwODlegCLS0Nrae_oYvMCfD6-7E"
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos_list = get_videos('politics')
    comments_list = get_comments(videos_list)
    comments = prepare_data(comments_list)
    data_tokenized = list(sent_to_words(comments))
    data_words_nostops = remove_stopwords(data_tokenized)
  # Form Bigrams
    data_words_bigrams = make_bigrams(data_words_nostops,data_tokenized)
  # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    corpus, id2word = word2id(data_lemmatized)
    build_LDA(5,corpus,id2word)
