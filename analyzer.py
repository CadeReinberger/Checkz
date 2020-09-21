from storer import read_stored_data, update
import math as m
import numpy as np
import networkx as nx
from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn.cluster import KMeans
import matplotlib
import pydot
from PIL import Image, ImageDraw, ImageFont
import re

#number of cryptocurrencies to include in the tree
NUM_TREE_VERTICES = 51  
#end file locations for key images
W_DIR = 'C:/Users/willi/OneDrive/Documents/python_scripts/checkz/'
SVG_FILE_LOC = W_DIR + 'data/viz_exp.svg' 
PNG_FILE_LOC = W_DIR + 'data/viz_exp.png' 
LEG_FILE_LOC = W_DIR + 'data/w_leg.png'

def strip_data():
    '''
    Read in the data from the excel file storing it, and preprocess it, by
    taking the correct number of coins from the top

    Returns
    -------
    df : pandas dataframe
        dataframe containing the time-series price data for each crypto
    nd : dictionary
        a dictionary of the cmc ids of each crypto associated to its name

    '''
    df, nd = read_stored_data()
    df.dropna() #get rid of any rows that aren't filled
    #take the correct number of rows
    num_rows =  min(NUM_TREE_VERTICES, len(df.index))
    df = df[:num_rows].T
    return df, nd

def get_legend():
    '''
    creates a legend for the image and saves it to a png
    
    Returns
    -------
    img : PIL Image
        a PIL image, 250 x 1000, containing the key written out
    '''
    #first, actually strip the dictionary
    df, nd = strip_data()
    sml_dict = {c : nd[c] for c in df.columns}
    pairs = sml_dict.items()
    #create the PIL image
    img = Image.new('RGB', (300, 1500), color = 'white')
    fnt = ImageFont.truetype("arial.ttf", 20)
    leg = ImageDraw.Draw(img)
    n = len(pairs) #number of coins in the legend
    inc = 1450 // n #size to move down between each legend elemeent
    max_len = max([len(str(val)) for key, val in pairs]) #longest cmc id
    for ind, (key, val) in enumerate(pairs):
        #the message here aligns things with python spacing
        msg = (str(val) + ':').ljust(max_len + 3, ' ') + key
        #in arial, spaces are half-width, so we double the length of each
        msg = re.sub(' ', '  ', msg)
        leg.text((25, 25 + inc * ind), msg, font = fnt, fill = (0, 0, 0))
    return img

