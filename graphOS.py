import dash
import json
import networkx as nx
import pandas as pd
from dash import dcc
from dash import html
import plotly.graph_objects as go

from colour import Color
from textwrap import dedent as d

# CSS stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'GraphOS'

year_range = [2022, 2023]
ACCOUNT = "C3PO01"

# Read data and create network graph
def network_graph(year_range, account_filter, current_year, customer_type='All'):
    edge1 = pd.read_csv('/Users/ihortresnystkyi/Documents/pythonProject2/edge1.csv')
    node1 = pd.read_csv('/Users/ihortresnystkyi/Documents/pythonProject2/node1.csv')

    # Create datetime and filter data by year, account
    edge1['Datetime'] = pd.to_datetime(edge1['Date'], format='%m/%d/%Y')
    edge1_filtered = edge1[(edge1['Datetime'].dt.year >= current_year) & (edge1['Datetime'].dt.year <= current_year)]
    edge1 = edge1[(edge1['Datetime'].dt.year >= year_range[0]) & (edge1['Datetime'].dt.year <= year_range[1])]

    accountSet = set(edge1['Source']).union(edge1['Target'])

    # Add the account to search to the first shell
    shells = []
    shell1 = []
    shell1.append(account_filter)
    shells.append(shell1)
    shell2 = []
    for ele in accountSet:
        if ele != account_filter:
            shell2.append(ele)
    shells.append(shell2)

    # Takes this DataFrame as input and creates a MultiDiGraph object G with nodes and edges defined by the 'Source' and 'Target' columns of edge1.
    G = nx.from_pandas_edgelist(edge1, 'Source', 'Target', ['Source', 'Target', 'TransactionAmt', 'Date'],
                                create_using=nx.DiGraph())

    # Add attributes to nodes and edges
    nx.set_node_attributes(G, node1.set_index('Account')['CustomerName'].to_dict(), 'CustomerName')
    nx.set_node_attributes(G, node1.set_index('Account')['Type'].to_dict(), 'Type')

    # Create a list of colors for the nodes based on the CustomerType
    if len(shell2) > 1:
        pos = nx.drawing.layout.shell_layout(G, shells)
    else:
        pos = nx.drawing.layout.spring_layout(G)
    for node in G.nodes():
        G.nodes[node]['pos'] = list(pos[node])

    if len(shell2)==0:
        traceRecode = []

        node_trace = go.Scatter(x=tuple([1]), y = tuple([1]), text = tuple([str(account_filter)]), textposition = "bottom center", mode = 'markers+text', marker={'size': 50, 'color': 'red'})
        traceRecode.append(node_trace)

        node_trace1 = go.Scatter(x=tuple([1]), y = tuple([1]), text = tuple([str(account_filter)]), textposition = "bottom center", mode = 'markers+text', marker={'size': 50, 'color': 'red'}, opacity=0)
        traceRecode.append(node_trace1)


        figure = {
            'data': traceRecode,
            'layout': go.Layout(title='Interactive Network Graph', showlegend=False,
                                margin={'b': 40, 'l': 40, 'r': 10, 't': 10},
                                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                height=600)
        }
        return figure

    # Create a list of colors for the nodes based on the CustomerType
    traceRecode = []
    colors = list(Color("red").range_to(Color("blue"), len(G.edges())))
    colors = ['rgb' + str(x.rgb) for x in colors]

    # Create the edges and nodes
    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = float(G.edges[edge]['TransactionAmt']) / max(edge1['TransactionAmt']) * 10
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': weight},
                           marker=dict(color=colors[index]),
                           line_shape='spline',
                           opacity=1)
        traceRecode.append(trace)
        index = index + 1

    # Create the nodes
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], textposition="bottom center", mode='markers+text',
                            hoverinfo='text', marker={'size': 50, 'color': 'red'})

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hovertext = "From: " + str(G.edges[edge]['Source']) + "<br>" + "To: " + str(
            G.edges[edge]['Target']) + "<br>" + "TransactionDate: " + str(
            G.edges[edge]['TransactionAmt']) + "<br>" + "TransactionDate: " + str(G.edges[edge]['Date'])
        node_trace['x'] += tuple([(x0 + x1) / 2])
        node_trace['y'] += tuple([(y0 + y1) / 2])
        node_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(node_trace)


    # Create the nodes
    figure = {
        'data': traceRecode,
        'layout': go.Layout(title='Interactive Network Graph', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 10, 't': 10},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            annotations=[
                                    dict(
                                        ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                        ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                        x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                        y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                        showarrow=True,
                                        arrowhead=3,
                                        arrowsize=4,
                                        arrowwidth=1,
                                        opacity=1
                                    ) for edge in G.edges]
                            )}
    return figure

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

############################## Define the app layout ##############################

app.layout = html.Div([

    html.Div([html.H1("Transaction Network Graph")],
             className="row",
             style={'textAlign': "center"}),

    html.Div(
        className="row",
        children=[

            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Time Range To Visualize**
                            Slide the bar to define year range.
                            """)),
                        dcc.Slider(
                            id='time-slider',
                            min=year_range[0],
                            max=year_range[1],
                            step=1,
                            value=year_range[0],
                            marks={str(year): str(year) for year in range(year_range[0], year_range[1] + 1)},
                            updatemode='drag'
                        ),
                        html.Div(id='slider-output-container'),

                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=2010,
                                max=2019,
                                step=1,
                                value=[2010, 2019],
                                marks={
                                    2010: {'label': '2010'},
                                    2011: {'label': '2011'},
                                    2012: {'label': '2012'},
                                    2013: {'label': '2013'},
                                    2014: {'label': '2014'},
                                    2015: {'label': '2015'},
                                    2016: {'label': '2016'},
                                    2017: {'label': '2017'},
                                    2018: {'label': '2018'},
                                    2019: {'label': '2019'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')
                        ],
                        style={'height': '300px'}
                    ),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Account To Search**
                            Input the account to visualize.
                            """)),
                            dcc.Input(id="input1", type="text", placeholder="Account"),
                            html.Div(id="output")
                        ],
                        style={'height': '300px'}
                    )
                ]
            ),


            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(year_range, ACCOUNT, year_range[0]))],
            ),


            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Hover Data**
                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '400px'}),

                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Click Data**
                            Click on points in the graph.
                            """)),
                            html.Pre(id='click-data', style=styles['pre'])
                        ],
                        style={'height': '400px'})
                ]
            )
        ]
    )
])

################## Callback to display hover data ########################

# Updates the hover data based on the slider value
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    if hoverData is None:
        return "No data available"
    return json.dumps(hoverData, indent=2)


# Updates the click data based on the slider value
@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return "No data available"
    return json.dumps(clickData, indent=2)


# Updates the slider value based on the slider value
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [
        dash.dependencies.Input('my-range-slider', 'value'),
        dash.dependencies.Input('input1', 'value'),
        dash.dependencies.Input('time-slider', 'value'),
    ]
)
def update_output(year_range, input1, current_year):
    return network_graph(year_range, input1, current_year)




if __name__ == '__main__':
    app.run_server(debug=True)


