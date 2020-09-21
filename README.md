# Checkz
 An analysis-rich MST visualization of time-series data of cryptocurrency prices

# The Visualization Algorithm

Compute the minimum spanning tree with a bunch of data visualization bells
and whistles. In particualar. 
1. Each node represents a cryptocurrency
2. Each node is labeled by it's coin market cap id
3. The size of each node is determined roughly by its market cap (in
   more detail, it's determined by its coinmarketcap ranking)
4. The color of each node is determined by computing the projection of
   its first three principle components after standardizing all the 
   data as the hsv color
5. The color of each edge goes from red to gray to green based on the 
   spearman correlation between the two cryptocurrencies involved
6. The length of each edge is begun and weighted within the graph 
   drawing algorithm based on spring physics by distance coming from 
   the absolute value of the pearson correlation, so coins that have 
   simple relations are closer togther. 
7. The actual edges themselves are a minimal spanning tree of the top
   chosen number of cryptocurencies where edge weight is determined by
   spearman correlation
   
Roughly speaking, this is just kind of a bunch of information put together in a way that's hopefully a bit intuitive. As such, the idea is to help one be able to see somewhat subtler trends in the data. 

A key is added in the case that the output is saved as a PNG, but because this image is quite large, an SVG is superior for seeing the data. The SVG image is without key, however. 

# Gathering and Storing Time-Series Data for Cryptocurrency Prices

About half of the code is just about getting and playing with the price data for cryptocurrencies. The source of this data is the CoinMarketCap (CMC) API, but getting historical data from the API requires a paid-tier amount of acess. Thus, the batch and the bit of VBScript are all about creating a scheduled command (the windows equivalent of cronjob) to run the python script periodically to update datasets and re-compute the visualization. 

The storage of the data is intended to be human-readible. Thus, the pandas dataframe with the time series data writes to and reads from excel directly, using the cryptocurrency name itself, instead of the cmc id which is what the visualziation uses, and the names and ids dictionary is saved as a json prettily instead of pickled. This way you can see the data, and also its visualization. 

# Gallery

## High Frequency

Data collected every 1 minute for 2 hours
![Example One](/data/notable_examples/example_viz.svg)

## Low Frequency 
Data collected once an hour for various time intervals

![Example Two](/data/notable_examples/example_viz_2.svg)

##

![Example Three](/data/notable_examples/example_viz_3.svg)

##

![Example Four](/data/notable_examples/example_viz_4.svg)

##

This one illustrates the key, which is a useful feature when one has a better idea of the structure of the data and wants to be more precise about specific cryptocurrencies
![Example Five](/data/notable_examples/example_viz_5.png)
