#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import networkx as nx
import plotly.graph_objs as go
import pandas as pd
import json

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Musician Network - Eric Dolphy"

# read data
df = pd.read_csv("ericDolphyDiscog1.csv", encoding='utf_8')

K = 0.009 # should now be established by slider
newData = df

##############################################################################################################################################################
def network_graph(K, newData):
    # get edge list
    newData['new_col'] = list(zip(newData.Album, newData.Artist))
    edge_list = list(newData['new_col'])
    # get nodes
    node_list = list(newData.Album.unique())
    artists = list(newData.Artist.unique())
    node_list.extend(artists)

    # create graph
    G = nx.Graph()
    # add nodes 
    for i in node_list:
        G.add_node(i)

    # add edges from this   
    for i,j in newData.iterrows():
        G.add_edges_from([(j["Album"],j["Artist"])])

    # object of positions whislt set layout 
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # add positions of the nodes to the graph
    for n, p in pos.items():
        G.nodes[n]['pos'] = p

    # add nodes and edges to the plotly api    
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='RdBu',
            reversescale=True,
            color= [],
            size=15,
            colorbar=dict(
                thickness=10,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=0)))

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    # coloring based on the number of connections of each node.
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        # add to hover fly ouy
        node_info = adjacencies[0] #+' # of connections: '+str(len(adjacencies[1]))
        node_trace['text']+=tuple([node_info])    

    # plot the figure    
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Network graph examining the musicians that Eric Dolphy played with during his short and prolific career.<br>Hover at the top right for more controls. Click and drag on the graph to zoom in. Double click to to go back.<br><br>',
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    clickmode='event+select',
                    width=1000,
                    height=850,
                    margin=dict(b=20,l=5,r=5,t=100),
                    annotations=[ dict(
                        text="",
                        showarrow=False,
                        xref="paper", yref="paper") ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    fig.layout.plot_bgcolor='rgba(247, 247, 247, 1)'  
    return(fig)

######################################################################################################################################################################
# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    #########################Title
    html.Div([html.H1("Eric Dolphy Musician Network")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown("""
                            **Adjust Network Layout**
                            Slide to move the nodes. You can use this to avoid overlap or place elements where you prefer on the graph.
                            """),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Slider(
                                id='slider_updatemode',
                                min=0.00,
                                max=1.00,
                                step=0.01,
                                value=0.09,
                                marks={
                                    0:{'label': '0.00'},
                                    1:{'label': '1.00'}
                                },
                                updatemode='drag'
                            ),
                            html.Br(),
                            html.Div(id='updatemode-output-container')
                        ],
                        style={'height': '300px'}
                    ),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown("""
                                    **Select Albums**
                                    Select the albums to be used in the graph. Select as many albums as you like. You can tune the graph using the slider above when the network expands.
                                    """),
                            html.Div(
                                className="twelve columns",
                                children=[
                                    dcc.Dropdown(
                                        id='dropdown',
                                        options=[
                                            {'label': 'At the Five Spot Volume One', 'value': 'LP: At the Five Spot Volume One'},
                                            {'label': 'At The Five Spot Volume Two', 'value': 'LP: At The Five Spot Volume Two'},
                                            {'label': 'Candid Dolphy', 'value': 'LP: Candid Dolphy'},
                                            {'label': 'Caribe', 'value': 'LP: Caribe'},
                                            {'label': 'Conversations', 'value': 'LP: Conversations'},
                                            {'label': 'Dash One', 'value': 'LP: Dash One'},
                                            {'label': 'Eric Dolphy in Europe', 'value': 'LP: Eric Dolphy in Europe'},
                                            {'label': 'Eric Dolphy Quintet featuring Herbie Hancock', 'value': 'LP: Eric Dolphy Quintet featuring Herbie Hancock'},
                                            {'label': 'Far Cry', 'value': 'LP: Far Cry'},
                                            {'label': 'Fire Waltz', 'value': 'LP: Fire Waltz'},
                                            {'label': 'Here and There', 'value': 'LP: Here and There'},
                                            {'label': 'Hot and Cool Latin', 'value': 'LP: Hot and Cool Latin'},
                                            {'label': 'Iron Man', 'value': 'LP: Iron Man'},
                                            {'label': 'Last Date', 'value': 'LP: Last Date'},
                                            {'label': 'Last Recordings', 'value': 'LP: Last Recordings'},
                                            {'label': 'Magic with Ron Carter', 'value': 'LP: Magic with Ron Carter'},
                                            {'label': 'Naima', 'value': 'LP: Naima'},
                                            {'label': 'Other Aspects', 'value': 'LP: Other Aspects'},
                                            {'label': 'Out There', 'value': 'LP: Out There'},
                                            {'label': 'Out to Lunch', 'value': 'LP: Out to Lunch'},
                                            {'label': 'Outward Bound', 'value': 'LP: Outward Bound'},
                                            {'label': 'Status', 'value': 'LP: Status'},
                                            {'label': 'Stockholm Sessions', 'value': 'LP: Stockholm Sessions'},
                                            {'label': 'The Complete Uppsala Concert', 'value': 'LP: The Complete Uppsala Concert'},
                                            {'label': 'The Illinois Concert', 'value': 'LP: The Illinois Concert'},
                                            {'label': 'Vintage Dolphy', 'value': 'LP: Vintage Dolphy'}
                                        ],
                                        value=['LP: Dash One', 'LP: Iron Man'],
                                        multi=True
                                        ) ,
                                    html.Br(),
                                ],
                                style={'height': '300px'}
                            ),
                        ]
                    ),
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my_graph",
                                    figure= network_graph(K, newData))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown("""
                            **Forward**
                            "Eric Dolphy was a true original with his own distinctive styles on alto, flute, and bass clarinet. His music fell into the “avant-garde” category yet he did not discard chordal improvisation altogether (although the relationship of his notes to the chords was often pretty abstract). While most of the other “free jazz” players sounded very serious in their playing, Dolphy’s solos often came across as ecstatic and exuberant. His improvisations utilized very wide intervals, a variety of nonmusical speechlike sounds, and its own logic. Although the alto was his main axe, Dolphy was the first flutist to move beyond bop (influencing James Newton) and he largely introduced the bass clarinet to jazz as a solo instrument. He was also one of the first (after Coleman Hawkins) to record unaccompanied horn solos, preceding Anthony Braxton by five years." SOURCE:http://www.bluenote.com/artist/eric-dolphy/
                            """),
                            #html.Pre(id='hover_data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

#                     html.Div(
#                         className='twelve columns',
#                         children=[
#                             dcc.Markdown("""
#                             **Click Data**
#                             Click on points in the graph.
#                             """),
#                             html.Pre(id='click_data', style=styles['pre'])
#                         ],
#                         style={'height': '400px'})
                ]
            )
        ]
    )
])

###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my_graph', 'figure'),
    [dash.dependencies.Input('dropdown', 'value'), dash.dependencies.Input('slider_updatemode', 'value')])
def update_output(dropdown, value):
    newData = df[df.Album.isin(dropdown)]
    K = value
    return network_graph(K, newData)


if __name__ == '__main__':
    app.run_server(debug=False) 


# In[ ]:




