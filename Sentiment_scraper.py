#!/usr/bin/env python
# coding: utf-8

# The Scraper for Financial News and Sentiment Score

# In[1]:


from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# Scraping

# In[2]:


#scrape data
url_1 = "https://finviz.com/quote.ashx?t="
news_tables = {}
# tickers = tickers_csv["Symbol"].tolist() #add csv for tickers
tickers = ['AMZN', 'TSLA', 'GOOG']
for ticker in tickers:
    url_2 = url_1 + ticker
    req =  Request(url = url_2, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'})
    response = urlopen(req)
    #extract into html
    html = BeautifulSoup(response)
    #find and load news_table
    news_table = html.find(id = 'news-table')
    #add table to dictionary
    news_tables[ticker] = news_table


# In[3]:


amzn = news_tables['AMZN']
amzn_tr = amzn.findAll('tr')

for i, table_row in enumerate(amzn_tr):
 # Read the text of the element ‘a’ into ‘link_text’
 a_text = table_row.a.text
 # Read the text of the element ‘td’ into ‘data_text’
 td_text = table_row.td.text
 # Print the contents of ‘link_text’ and ‘data_text’
 print(a_text)
 print(td_text)
 # Exit after printing 4 rows of data
 if i == 7:
    break


# In[4]:


parsed_news = []
#news iteration
for file_name, news_table in news_tables.items():
    #iterate through all tr tags
    for x in news_table.findAll('tr'):
        text = x.a.get_text() #read text from each a tag under tr tag
        date_scrape = x.td.text.split()
        if len(date_scrape) == 1:
            time = date_scrape[0] #to make sure all news time for a given date is taken
        else:
            date = date_scrape[0]
            time = date_scrape[1]
        ticker = file_name.split('_')[0]
        parsed_news.append([ticker, date, time, text])


parsed_news[:5]


# In[5]:


#converting into a DataFrame

columns = ['ticker', 'date', 'time', 'headline']
news_df = pd.DataFrame(parsed_news, columns=columns)
news_df


# Sentiment Analysis

# In[6]:


import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# In[7]:


vader = SentimentIntensityAnalyzer()
#to get polarity scores from the headlines
scores = news_df['headline'].apply(vader.polarity_scores).tolist()
scores_df = pd.DataFrame(scores)
news_df = news_df.join(scores_df, rsuffix = '_right')
news_df['date'] = pd.to_datetime(news_df.date).dt.date #to convert date column to datetime format

news_df.head()


# In[9]:


#basic plotting
plt.rcParams['figure.figsize'] = [10, 6]
mean_scores = news_df.groupby(['ticker', 'date']).mean()

mean_scores = mean_scores.unstack() #unstacking the mean

mean_scores = mean_scores.xs('compound', axis = "columns").transpose()

mean_scores.plot(kind = 'bar')
plt.grid()



# In[ ]:




