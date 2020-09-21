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
