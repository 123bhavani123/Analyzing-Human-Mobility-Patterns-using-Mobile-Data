import networkx as nx

def build_transition_graph(df):
    df['location'] = df[['latitude', 'longitude']].astype(str).agg(','.join, axis=1)
    df = df.sort_values(['user_id', 'timestamp'])

    G = nx.DiGraph()
    for uid, user_data in df.groupby('user_id'):
        locations = user_data['location'].tolist()
        for i in range(len(locations) - 1):
            G.add_edge(locations[i], locations[i+1])
    
    nx.write_gexf(G, r"C:\Users\Bhavani\Desktop\Mobility\transition_graph.gexf")
    return G
