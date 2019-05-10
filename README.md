# Extracting-Topics-from-Youtube-Comments
# Inroduction
Youtube is a video sharing website that is extremely popular and is used daily by millions of users around the world for differnet reasons and purposes, such as; entertainment, education, news and for getting to know for about some topics and people. Youtube also offers viewers to interact with the videos in the comments as they discuss topics related to the content of the video (not always the case).

This project scrabs viewers comments on political videos on Youtube, while getting the top topics discussed in the comments using Youtube API Data to access Youtube videos comments, Latent Dirichlet Allocation (LDA) for topic modelling and python as a programming language. 

# Main Steps:
The workflow of this project can be summurized in the following steps:

1- Getting the Data (youtube comments on political videos). 

2- Storing the collected data in a database using SQLite.

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
```
api_key = "YOUR_API_KEY"
```

Now we need to import the [Google API client Library](https://developers.google.com/api-client-library/python/start/get_started)
```
from apiclient.discovery import build
```
Then using the [build function](https://developers.google.com/api-client-library/python/start/get_started#building-and-calling-a-service) to create the service object. This function takes the api_name, api_version and developer_key as arguments which are youtube, v3 and api_key respectively in our case.

```
youtube = build('youtube', 'v3', developerKey=api_key)
```

Since our goal is to get Youtube comments on videos, at first we need the videos (obviously!). This can be done by the following [line of code](https://developers.google.com/youtube/v3/docs/search/list). 
```
videos = youtube.search().list(part='id',
                            q=query,
                            order = 'relevance',
                            type='video',
                            maxResults=50).execute()
```
Where query is predefined by the user to specify the topic of the videos; e.g: politics, news, Marvel, Messi. Where maxResults is the number of videos (0 to 50). But be careful as you cant do this all day due to the [daily quota](https://developers.google.com/youtube/v3/getting-started#quota) 
This will return the following(for one video):

Since we are concerned only about the comments of the video, hence we only need the ID of the video, which can be extracted as following (i is a value between 0 and maxResults):
```
videos['items'][i]['id']['videoId']
```
Now we are ready to extract the comments of the video using [this line](https://developers.google.com/youtube/v3/docs/commentThreads/list):
```
comments = youtube.commentThreads().list(
                    part = 'snippet',
                    videoId = VideoId,
                    maxResults = 100, # Only take top 100 comments...
                    order = 'relevance', #... ranked on relevance
                    textFormat = 'plainText',
                    ).execute()
```
This will return, and we are only concerned about the comments of the users, which we can extract using this command line:9i is a value between 0 and maxResults):
```
comment_list.append(response['items'][j]['snippet']['topLevelComment']['snippet']['textDisplay'])
```
To wrap up, this is the whole code that will extract user comments from political videos on Youtube using Youtube Data API with some modifications from the above, such as navigating through multiple pages (the comments in the code will lead you through that):
```
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
 ```
