#!/usr/bin/env python
# coding: utf-8

# Stock Profile Heatmap based on Sentiment and Returns

# In[1]:


# libraries for webscraping, parsing and getting stock data
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd


# In[60]:


#ticker list for the project
tickers_dict = {'AMZN': 5, 'TSLA': 1, 'GOOG': 3, 'META': 3, 'KO': 10, 'PEP': 5,
                'BA': 5, 'XOM': 5, 'CVX': 4, 'UNH': 1, 'JNJ': 3, 'JPM': 3,
                'BAC': 5, 'C': 5, 'SPG': 10, 'AAPL': 6, 'MSFT': 5, 'WMT': 6,
                'LMT': 2, 'PFE': 10, 'MMM': 3, 'DIS': 8, 'AIG': 5, 'BRK-B': 4,
                'SLB': 16, 'PLD': 5, 'AMD': 5, 'ISRG': 3, 'INTC': 5}

 devices, intuitive surgical, intel

tickers = tickers_dict.keys()
n_shares = tickers_dict.values()


# In[61]:


#this part is copied fromt the crawler notebook I made

#scrape data
url_1 = "https://finviz.com/quote.ashx?t="
news_tables = {}

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


# In[62]:


# NLTK VADER for sentiment analysis
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# In[63]:


# Instantiate the sentiment intensity analyzer
vader = SentimentIntensityAnalyzer()
# Set column names
columns = ['ticker', 'date', 'time', 'headline']
# Convert the parsed_news list into a DataFrame called 'news_df'
news_df = pd.DataFrame(parsed_news, columns=columns)

# Iterate through the headlines and get the polarity scores using vader
scores = news_df['headline'].apply(vader.polarity_scores).tolist()
# Convert the 'scores' list of dicts into a DataFrame
scores_df = pd.DataFrame(scores)

# Join the DataFrames of the news and the list of dicts
news_df = news_df.join(scores_df, rsuffix='_right')
# Convert the date column from string to datetime
news_df['date'] = pd.to_datetime(news_df.date).dt.date
news_df.tail()


# In[64]:


# Group by each ticker and get the mean of all sentiment scores
mean_scores = news_df.groupby(['ticker']).mean()
mean_scores.head()


# In[65]:


# Get Current Price, Sector and Industry of each Ticker
# as an example this is the information that the api returns for Google
tickerdata = yf.Ticker('GOOG')
tickerdata.info


# In[66]:


# Now, we do it for all the companies and extract the necessary information

sectors = []
industries = []
prices = []
for ticker in tickers:
    print(ticker)
    tickerdata = yf.Ticker(ticker)
    prices.append(tickerdata.info['regularMarketPrice'])
    sectors.append(tickerdata.info['sector'])
    industries.append(tickerdata.info['industry'])

d = {'Sector': sectors, 'Industry': industries, 'Price': prices, 'No. of Shares': n_shares}
df_info = pd.DataFrame(data=d, index = tickers)
df_info


# In[67]:


# we  create a column of the total value of each share
df_info['Total Stock Value in Portfolio'] = df_info['Price']*df_info['No. of Shares']
df_info.head()


# In[68]:


df = mean_scores.join(df_info)
df = df.rename(columns={"compound": "Sentiment Score", "neg": "Negative", "neu": "Neutral", "pos": "Positive"})
df = df.reset_index()
df.head()


# In[69]:


#Now we generate the required treemap
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import plotly
import plotly.express as px


# In[70]:


fig = px.treemap(df, path=[px.Constant("Sectors"), 'Sector', 'Industry', 'ticker'], values='Total Stock Value in Portfolio',
                  color='Sentiment Score', hover_data=['Price', 'Negative', 'Neutral', 'Positive', 'Sentiment Score'],
                  color_continuous_scale=['#FF0000', "#000000", '#39FF14'],
                  color_continuous_midpoint=0)

fig.data[0].customdata = df[['Price', 'Negative', 'Neutral', 'Positive', 'Sentiment Score']].round(3) # round to 3 decimal places
fig.data[0].texttemplate = "%{label}<br>%{customdata[4]}"

fig.update_traces(textposition="middle center")
fig.update_layout(margin = dict(t=30, l=10, r=10, b=10), font_size=20)

plotly.offline.plot(fig, filename='stock_sentiment.html') # this writes the plot into a html file and opens it
fig.show()


# In[ ]:




