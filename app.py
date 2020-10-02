# -*- coding: utf-8 -*-
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime as dt

def generate_table(dataframe, max_rows=11):
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


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#EFEFEF',
    'text': '#3F5765'
}

df_episodes = pd.read_csv('_RES/data/Dolores_All_Episodes.csv', index_col=0)
df_shows = pd.read_csv('_RES/data/Dolores_TV_Shows.csv', index_col=0)
df_shows.columns
df_episodes.columns
df_episodes['year'] = pd.DatetimeIndex(df_episodes['airdate']).year
df_episodes['airdate']
df_episodes['airdate'] =  pd.to_datetime(df_episodes['airdate'], infer_datetime_format=True)
df_episodes['airdate']
df_episodes['imdb_rating'].count()
df_episodes['viewers'].values
df_episodes['viewers'] = df_episodes['viewers'].apply(lambda x: 0 if x == '' else x)
df_episodes['viewers'] = df_episodes['viewers'].interpolate(method='linear', limit_direction='forward', axis=0)

info_column_labels = {'title': 'Show Title',
           'imdb_rating': 'IMDB Rating',
           'genre': 'Genre',
           'link_wiki': 'Wikipedia Link',
           'link_imdb': 'IMDB Link'}
info_columns = ['title', 'link_wiki', 'link_imdb']
df_shows_info = df_shows[info_columns]
df_shows_info = df_shows_info.rename(columns=info_column_labels)
df_episodes_dti = df_episodes.copy()
df_episodes_dti.index = pd.DatetimeIndex(df_episodes.airdate)

df_episodes[df_episodes['title'] == "The Iron Throne"]

labels = dict(title="Show ",
              imdb_rating="IMDB Rating (0-10) ",
              airdate="First Airdate ",
              show_title="Show ",
              viewers="U.S. Viewers (millions) ")

fig1 = px.bar(df_shows,
              x="title",
              y="imdb_rating",
              color='title',
              title="IMDB Show Rating (in descending order)",
              labels=labels,
              template="none",
              color_discrete_sequence=px.colors.qualitative.Plotly)

num_slices = 11
theta = [(i + 1.5) * 360 / num_slices for i in range(num_slices)]
width = [360 / num_slices for _ in range(num_slices)]
width

fig3 = px.bar_polar(df_episodes,
                    r="season",
                    theta="show_title",
                    color="show_title",
                    title="Episodes per Show",
                    template="none",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                    )

fig1.update_layout(
    # plot_bgcolor=colors['background'],
    # paper_bgcolor=colors['background'],
    font_color=colors['text'],
    height=800,
    xaxis={'categoryorder': 'total descending'}
)

fig1.update_yaxes(range=[8, 10])

fig3.update_layout(
    polar_radialaxis_ticks="",
    polar_radialaxis_showticklabels=False,
    plot_bgcolor=colors['background'],
    # paper_bgcolor=colors['background'],
    font_color=colors['text'],
    height=800,
)


app.layout = html.Div(
    style={
            'textAlign': 'center',
            'marginTop': 50},
    children=[
        html.H1(children='Dolores v 0.1',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),
        html.H5(children='''
            Visualizing TV Show data
            ''',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),
        html.Div(children=[
            dcc.Graph(
                id='shows_rating',
                figure=fig1
            )
            ],
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'margin-bottom': 50,
            }),

        html.Div(
            style={'textAlign': 'center',
                   'color': colors['text'],
                   'backgroundColor': colors['background'],
                   'padding-top': 50,
                   'padding-bottom': 50,
                   },
            children=[
                dcc.Graph(
                    id='episodes',
                ),
                dcc.RangeSlider(
                    id='episodes_range-slider',
                    min=df_episodes['year'].min(),
                    max=df_episodes['year'].max(),
                    value=[df_episodes['year'].min(), df_episodes['year'].max()],
                    marks={str(year): str(year) for year in df_episodes['year'].unique()},
                    step=None
                )
                ]),

        html.Div(
            style={'textAlign': 'center',
                   'color': colors['text'],
                   'backgroundColor': colors['background'],
                   'margin-top': 100,
                   'margin-bottom': 50,
                   },
            children=[
                dcc.Graph(
                    id='seasons',
                    figure=fig3
                )
                ]),

        html.Div(
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'backgroundColor': colors['background'],
                'padding-top': 50,
                'padding-bottom': 50,
                'margin-left': 'auto',
                'margin-right': 'auto'
                },
            children=[
                dcc.Markdown('''
                    ### Data Sources
                    '''),
                generate_table(df_shows_info)
                     ]),
        html.Div(
            style={
                'textAlign': 'center',
                'padding-top': 50,
                'padding-bottom': 50
                },
            children=[
                 dcc.Markdown('''
                     All rights reserved by Snaylix
                     ''')
                     ])
            ])


@app.callback(
    Output('episodes', 'figure'),
    [Input('episodes_range-slider', 'value')])
def update_figure(year_range):
    date_start = str(year_range[0])
    date_end = str(year_range[1])
    df_episodes_transformed = df_episodes_dti[date_start: date_end]

    fig = px.scatter(df_episodes_transformed,
                     x='airdate',
                     y='imdb_rating',
                     color='show_title',
                     hover_name='title',
                     size='viewers',
                     size_max=60,
                     title="U.S. Viewers (in millions) / Rating per Episode",
                     labels=labels,
                     color_discrete_sequence=px.colors.qualitative.Plotly,
                     template="none"
                     )

    fig.update_layout(transition_duration=500)
    fig.update_xaxes(range=[date_start, date_end])
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        height=800,
        )
    fig.add_annotation( # add a text callout with arrow
        text="Dexter Series Finale", x="2013-09-22", y=4.8, arrowhead=1, showarrow=True
        )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
