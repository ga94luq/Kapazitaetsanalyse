from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
from datetime import datetime
import math
import plotly.graph_objects as go

chart_types = [
    {'label': 'Scatter Plot', 'value': 'scatter'},
    {'label': 'Bar Chart', 'value': 'bar'}
]

df = pd.read_csv('https://raw.githubusercontent.com/ga94luq/Kapazitaetsanalyse/main/Kapazitaet_struct.csv')

df['Bezeichnung'] = 'SOC:' + df['SOC'].astype(str) + '% SiO:' + df['SiO'].astype(str) + '% D:' + df['D'].astype(str)
df.loc[df['D'] == 1, 'Zyklen_Joined'] = df['Zyklen'] + 0
df.loc[df['D'] == 2, 'Zyklen_Joined'] = df['Zyklen'] + 3
df.loc[df['D'] == 3, 'Zyklen_Joined'] = df['Zyklen'] + 13
df.loc[df['D'] == 4, 'Zyklen_Joined'] = df['Zyklen'] + 23
df.loc[df['D'] == 5, 'Zyklen_Joined'] = df['Zyklen'] + 33
df.loc[df['D'] == 6, 'Zyklen_Joined'] = df['Zyklen'] + 43
Vektor = []
for i in df.index:
    try:
        date_string = df['AbsZeit'][i]
        date_time_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        Vektor.append(date_time_obj)
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        print("Ein Fehler ist aufgetreten:", e)
        print(error_type)
        print(error_message)
        print(df['AbsZeit'][i])

Vektor = [eintrag.strftime('%Y-%m-%d %H:%M:%S') for eintrag in Vektor]
df['Zeit'] = Vektor
startzeitpunkt = datetime.strptime(df['Zeit'].min(), '%Y-%m-%d %H:%M:%S')
df['Zeit'] = pd.to_datetime(df['Zeit'])
df['Stunden_seit_Beginn'] = (df['Zeit'] - startzeitpunkt).dt.total_seconds() / 3600
df['Tage_seit_Beginn'] = (df['Zeit'] - startzeitpunkt).dt.days
df['AbsZeit'] = pd.to_datetime(df['AbsZeit'])
neue_spaltennamen = {'Zyklen': 'Zyklen',
                     'Qm': 'Kapazität Relativ',
                     'Q_rel': 'Kapazität Relativ b. Durchlauf',
                     'AbsZeit': 'Absolute Zeitangabe',
                     'Zyklen_Joined': 'Zyklen gereiht',
                     'Stunden_seit_Beginn': 'Stunden [h]',
                     'Q': 'Kapazität',
                     'Q_Leakage': 'Q Leakage Voltage Hold',
                     'Q_Delta_Checkup':'Q Leakage Checkup'
                     }
df = df.rename(columns=neue_spaltennamen)
data = df

app = Dash(__name__)
server = app.server

dropdown_options = [{'label': col, 'value': col} for col in df.columns]

initial_min_y = df['Kapazität Relativ'].min()
LowerGrenze = math.ceil(initial_min_y / 10.0) * 10
initial_max_y = df['Kapazität Relativ'].max()
UpperGrenze = math.ceil(initial_max_y / 10) * 10

