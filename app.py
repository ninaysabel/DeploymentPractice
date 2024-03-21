# import dependencies 
from dash import Dash, dcc, html 
import plotly.express as px 
import pandas as pd
from dash.dependencies import Input, Output

df = pd.read_csv("gdp_pcap.csv")

#df.head()

# the dataset represents thousands with a "k" at the end and the graphs weren't accurately depicting the information
# this was my line of thinking to fix it: if last character is k, then index out the last character then replace by n-1 character/value and multiply by 1000 as int


def process_gdp(value):
    if isinstance(value, str) and value[-1] == 'k':
        return int(float(value[:-1])) * 1000
    return value


for col in df.columns[1:]:
    df[col] = df[col].apply(process_gdp)

#df.head()

# load css stylesheet and initialize app
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
app = Dash(__name__, external_stylesheets=stylesheets) 
server = app.server

# year and gdpPerCap as separate columns
df_melted = df.melt(id_vars='country', var_name='year', value_name='gdpPerCap')

# convert 'year' column to integers so that it's able to be graphed (can't graph a string)
df_melted['year'] = df_melted['year'].astype(int)

# app building
app.layout = html.Div([
    html.Div(children=[ # title and description below
        dcc.Markdown('''
# Basic UI- International Gross Domestic Product per Capita
 ###### DS 4003 // Nina Ysabel Alinsonorin 
###### The following conveys information acquired from a CSV depicting the annual Gross Domestic Product per Capita for all countries, spanning from the year 1800 to 2100. This data is able to be manipulated by the user in the form of a multi-select dropdown menu and range slider. In doing so, the user is able to view the GDP per Capita for each selected country and timeframe on the line graph below.
'''),
        html.Br(), # line break
        html.Div(className='row', children=[
            html.Div(className='six columns', children=[
                html.Label('Country Dropdown Menu: Select Countries'), # drop down menu parameters
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in df['country']],
                    value=[],
                    multi=True
                )
            ]),
            html.Div(className='six columns', children=[
                html.Label('Slider: Select a Range of Years from 1800 - 2100'), # slider parameters
                dcc.RangeSlider(
                    id='range-year-slider',
                    min=1800,
                    max=2100,
                    step=1,
                    marks={i: str(i) for i in range(1800, 2101, 25)},
                    value=[1800, 2100]
                )
            ]),
        ]),
        html.Br(), # line break (for aesthetic purposes so it doesn't look too crammed)
        html.Label('gdpPerCapita Graph'), # gdp graph
        dcc.Graph(
            id='gdpPerCapita-graph',
            figure=px.line(title='GDP Per Capita Over Time')
        )
    ])

])

# callback function used to update the graph based on user selection
@app.callback(
    Output('gdpPerCapita-graph', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('range-year-slider', 'value')]
)
def update_graph(selected_countries, selected_years):
    filtered_df = df_melted[df_melted['country'].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df['year'].between(selected_years[0], selected_years[1])]
    fig = px.line(filtered_df, x='year', y='gdpPerCap', color='country', title='GDP Per Capita Over Time') # specifying graph specifics (axes, how to fill in 'color' of graph, title)
    fig.update_layout(xaxis_title='Year', yaxis_title='GDP Per Capita')
    return fig

# run app 
if __name__ == '__main__':
    app.run_server(debug=True,
            port = 8052)
