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

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
%matplotlib inline

youtube = build('youtube', 'v3', developerKey=api_key)
query = 'politics'
videos_list = [] #storing the videos IDs in a list
videos = youtube.search().list(part='id',
                            q=query,
                            order = 'relevance',
                            type='video',
                            maxResults=50).execute()
for i in range(50):
  #stroing the results in a list
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
  
comment_list = [] # initially, let's store the comments in a list 
for i in videos_list:
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
      comment_list.append(response['items'][j]['snippet']['topLevelComment']['snippet']['textDisplay'])
    except:
      continue