app.layout = html.Div(style={'backgroundColor': 'white'}, children=[
    html.H4('Auswertung Kapazität'),
    # Dropdown-Menü für Diagrammtyp
    dcc.Dropdown(
        id='chart-type-dropdown',
        options=[
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Line Plot', 'value': 'line'},
            {'label': 'Bar Chart', 'value': 'bar'}
        ],
        value='line',  # Standardwert: Scatter Plot
        clearable=False
    ),
    html.Div([
        html.H6("Achsenbeschriftung ändern"),
        dcc.Input(id="x-axis-title", type="text", placeholder="X-Achsenbeschriftung"),
        dcc.Input(id="y-axis-title", type="text", placeholder="Y-Achsenbeschriftung"),
        dcc.Input(id="title", type="text", placeholder="Titel des Plots"),
        html.Button(id="submit-title", n_clicks=0, children="Titel anwenden"),
    ]),
    # Graph-Element für das Diagramm
    dcc.Graph(id="chart-graph"),
    html.P("Auswahl der Durchläufe"),
    dcc.RangeSlider(
        id='range-slider-x',
        min=1, max=6, step=1,
        marks={i: str(i) for i in range(1, 7)},
        value=[1, 6],
        className='slider-x',
        tooltip={"placement": "bottom", "always_visible": False}
    ),
    html.Div([
        html.H6("Y-Achsenbereich"),
        dcc.RangeSlider(
            id='range-slider-y',
            min=initial_min_y,
            max=initial_max_y,
            step=0.05,
            marks={LowerGrenze: str(LowerGrenze), UpperGrenze: str(UpperGrenze)},
            value=[initial_min_y, initial_max_y],
            className='slider-y',
            tooltip={"placement": "bottom", "always_visible": True}
        ),
    ]),
    html.Div([
        html.H6("Spaltenauswahl"),
        dcc.Dropdown(
            id='x-axis-dropdown',
            options=dropdown_options,
            value='Zyklen gereiht',  # Standardwert für die x-Achse
            clearable=False
        ),
        dcc.Dropdown(
            id='Y_Achsen',
            options=dropdown_options,
            multi=True,  # Erlaubt die Auswahl mehrerer Optionen
            value=['Kapazität Relativ'],  # Standardwert für die y-Achse
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Farbauswahl"),
        dcc.Dropdown(
            id='color-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='SOC',  # Standardwert für die Farbauswahl
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Symbolauswahl"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value='SiO',  # Standardwert für die Symbolauswahl
            clearable=False
        ),
    ]),
    html.Div([
        html.H6("Werte für SOC auswählen"),
        dcc.Checklist(
            id='soc-checklist',
            options=[
                {'label': '10%', 'value': 10},
                {'label': '30%', 'value': 30},
                {'label': '50%', 'value': 50},
                {'label': '70%', 'value': 70},
                {'label': '90%', 'value': 90}
            ],
            value=[10, 30, 50, 70, 90],  # Standardmäßig alle Werte ausgewählt
            labelStyle={'display': 'block'}
        ),
    ]),
    html.Div([
        html.H6("Werte für SiO auswählen"),
        dcc.Checklist(
            id='sio-checklist',
            options=[
                {'label': '0%', 'value': 0},
                {'label': '10%', 'value': 10},
                {'label': '15%', 'value': 15}
            ],
            value=[0, 10, 15],  # Standardmäßig alle Werte ausgewählt
            labelStyle={'display': 'block'}
        ),
    ]),
    html.Div([
        html.H6("Werte für Bezeichnung auswählen"),
        dcc.Checklist(
            id='bezeichnung-checklist',
            options=[{'label': label, 'value': label} for label in df['Bezeichnung'].unique()],
            value=df['Bezeichnung'].unique(),  # Alle Einträge vorausgewählt
            labelStyle={'display': 'block'}
        ),
    ]),
])

@app.callback(
    [Output("chart-graph", "figure")],
    [Output("range-slider-y", "min"),
     Output("range-slider-y", "max"),
     Output("range-slider-y", "marks")],
    [Input("range-slider-x", "value"),
     Input("range-slider-y", "value"),
     Input('x-axis-dropdown', 'value'),
     Input('Y_Achsen', 'value'),
     Input('color-dropdown', 'value'),
     Input('symbol-dropdown', 'value'),
     Input('soc-checklist', 'value'),
     Input('sio-checklist', 'value'),
     Input('chart-type-dropdown', 'value'),
     Input('bezeichnung-checklist', 'value'),
     Input('x-axis-title', 'value'),
     Input('y-axis-title', 'value'),
     Input('title', 'value'),
     Input('submit-title', 'n_clicks')]
)
def update_bar_chart(x_range, y_range, x_column, y_columns, color_column, symbol_column, soc_values, sio_values,
                     chart_type, bezeichnung_values,  x_title, y_title, title, n_clicks):
    # DataFrame aktualisieren
    df = data
    Min = 0
    Max = 0
    Min_col = y_columns[0]
    Max_col = y_columns[0]

    for col in y_columns:
        if df[col].min()<Min:
            Min=df[col].min()
            Min_col = col
        if df[col].max()>Max:
            Max = df[col].max()
            Max_col = col

    min_y = df[y_columns].min().min()  # Minimum across all selected y-columns
    LowerGrenze = math.floor(min_y / 10.0) * 10
    max_y = df[y_columns].max().max()  # Maximum across all selected y-columns
    UpperGrenze = math.ceil(max_y / 10) * 10

    low_x, high_x = x_range
    low_y, high_y = y_range

    # Create a mask for x_column
    mask_x = (df['D'] >= low_x) & (df['D'] <= high_x)
    mask_y = (df[y_columns] >= low_y) & (df[y_columns] <= high_y)
    for col in y_columns:
        mask_y = (df[col] >= low_y) & (df[col] <= high_y)

    if 'dQ/dV' in y_columns:
        LowerGrenze = 0
        low_y = 0
        min_y = 0

    filtered_df = df[
        df['SOC'].isin(soc_values) & df['SiO'].isin(sio_values) & df['Bezeichnung'].isin(bezeichnung_values) & mask_y]
    df = filtered_df
    df[color_column] = df[color_column].astype(str)

    step_size = 10
    NumberofSteps = int((UpperGrenze - LowerGrenze) / step_size) + 1
    marks = {LowerGrenze + i * step_size: str(round(LowerGrenze + i * step_size, 2)) for i in range(NumberofSteps)}

    if len(y_columns) == 1:
        if chart_type == 'line':
            fig = px.line(
                df[mask_x & mask_y], x=x_column, y=y_columns[0],
                color=color_column, symbol=symbol_column,
                hover_data=['Bezeichnung'], width=2000, height=800, markers=True,
                # color_discrete_sequence=Farben
            )
        elif chart_type == 'bar':
            fig = px.bar(
                df[mask_x & mask_y],
                x=x_column,
                y=y_columns[0],
                color=color_column,
                # symbol=symbol_column,
                hover_data=['Bezeichnung'],
                width=2000,
                height=800,
                # color_discrete_sequence=Farben
            )
        elif chart_type == 'scatter':
            fig = px.scatter(
                df[mask_x & mask_y],
                x=x_column,
                y=y_columns[0],
                color=color_column,
                symbol=symbol_column,
                hover_data=['Bezeichnung'],
                width=2000,
                height=800,
                # color_discrete_sequence=Farben
            )
        fig.update_xaxes(rangeslider_visible=True)
    else:
        fig = go.Figure()
        if chart_type == 'line':
            for col in y_columns:
                fig.add_trace(go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    name=col,
                    mode='lines',
                ))

        elif chart_type == 'bar':
            for col in y_columns:
                fig.add_trace(go.Bar(
                    x=df[x_column],
                    y=df[col],
                    name=col,
                    #marker_color=df[color_column],  # Assign color based on column values
                ))

        elif chart_type == 'scatter':
            for col in y_columns:
                fig.add_trace(go.Scatter(
                    x=df[x_column],
                    y=df[col],
                    name=col,
                    mode='markers',
                    marker_symbol=df[symbol_column],  # Assign symbol based on column values
                    #marker_color=df[color_column],  # Assign color based on column values
                ))
        fig.update_xaxes(rangeslider_visible=True)

    large_rockwell_template = dict(
        layout=go.Layout(
            title_font=dict(family="Arial", size=24),
            xaxis=dict(showline=True, zeroline=False, linecolor='black', title=x_title),
            yaxis=dict(showline=True, zeroline=False, linecolor='black', title=y_title),
            plot_bgcolor='white',
        )
    )
    fig.update_layout(template=large_rockwell_template)
    fig.update_layout(title=f'{", ".join(y_columns)} - {x_column}')

    fig.update_xaxes(title=x_title,rangeslider_visible=True)
    fig.update_yaxes(title=y_title)
    if  title:
        fig.update_layout(title=title)


    return fig, LowerGrenze, UpperGrenze, marks


if __name__ == '__main__':
    app.run_server(debug=True)
