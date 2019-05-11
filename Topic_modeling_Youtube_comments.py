# importing libraries and packages
from apiclient.discovery import build #google API library
import re #for regular expressions
import nltk #for stopwords
import numpy as np 
import pandas as pd
import sqlite3 #for teh database
import gensim #for building LDA algorithm
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
#downloading stopwords
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
  while 'nextPageToken' in videos and i < 20:
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

def list_to_listoflists(lst): 
  #this function to convert a list of list of list for the purpose of stroing in a database
  result = [] 
  for el in lst: 
    sub = el.split(', ') 
    result.append(sub) 
  return (result)

def prepare_data(data): 
  #preprocessing using regular expressions
  #Removing emails
  data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]
  #Remove new line characters
  data = [re.sub('\s+', ' ', sent) for sent in data]
  #Remove distracting single quotes
  data = [re.sub("\'", "", sent) for sent in data]

  return data

def store_in_file(comments):
  #to store the data in a text file
  with open('youtube_comments.txt', 'w') as f:
    for comment in comments:
        f.write("%s\n" % comment)

def store_in_database(comments):
  #to store the data in a database using sqlite
  #creating a connection
  con = sqlite3.connect('Youtube_comments.db')
  #creating the cursor to be able to execture SQL commands
  cur = con.cursor()
  #creating the table, its name is Youtube and has one column called Comment
  cur.execute('''CREATE TABLE Youtube
         (Comment TEXT NO NULL);''')
  con.commit()
  #converting the data from list to list of lists
  new_list = list_to_listoflists(comments)
  cur.executemany("INSERT INTO Youtube VALUES (?)", new_list)
  con.commit()
  
  
def tokenization(sentences):
  #converting from sentences to words using gensim preprocess
  for sent in sentences:
    yield(gensim.utils.simple_preprocess(str(sent), deacc=True))  # deacc=True removes punctuations

def remove_stopwords(texts):
  #To remove stop words using simple preprocess from nltk
  #getting the popular stop words from nltk
  stop_words = stopwords.words('english')
  # we can also extend our stopwords
  stop_words.extend(['hello', '.com', 'also','this', 'there', 'really' , 'still'])
  return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts, data_words):
  #create bigrams
  bigram = gensim.models.Phrases(data_words, min_count=1, threshold=10) # higher threshold fewer phrases.
  #faster model
  bigram_mod = gensim.models.phrases.Phraser(bigram)
  return [bigram_mod[doc] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
  #converting words back to roots using spacy because it supports simple POS
  texts_out = []
  # Initialize spacy 'en' model, disabling Named entity recognition and keeping POS
  nlp = spacy.load('en', disable=['parser', 'ner'])
  for sent in texts:
      doc = nlp(" ".join(sent)) 
      texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
  return texts_out

def word2id(data_lemmatized):
  #representing each word with a unique ID
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
    #building the API that crawls the comments
    api_key = "AIzaSyB9u9kWqwODlegCLS0Nrae_oYvMCfD6-7E"
    youtube = build('youtube', 'v3', developerKey=api_key)
    #getting the political videos
    videos_list = get_videos('politics')
    #getting the comments from the videos
    comments_list = get_comments(videos_list)
    
    #store the comments in a file and a database
    store_in_file(comments_list)
    #store_in_database(comments_list)
    
    #data preprocessing, tokenization and removing stopwords
    comments = prepare_data(comments_list)
    data_tokenized = list(sent_to_words(comments))
    data_words_nostops = remove_stopwords(data_tokenized)
    
  # Form Bigrams
    data_words_bigrams = make_bigrams(data_words_nostops,data_tokenized)
  # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    
    #start building the LDA by creating a dictionary 
    corpus, id2word = word2id(data_lemmatized)
    
    #specify number of topics (5 in the case below)
    build_LDA(5,corpus,id2word)
