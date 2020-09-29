# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

df_episodes = pd.read_csv('_RES/data/Dolores_All_Episodes.csv', index_col=0)
df_shows = pd.read_csv('_RES/data/Dolores_TV_Shows.csv', index_col=0)
df_episodes.columns
df_episodes['airdate']
df_episodes['airdate'] =  pd.to_datetime(df_episodes['airdate'], infer_datetime_format=True)
df_episodes['airdate']
df_episodes['imdb_rating'].count()
df_episodes['viewers'].values
df_episodes['viewers'] = df_episodes['viewers'].apply(lambda x: 0 if x == '' else x)
# df_episodes['viewers'].isnull().sum()
# df_episodes['viewers'].fillna(0,inplace=True)
# df_episodes['viewers'].isnull().sum()
df_episodes['viewers'] = df_episodes['viewers'].interpolate(method='linear', limit_direction='forward', axis=0)

fig = px.bar(df_shows, x="title", y="imdb_rating", color="genre")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

fig2 = px.scatter(df_episodes, x='airdate', y='imdb_rating', color='show_title', hover_name='title', size='viewers', size_max=60)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Dolores v0.1',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),

    html.Div(children='''
        Visualizing TV Show data
    ''', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='shows_rating',
        figure=fig
    ),

    dcc.Graph(
        id='episodes',
        figure=fig2
    ),

    html.Div(children=[
        html.H4(children='TV Show Data (2020)'),
        generate_table(df_shows)], style={
            'textAlign': 'center',
            'color': colors['text']
        })
])

if __name__ == '__main__':
    app.run_server(debug=True)
