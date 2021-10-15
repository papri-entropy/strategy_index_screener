#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from secrets import IEX_CLOUD_API_TOKEN


# In[2]:


stocks = pd.read_csv('sp_500_stocks.csv')
type(stocks)
stocks


# In[3]:


symbol = "AAPL"
api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}"
data = requests.get(api_url).json()


# In[4]:


price = data['latestPrice']
market_cap = data['marketCap']


# In[5]:


my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)


# In[6]:


final_dataframe.append(
    pd.Series(
    [
        symbol,
        price,
        market_cap,
        "N/A"
    ],
    index = my_columns
    ),
    ignore_index = True)


# In[7]:


final_dataframe = pd.DataFrame(columns = my_columns)
for stock in stocks['Ticker']:
    api_url = f"https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(
        pd.Series(
        [
            stock,
            data['latestPrice'],
            data['marketCap'],
            'N/A'
        ],
        index = my_columns),
    ignore_index = True
    )


# In[8]:


#final_dataframe


# In[9]:


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# In[10]:


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = list()
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#   print(symbol_strings[i])
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
#    print(batch_api_call_url)
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
        pd.Series(
        [
            symbol,
            data[symbol]['quote']['latestPrice'],
            data[symbol]['quote']['marketCap'],
            'N/A'
        ],
        index = my_columns),
        ignore_index = True
        )
final_dataframe


# In[32]:


portfolio_size = input("Enter the value of your portfolio: ")
try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number! \nPlease try again:")
    portfolio_size = input("Enter the value of your portfolio: ")
    val = float(portfolio_size)


# In[33]:


position_size = val / len(final_dataframe.index)
for i in range(0, len(final_dataframe.index)):
    #final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size / final_dataframe["Stock Price"][i])
    final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size / final_dataframe.loc[i, "Stock Price"])

final_dataframe          


# In[61]:


writer = pd.ExcelWriter("recommended trades.xlsx", engine = "xlsxwriter")
final_dataframe.to_excel(writer, "Recommended Trades", index = False)


# In[62]:


background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
    {
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)
dollar_format = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)
integer_format = writer.book.add_format(
    {
        'num_format': '0',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)


# In[63]:


# writer.sheets["Recommended Trades"].set_column('A:A', 18, string_format)
# writer.sheets["Recommended Trades"].set_column('B:B', 18, string_format)
# writer.sheets["Recommended Trades"].set_column('C:C', 18, string_format)
# writer.sheets["Recommended Trades"].set_column('D:D', 18, string_format)
# writer.save()


# In[64]:


column_formats = {
    'A': ['Ticker', string_format],
    'B': ['Stock Price', dollar_format],
    'C': ['Market Capitalization', dollar_format],
    'D': ['Number of Shares to Buy', integer_format]
}


# In[65]:


for column in column_formats.keys():
    writer.sheets["Recommended Trades"].set_column(f"{column}:{column}", 18, column_formats[column][1])
    writer.sheets["Recommended Trades"].write(f"{column}1", column_formats[column][0],column_formats[column][1])

writer.save()

