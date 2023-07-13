from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly_express as px

from dash_bootstrap_components.themes import VAPOR
from dash_bootstrap_templates import load_figure_template
import pandas as pd

DATA_PATH= "wine_130_dashboard.csv"
data = pd.read_csv(DATA_PATH)
varietales = data['variety'].unique()

app = Dash(__name__, external_stylesheets=[VAPOR])
app.title = "Los varietales del mundo 🍷 "

app.layout = html.Div(
        className= "app-div",
        children = [
            html.H1(app.title),
            dcc.Markdown('''
                    A partir de un varietal, es posible ver su distribución en el mundo, 
                    y los puntajes otorgados por especialistas. Además, haciendo click sobre el país que quieras, podrás obtener más información'''),
            html.Hr(),
            html.Div(
                children=[
                    html.H6("Varietal"),
                    dcc.Dropdown(
                        id="VARIETALES_DROPDOWN",
                        options=[{"label": varietal, "value": varietal} for varietal in varietales],
                        value="Malbec",
                        multi=False,
                    ),
                ]
            ),
            html.Div([
                html.Div(id='output'),
                html.Button('Reset',id='reset_button', n_clicks=0),
                ],
                style={'marginTop':20, 'marginLeft':20}
            ),

            html.Div(style={'width': '60%', 'display': 'inline-block'},
                     className="choropleth-container",
                     children=dcc.Graph(id="CHOROPLETH")
            ),
            html.Div(
                style={'width': '40%', 'display': 'inline-block'},
                className="container",
                children=dcc.Graph(id="HISTOGRAM")
            ),
            dbc.Row([
                dbc.Col(html.Div(
                style={'width': '60%'},
                className="container",
                children=dcc.Graph(id="SUN")), align="start"),
                dbc.Col(dbc.Row(html.Div(
                            className="container",
                            style={'width': '40%'},
                            children=dcc.Markdown(id="VARIETY_TEXT")), align="end")
            )]),
            html.Div(className="container",
                     style={'width': '100%'},
                     children=dcc.Graph(id="SCATTER")),
            html.Div(className="container",
                    style={'width': '100%'},
                    children=dcc.Markdown('''Proyecto Final de la Especialización en Ciencias de Datos, Departamento de Ciencias e Ingeniería de la Computación. Universidad Nacional del Sur. Albertina Popp''')),
            html.Div([
                html.Div(id='output'),
                html.Button('Reset', id='reset_button', n_clicks=0),
                ],
                style={'marginTop': 20, 'marginLeft': 20}
            ),
        ])


@app.callback(Output('CHOROPLETH', 'clickData'),
              Output('SCATTER', 'clickData'),
             [Input('reset_button','n_clicks')])

def update(reset):
    clickData = None
    clickData2= None
    return clickData, clickData2

@app.callback(
    Output("CHOROPLETH", "figure"),
    Output('HISTOGRAM', "figure"),
    Output("SUN", "figure"),
    Output("VARIETY_TEXT", "children"),
    Output("SCATTER", "figure"),
    Input("VARIETALES_DROPDOWN", "value"),
    Input('CHOROPLETH', 'clickData'),
    Input('SUN', 'clickData')
    )

def update_charts(value, pais, pais_sun):
    filtered_data = data[data["variety"] == value]
    if filtered_data.shape[0] == 0:
        return html.Div("No se eligió ningún varietal")
    if pais is None:
        title_histogram = "Distribución de puntajes de {}".format(value)
        title_sun = "Distribución por países, provincias y bodegas"
        title_scatter = "Puntaje versus Precio"
    if pais is not None:
        pais_elegido = pais['points'][0].get('location')
        nombre_pais = pais['points'][0].get('hovertext')
        filtered_data = filtered_data[filtered_data['ISO3'] == pais_elegido]
        title_histogram = "Distribución de puntajes de {} en {}".format(value, nombre_pais)
        title_sun = "Distribución por provincia y bodega"
        title_scatter = "Puntaje versus Precio de {} en {}".format(value, nombre_pais)
    if pais_sun is not None:
        pais_elegido = pais_sun['points'][0].get('label')
        nombre_pais = pais_sun['points'][0].get('label')
        filtered_data = filtered_data[filtered_data['country'] == pais_elegido]
        title_histogram = "Distribución de puntajes de {} en {}".format(value, nombre_pais)
        title_sun = "Distribución por provincia y bodega"
        title_scatter = "Puntaje versus Precio de {} en {}".format(value, nombre_pais)
    # make a dict with counts
    count_dict = {d: (filtered_data['country'] == d).sum() for d in filtered_data.country.unique()}
    # assign that dict to a column
    filtered_data['count'] = [count_dict[d] for d in filtered_data.country]
    filtered_data['sun_count'] = 1

    fig_choropleth = px.choropleth(filtered_data, locations="ISO3",
                        hover_name="country",
                        color='count',
                        labels={'count': 'Cantidad de reseñas'},
                        title="El varietal en el mundo: {}".format(value),
                        color_continuous_scale='BuPu',
                        template=load_figure_template('vapor')
                        )
    fig_histogram = px.histogram(filtered_data,
                       x=filtered_data['points'],
                       title=title_histogram,
                       template=load_figure_template('vapor'),
                        labels={"points": "Puntaje", "count": "Cantidad de reseñas"},
                       )
    fig_sun = px.sunburst(data_frame=filtered_data,
                          path=['country', 'province', 'winery'],
                          values='sun_count',
                          color='country',
                          hover_data={'country':False,
                                    'province':False,
                                    'winery': False,
                                    'points':False,
                                    'sun_count':True},
                          title=title_sun,
                          width=700,
                          height=700,
                          template=load_figure_template('vapor'),
                          color_discrete_sequence=px.colors.sequential.BuPu_r
                          )
    fig_scatter = px.scatter(data_frame=filtered_data,
                             x=filtered_data['points'],
                             y=filtered_data['price'],
                             title=title_scatter,
                             labels={
                                 "points": "Puntaje",
                                 "price": "Precio (USD)"
                             },
                             )
    title = "Una descripción de un {}: ".format(value)
    text = filtered_data['description'].sample()

    return fig_choropleth, fig_histogram, fig_sun, title+text, fig_scatter

if __name__ == "__main__":
    app.run_server(debug=True)