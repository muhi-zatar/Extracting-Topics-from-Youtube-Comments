# Extracting Topics from Youtube Comments
# Inroduction
Youtube is a video sharing website that is extremely popular and is used daily by millions of users around the world for differnet reasons and purposes, such as; entertainment, education, news and for getting to know for about some topics and people. Youtube also offers viewers to interact with the videos in the comments as they discuss topics related to the content of the video (not always the case).

This project scrabs viewers comments on political videos on Youtube, while getting the top topics discussed in the comments using Youtube API Data to access Youtube videos comments, Latent Dirichlet Allocation (LDA) for topic modelling and python as a programming language. 
# Prerequisites

- Python 2.7, 3.5 or 3.6

- nltk

- spacy (download with !python3 -m spacy download en)

- gensim

# Main Steps:
The workflow of this project can be summurized in the following steps:

1- Getting the Data (youtube comments on political videos). 

2- Storing the collected data in a database using SQLite or a file.

3- Data preprocessing (This step is always more important than you think).

4- Apply Latent Dirichlet Allocation (LDA) on the Data to get the topics.

5- Visualize the results in a fancy way.

# Getting the Data

Of course the first step will be crawling the Data (because what can we do without it). Getting comments from youtube can be divided into two steps; creating your project and credentials on Google Developers and writing the code that crawls the users comments.

**Creating project and credentials**

