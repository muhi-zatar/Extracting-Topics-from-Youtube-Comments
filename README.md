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

Of course the first step will be crawling the Data (because what can we do without it).
Youtube provides an API to access the comments on the videos with a proper [documentation](https://developers.google.com/youtube/v3/docs/commentThreads/list)



