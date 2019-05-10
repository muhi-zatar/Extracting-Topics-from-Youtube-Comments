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