Youtube provides an API to access the comments on the videos with a proper [documentation](https://developers.google.com/youtube/v3/docs/commentThreads/list).
To start with, one needs to create a project and Google Developers and Enable Youtube Data API; [a step by step guide](https://www.slickremix.com/docs/get-api-key-for-youtube/).

Generally speaking, one can access and crawl comment on youtube by either creating [OAuth 2.0 credentials or API keys](https://developers.google.com/youtube/registering_an_application). For the purpose of this project, API keys will be used.

Now assuming you got your API key, let's move to the next step and write the code. 

**Writing the Code**

First of all, we need the API KEY
```python
api_key = "YOUR_API_KEY"
```

Now we need to import the [Google API client Library](https://developers.google.com/api-client-library/python/start/get_started)
```python
from apiclient.discovery import build
```
Then using the [build function](https://developers.google.com/api-client-library/python/start/get_started#building-and-calling-a-service) to create the service object. This function takes the api_name, api_version and developer_key as arguments which are youtube, v3 and api_key respectively in our case.

```python
youtube = build('youtube', 'v3', developerKey=api_key)
```

Since our goal is to get Youtube comments on videos, at first we need the videos (obviously!). This can be done by the following [line of code](https://developers.google.com/youtube/v3/docs/search/list). 
```python
videos = youtube.search().list(part='id',
                            q=query,
                            order = 'relevance',
                            type='video',
                            maxResults=50).execute()
```
Where query is predefined by the user to specify the topic of the videos; e.g: politics, news, Marvel, Messi. Where maxResults is the number of videos (0 to 50). But be careful as you cant do this all day due to the [daily quota](https://developers.google.com/youtube/v3/getting-started#quota) 

This will return the following(for one video):
```
{'etag': '"XpPGQXPnxQJhLgs6enD_n8JR4Qk/anRstLeDC5jwWAjZoA6OemWG3-A"',
 'id': {'kind': 'youtube#video', 'videoId': 'kdFFzjWJd2g'},
 'kind': 'youtube#searchResult'}
```

Since we are concerned only about the comments of the video, hence we only need the ID of the video, which can be extracted as following (i is a value between 0 and maxResults):
```python
videos['items'][i]['id']['videoId']
```
Now we are ready to extract the comments of the video using [this line](https://developers.google.com/youtube/v3/docs/commentThreads/list):
```python
comments = youtube.commentThreads().list(
                    part = 'snippet',
                    videoId = VideoId,
                    maxResults = 100, # Only take top 100 comments...
                    order = 'relevance', #... ranked on relevance
                    textFormat = 'plainText',
                    ).execute()
```
Executing this will return the following for one video:
```
{'etag': '"XpPGQXPnxQJhLgs6enD_n8JR4Qk/PQb0UysY2hmL5QQLd7NNAwko7sQ"',
 'id': 'UgwfqkoJx7fsJPv6-iJ4AaABAg',
 'kind': 'youtube#commentThread',
 'snippet': {'canReply': True,
  'isPublic': True,
  'topLevelComment': {'etag': '"XpPGQXPnxQJhLgs6enD_n8JR4Qk/8uH99A9-wjz1kHxAyoV2OwRbEhQ"',
   'id': 'UgwfqkoJx7fsJPv6-iJ4AaABAg',
   'kind': 'youtube#comment',
   'snippet': {'authorChannelId': {'value': 'UCWyqLzBpUpJ655riXS7GNZQ'},
    'authorChannelUrl': 'http://www.youtube.com/channel/UCWyqLzBpUpJ655riXS7GNZQ',
    'authorDisplayName': 'Iyobo Festus',
    'authorProfileImageUrl': 'https://yt3.ggpht.com/-ZAzGYA7HgIs/AAAAAAAAAAI/AAAAAAAAAAA/i2UDO4HGlCA/s28-c-k-no-mo-rj-c0xffffff/photo.jpg',
    'canRate': True,
    'likeCount': 11,
    'publishedAt': '2019-05-09T03:58:28.000Z',
    'textDisplay': "It's  good  to be sincere  Atiku  was the winner  of that election",
    'textOriginal': "It's  good  to be sincere  Atiku  was the winner  of that election",
    'updatedAt': '2019-05-09T03:58:28.000Z',
    'videoId': 'kdFFzjWJd2g',
    'viewerRating': 'none'}},
  'totalReplyCount': 1,
  'videoId': 'kdFFzjWJd2g'}}
```
However, we are only concerned about the comments of the users, which we can extract using this command line(i is a value between 0 and maxResults):
```python
comment_list.append(response['items'][j]['snippet']['topLevelComment']['snippet']['textDisplay'])
```
To wrap up, this is the whole code that will extract user comments from political videos on Youtube using Youtube Data API with some modifications from the above, such as navigating through multiple pages (the comments in the code will lead you through that):
```python
api_key = "YOUR_API_KEY"
from apiclient.discovery import build
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
 ```
# Storing the collected Data

The collected data is valuable indeed, and therefore it is recommended to be stored for future use. One can store the data in a file (CSV, Excel, text). In python, this can be done easily using the following command.
```python
with open('youtube_comments.txt', 'w') as f:
    for comment in comment_list:
        f.write("%s\n" % item)
```
On the other hand, a more sophisticated and feasible way to store data is using a database. It is worth mentioning that how we are using the database in this example, is not the optimal use of databases and not the reason why databases were created in the first place, as they are created for far more complicated, relational and structured data. 

We will be using [SQLite](https://docs.python.org/2/library/sqlite3.html) due to the fact that it does not require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language. Frist of all, we need to establish a connection and create a cursor as following:
```python
import sqlite3
con = sqlite3.connect('Youtube_comments.db')
cur = con.cursor()
```
Then we need to create the table using the following SQL command (the name of the table is Youtube and it has one TEXT column called comment:
```python
cur.execute('''CREATE TABLE Youtube
         (Comment TEXT NO NULL);''')
con.commit()
```
The collected comments are currently stored in a list, which is required to be converted to a list of lists to be inserted in the database using execturemany() command:
```python
def list_to_listoflists(lst): 
    result = [] 
    for el in lst: 
        sub = el.split(', ') 
        result.append(sub) 
      
    return(result) 
new_list = list_to_listoflists(comment_list)
cur.executemany("INSERT INTO Youtube VALUES (?)", new_list)
con.commit()
```
Now to fetch the data from the database, the following command is used:
```python
cur.execute('SELECT * FROM Youtube')
data = cur.fetchall()
```

# Data Preprocessing

After retrieving the Data from the database, it is mandatory to preprocess the data in order to apply Machine Learning techniques on it.

The preprocessing in our case is divided into multiple steps as follwoing:

1- Preprocessing using regular expressions.

2- Tokenization.

3- Preparing and removing stop words.

4- Create bag of words(bigram models).

5- Lemmatizing and stemming.

**Preprocessing using regular expressions**

[Regular expressions](https://www.machinelearningplus.com/python/python-regex-tutorial-examples/) is a very useful tool for preprocessing data such as; removing undesirable strings, spaces, etc. Which we will be using here for the purpose of text preprocessing.
```python
import re

def prepare_data(data): 
  data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]
# Remove new line characters
  data = [re.sub('\s+', ' ', sent) for sent in data]
# Remove distracting single quotes
  data = [re.sub("\'", "", sent) for sent in data]

  return data
```
**Tokeinization**

Simply in this step, we're splitting sentences into words for purposes that will be more obvious later in the document. For doing this, [simple_preprocess from gensim](https://radimrehurek.com/gensim/utils.html) does the job in addition to removing punctuation and undesirable characters.
```python
from gensim.utils import simple_preprocess
def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations
```
**Preparing and removing stop words**

This step gives more emphasis on the words that are more relevant and help the learning technique to concentrate on them. Examples on stop words in english could be: 'and', 'but', 'a', 'how', 'what'. Words like these could occur in any text and hence it is better to remove them.

Stop words removal start with stating these words, luckily, we have them ready thank to [Natural Language Toolkit (nltk)](https://www.nltk.org/). 
The following lines of code prepares the stop words in english. 
```python
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
# we can also extend our stopwords
stop_words.extend(['hello', '.com'])
def remove_stopwords(texts):
  stop_words = stopwords.words('english')
  # we can also extend our stopwords
  stop_words.extend(['hello', '.com'])
  return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]
```

**Create bag of words (bigram models)**

Bigrams are two words frequently occurring together in the document. Again, they can be [created in gensim](https://radimrehurek.com/gensim/models/phrases.html)
```python
bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
bigram_mod = gensim.models.phrases.Phraser(bigram)
def make_bigrams(texts, data_words):
  bigram = gensim.models.Phrases(data_words, min_count=1, threshold=10) # higher threshold fewer phrases.
  bigram_mod = gensim.models.phrases.Phraser(bigram)
  return [bigram_mod[doc] for doc in texts]
```

**Lemmatizing and stemming**

Lemmatizing is changing past and future tenses to present tense and third point of view are changed to first point of view, whereas Stemming is simply convierting the word back to its root. Again these techniques help to unify the appearance of words that existed in different forms, as an example; rockets is converted back to rocket, walks, walked and walking are converted to walk. This helps the learning technique not to get confused by these form of the same word (after all, the machines are not as smart as us, so far!).
However, this is not as tiring as it sounds. It can be done using [WordNetlemmatizer](https://www.geeksforgeeks.org/python-lemmatization-with-nltk/) from nltk or lemmatizer from [spacy](https://spacy.io/api/lemmatizer), we will be using sapcy as it supports simple part of speech tagging(identifies if the word is verb, noun, adj, etc. 
```python
import spacy
def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
  texts_out = []
  # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
  nlp = spacy.load('en', disable=['parser', 'ner'])
  for sent in texts:
      doc = nlp(" ".join(sent)) 
      texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
  return texts_out
```

# Apply Latent Dirichlet Allocation (LDA)

Latent Dirichlet Allocation (LDA) is an unsupervised learning algorithm for topic modeling. To tell briefly, LDA imagines a fixed set of topics. Each topic represents a set of words. And the goal of LDA is to map all the documents to the topics in a way, such that the words in each document are mostly captured by those imaginary topics. For more details, read the [paper](http://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf), or [this article](https://towardsdatascience.com/light-on-math-machine-learning-intuitive-guide-to-latent-dirichlet-allocation-437c81220158) and have a look on [this video](https://www.youtube.com/watch?v=3mHy4OSyRf0). With Gensim, life is much easier for building this algorithm; you only have to predetermine the number of topics, get the data, clean it and gensim does the magic. 

But first of all, as known, machines do not understand words, and hence we need to represent each word by a differen id in a dictionary, and calculating the frequency of each term. This can be done using [doc2bow from gensim](https://radimrehurek.com/gensim/corpora/dictionary.html)
```python
# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized)

# Create Corpus
texts = data_lemmatized

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# View
print(corpus[:1])
```
Now we have everything ready to build the [LDA model](https://radimrehurek.com/gensim/models/ldamodel.html)
```python
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=5, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)
```
# Interpreting and visualizing the results

Now we cant get the keywords in each topic by writing the following line:
```python
print(lda_model.print_topics())
```
The output of this line will be in the following format:
```
[(0,
  '0.046*"video" + 0.020*"right" + 0.017*"also" + 0.016*"watch" + 0.013*"have" '
  '+ 0.013*"congress" + 0.012*"first" + 0.009*"law" + 0.009*"interview" + '
  '0.008*"medium"'),
 (1,
  '0.028*"work" + 0.022*"could" + 0.015*"tell" + 0.013*"hear" + 0.013*"hate" + '
  '0.012*"build" + 0.011*"money" + 0.010*"mind" + 0.009*"modiji_modiji" + '
  '0.009*"next"'),
 (2,
  '0.040*"not" + 0.025*"do" + 0.021*"be" + 0.013*"great" + 0.010*"way" + '
  '0.010*"politic" + 0.010*"party" + 0.010*"political" + 0.008*"can" + '
  '0.007*"government"'),
 (3,
  '0.027*"really" + 0.024*"guy" + 0.020*"well" + 0.019*"bjp" + 0.017*"hai" + '
  '0.017*"modi" + 0.013*"long" + 0.013*"still" + 0.010*"someone" + 0.009*"ki"'),
 (4,
  '0.021*"people" + 0.020*"good" + 0.017*"get" + 0.014*"s" + 0.014*"make" + '
  '0.014*"say" + 0.013*"would" + 0.013*"trump" + 0.013*"think" + 0.012*"go"')]
```
How to interpret this?

Topic 0 is a represented as (0,
  '0.046*"video" + 0.020*"right" + 0.017*"also" + 0.016*"watch" + 0.013*"have" '
  '+ 0.013*"congress" + 0.012*"first" + 0.009*"law" + 0.009*"interview" + '
  '0.008*"medium"'),.

It means the top 10 keywords that contribute to this topic are: ‘video’, ‘right’, ‘also’.. and so on and the weight of ‘video’ on topic 0 is 0.046.

The weights reflect how important a keyword is to that topic.

**Data Visualization**
 
 There are multiple ways that we can visualize and represent our results from topic modeling using LDA. However, one popular way to do that is using [pyLDAvis](https://pyldavis.readthedocs.io/en/latest/readme.html).
 ```
 import pyLDAvis.gensim
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary=lda_model.id2word)
vis
```
**Image of the results will be posted once ready**

# Future work and enhancement

It is inevitable that the built model can be enhanced in many ways, some examples are:

- Optimizing the selection of the number of topic using [Topic Cohernence score](https://rare-technologies.com/what-is-topic-coherence/) and tunning the parameters of the LDA to increase the topic coherence.

- Manual Error Analysis that my lead to some useful conclusions in some stages such as removing some words and expressions in the preprocessing stage.

- More data (always a solution)

- Using [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) which is intended to reflect how important a word is to a document in a collection or corpus. 

-  Building LDA Mallet Model, which usually gives better models and results. 
 