def compute_mst():
    '''
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

    Returns
    -------
    graph : Pydot graph
        A graph object containing the layout of the visualized data

    '''
    df, nd = strip_data() #read in daata
    #inverse dictionary of the names dictionary
    dn = {str(v) : k for k, v in nd.items()}
    #compute the minimum spanning tree for the data, by spearman correlation
    spearman_rho = df.corr(method = 'spearman')
    G = nx.Graph()
    vertices = [str(nd[col]) for col in df.columns]
    for vertex in vertices:
        G.add_node(vertex)
    #for each pair of cryptos
    for i in range(1, len(vertices)):
        for j in range(i):
            #compute the weight based on the spearman correlation
            w = 1 - m.fabs(spearman_rho[df.columns[i]][df.columns[j]])
            #add the edge in with the weight
            G.add_edge(vertices[i], vertices[j], weight = w)
    #actually compute the minimal spanning tree for this graph
    mst = nx.algorithms.tree.mst.minimum_spanning_tree(G, weight="weight", 
                                                          algorithm="kruskal", 
                                                          ignore_nan=True)
    edges = [(a, b) for a, b, c in nx.convert.to_edgelist(mst)] #edges of mst
    
    #compute the PCA for the data to compute node colors
    ppdf = df #copy the dataframe, so that we can standardize each column
    #shift and divide all the columns so each row has mean 0 variance 1
    for col in ppdf.columns:
        ppdf[col] = preprocessing.scale(ppdf[col])
    pca = PCA(n_components = 3) #3 components because 3 dimensions to color
    #compute the principle components and apply it
    pca.fit(ppdf.T) 
    pcad = pca.transform(ppdf.T)
    #a sigmoid function to map the pca projections into (0, 1) to be hsv vals
    sig = lambda x : .5 + .5 * np.tanh(2*x)
    #.736 here comes from maling sure that the greatest hsv value is ~.95
    mults = [.736 / max([m.fabs(a[i]) for a in pcad]) for i in range(3)]
    for i in range(len(pcad)):
        for j in range(3):
            #modify results of pca to be in the proper range
            pcad[i][j] = sig(pcad[i][j] * mults[j])
    col_dict = {}
    text_col_dict = {}
    #create a dictiory to the colors and text color for each coin
    for i in range(len(pcad)):
        coin = str(nd[ppdf.columns[i]])
        col = matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb(pcad[i]))
        col_dict[coin] = col
        #if its too dark make the text white
        text_col_dict[coin] = 'black' if pcad[i][2] > .35 else 'white'
        
    #simply compute node sizes with exponential decay from 1.5 to .5
    sz = lambda i : 1.5 * m.exp(-1.5 * (i * m.log(3) / len(df.columns)))
    sz_dict = {str(nd[df.columns[i]]) : sz(i) for i in range(len(df.columns))}
    
    #compute shapes of each node using k-means clustering
    #note also that the k means uses the standardized data
    km = KMeans(n_clusters = 6, algorithm = 'full', random_state = 42)
    km.fit(ppdf.T)
    #arbitrarily chosen just to be different shapes
    shapes = ['box', 'ellipse', 'triangle', 'diamond', 'pentagon', 'octagon']
    #create a dictionary of the results
    get_shape = lambda i : shapes[km.predict([ppdf[ppdf.columns[i]]])[0]]
    shapes_dict = {str(nd[df.columns[i]]) : get_shape(i)
                   for i in range(len(df.columns))}
    
    #compute the length of every edge using linear corellation
    edge_lengths_dict = {}
    edge_weight_dict = {}
    cor = df.corr(method = 'pearson')
    for a, b in edges:
        edgestr = a + '--' + b
        c = m.fabs(cor[dn[a]][dn[b]])
        #the length ranges from 1.5  to 3.5 for strength of the correlation
        l = 3.5 - 1.5 * c 
        edge_lengths_dict[edgestr] = l
        edge_weight_dict[edgestr] = c
        
    #compute the color of every edge using spearman correlation
    edge_cols_dict = {}
    #uses a quadratic bezier curve to interpolate between these control points
    red = np.array([1, 0, 0])
    mid = np.array([.5, .5, .5]) #pure gray color chosen
    green = np.array([0, 1, 0])    
    for a, b in edges:
        edgestr = a + '--' + b
        rho = spearman_rho[dn[a]][dn[b]]
        t = .5 + .5 * rho #the paramater along the quadratic bezier
        color = (1 - t) ** 2 * red + 2 * (1-t) * t * mid + t ** 2 * green
        col_str = matplotlib.colors.to_hex(color)
        edge_cols_dict[edgestr] = col_str
        
    #combine all of the analysis above to produce a graph drawing
    graph = pydot.Dot(graph_type = 'graph')
    #stores the pydot.Node objects, to define edges between them
    nodes_dict = {} 
    for node in df.columns:
        name = str(nd[node])
        #create the node with all of the desired properties and add it
        n = pydot.Node(name=name, style='filled', fillcolor=col_dict[name],
                       width=sz_dict[name], height=sz_dict[name],
                       shape=shapes_dict[name], fontcolor=text_col_dict[name])
        nodes_dict[name] = n
        graph.add_node(n)
    for a, b in edges:
        es = a + '--' + b #string to access the edge in the edge dictionaries
        #create the edge with the desired propeties
        e = pydot.Edge(nodes_dict[a], nodes_dict[b], len=edge_lengths_dict[es],
                       color=edge_cols_dict[es], weight=edge_weight_dict[es])     
        graph.add_edge(e)
    #set the root of the graph
    root = str(nd[df.columns[0]])
    graph.set_root(root)
    
    return graph

def visualize_mst():
    '''
    this actually updates the data and runs and saves the visualization
    '''
    update() #update data from the cmc api, logging to the excel & json files
    mst = compute_mst() #actually compute the disred graph
    #render the graph using spring physics and save it to an SVG
    mst.write_svg(SVG_FILE_LOC, prog = 'neato') 
    #save a png on its own
    mst.write_png(PNG_FILE_LOC, prog = 'neato')
    #compute and save a png with the legend on the end
    #get the images
    main_img = Image.open(PNG_FILE_LOC)
    leg_img = get_legend()
    #compute the dimensions
    res_img_width = main_img.width + leg_img.width
    res_img_height = max(main_img.height, leg_img.height)
    res_image_dim = (res_img_width, res_img_height)
    #create the image with legend
    fin_img = Image.new('RGB', res_image_dim, color = 'white')
    fin_img.paste(main_img, (0, 0))
    fin_img.paste(leg_img, (main_img.width, 0))
    #save the image with legend
    fin_img.save(LEG_FILE_LOC)
    
visualize_mst()