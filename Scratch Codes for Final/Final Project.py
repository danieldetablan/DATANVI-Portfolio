# Import required libraries
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import ctx
import pandas as pd
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import json
from urllib.request import urlopen
with urlopen("https://raw.githubusercontent.com/macoymejia/geojsonph/refs/heads/master/Regions/Regions.50m.json") as request:
    regions = json.load(request)

df = pd.read_csv(
    "C:/Users/Daniel Detablan/Desktop/Notes/Term 24-25-1/DATAINVI/Final Project/assets/ph_dengue_cases2016-2020.csv")
df["Year"] = pd.to_datetime(df["Year"], format="%Y")

unique_region = df["Region"].unique()
unique_region_options = [
    {"label": region, "value": region}
    for region in unique_region
]

# All Philippine Regions
philippine_regions = [
    # Luzon
    "Ilocos Region (Region I)",
    "Cagayan Valley (Region II)",
    "Central Luzon (Region III)",
    "CALABARZON (Region IV-A)",
    "MIMAROPA (Region IV-B)",
    "Bicol Region (Region V)",
    "Cordillera Administrative Region (CAR)",
    "Metropolitan Manila",
    # Visayas
    "Western Visayas (Region VI)",
    "Central Visayas (Region VII)",
    "Eastern Visayas (Region VIII)",
    # Mindanao
    "Zamboanga Peninsula (Region IX)",
    "Northern Mindanao (Region X)",
    "Davao Region (Region XI)",
    "SOCCSKSARGEN (Region XII)",
    "Caraga (Region XIII)",
    "Autonomous Region of Muslim Mindanao (ARMM)"
]

Luzon = [
    "Region I",  # Ilocos Region
    "CAR",  # Cordillera Administrative Region
    "NCR",  # National Capital Region
    "Region II",  # Cagayan Valley
    "Region III",  # Central Luzon
    "Region IV-A",  # CALABARZON
    "Region IV-B",  # MIMAROPA
    "Region V"  # Bicol Region
]
Visayas = [
    "Region VI",  # Western Visayas
    "Region VII",  # Central Visayas
    "Region VIII"  # Eastern Visayas
]
Mindanao = [
    "Region IX",  # Zamboanga Peninsula
    "Region X",  # Northern Mindanao
    "Region XI",  # Davao Region
    "Region XII",  # SOCCSKSARGEN
    "Region XIII",  # Caraga
    "BARMM"  # Bangsamoro Autonomous Region in Muslim Mindanao
]


def get_island(region):
    if region in Luzon:
        return "Luzon"
    elif region in Visayas:
        return "Visayas"
    elif region in Mindanao:
        return "Mindanao"


def region_mapdata(region):
    for map_regions in philippine_regions:
        if region in map_regions:
            return map_regions
        elif region == "NCR":
            return "Metropolitan Manila"
        elif region == "BARMM":
            return "Autonomous Region of Muslim Mindanao (ARMM)"


df['Island'] = df['Region'].apply(get_island)

# Column REGION serves as an ID for the geojson map data and the dataframe df
df['REGION'] = df['Region'].apply(region_mapdata)

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)


# average cases per year
def get_avg_cases():
    annual_cases = df.groupby("Year")["Dengue_Cases"].mean()
    average = int(annual_cases.mean())
    return average


# average deaths per year
def get_avg_deaths():
    annual_deaths = df.groupby("Year")["Dengue_Deaths"].mean()
    average = int(annual_deaths.mean())
    return average


def main_graph():
    annual_total_df = df.groupby("Year")[["Dengue_Deaths", "Dengue_Cases"]].sum().reset_index()
    fig = px.line(annual_total_df, x="Year", y=["Dengue_Deaths", "Dengue_Cases"])
    return fig


app.layout = html.Div(
    [
        html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Philippines Dengue Cases 2016-2020",
                                style={"margin-bottom": "0px"},
                            ),
                        ]
                    )
                ],
                className="one-half column",
                id="title",
            ),
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Total Cases", className="card-title"),
                        html.P(df["Dengue_Cases"].sum(), className="card-text")
                    ]
                ),
                html.Div(
                    [
                        html.H4("Total Deaths", className="card-title"),
                        html.P(df["Dengue_Deaths"].sum(), className="card-text")
                    ]
                ),
                html.Div(
                    [
                        html.H4("Average Cases by Year", className="card-title"),
                        html.P(get_avg_cases(), className="card-text")  # highest 2166
                    ]
                ),
                html.Div(
                    [
                        html.H4("Average Deaths by Year", className="card-title"),
                        html.P(get_avg_deaths(), className="card-text")
                        # highest is 39. should we get the highest instead?
                    ]
                )
            ]
        ),

        dcc.Graph(id="main_chart", figure=main_graph()),

        html.Div(
            [
                html.Button("Total Cases", id="button_cases", n_clicks=0),
                html.Button("Total Deaths", id="button_deaths", n_clicks=0)
            ]
        ),

        dcc.Graph(id="donut_chart"),

        dcc.Graph(id="map_graph"),

        html.Div(
            [
                html.P(
                    "Filter by Year:",
                    className="year_filter",
                ),
                dcc.RangeSlider(
                    id="year_slider",
                    min=2016,
                    max=2020,
                    marks={i: '{}'.format(i) for i in range(2016, 2021)},
                    value=[2016, 2020],
                    className="year_slider",
                    step=1
                )
            ]
        ),
        html.Div(
            [
                html.P(
                    "Filter by Region:",
                    className="region_filter",
                ),
                dcc.Dropdown(
                    id="region_options",
                    options=unique_region_options,
                    multi=True,
                    value="Region I",
                    className="dd_region",
                )
            ]
        ),

        dcc.Graph(id="stacked_bar_chart")

    ]
)

@app.callback(
    Output("donut_chart", "figure"),
    [Input("button_cases", "n_clicks"),
     Input("button_deaths", "n_clicks")]
)
def make_donut_chart(btn1, btn2):
    # default donut chart (total cases per island)
    annual_cases = df.groupby("Island")["Dengue_Cases"].sum().reset_index()
    order_list = ["Luzon", "Visayas", "Mindanao"]
    annual_cases["Island"] = pd.Categorical(annual_cases["Island"], categories=order_list)
    annual_cases.sort_values(by="Island", inplace=True)

    fig = go.Figure(data=[go.Pie(labels=annual_cases["Island"], values=annual_cases["Dengue_Cases"], hole=0.3)])
    if "button_cases" == ctx.triggered_id:
        annual_cases = df.groupby("Island")["Dengue_Cases"].sum().reset_index()
        order_list = ["Luzon", "Visayas", "Mindanao"]
        annual_cases["Island"] = pd.Categorical(annual_cases["Island"], categories=order_list)
        annual_cases.sort_values(by="Island", inplace=True)
        fig = go.Figure(data=[go.Pie(labels=annual_cases.Island, values=annual_cases["Dengue_Cases"], hole=0.3)])
    elif "button_deaths" == ctx.triggered_id:
        annual_deaths = df.groupby("Island")["Dengue_Deaths"].sum().reset_index()
        order_list = ["Luzon", "Visayas", "Mindanao"]
        annual_deaths["Island"] = pd.Categorical(annual_deaths["Island"], categories=order_list)
        annual_deaths.sort_values(by="Island", inplace=True)
        fig = go.Figure(data=[go.Pie(labels=annual_deaths["Island"], values=annual_deaths["Dengue_Deaths"], hole=0.3)])

    fig.update_traces(sort=False)
    return fig


@app.callback(
    Output("map_graph", "figure"),
    [Input("year_slider", "value"),
     Input("region_options", "value")]
)
def make_map(year_slider, region_options):
    new_df = df[(df["Year"].dt.year >= year_slider[0]) & (df["Year"].dt.year <= year_slider[1])]
    new_df = new_df[new_df["Region"] == region_options]

    map_fig = px.choropleth_map(df, geojson=regions, color="winner",
                            locations="district", featureidkey="properties.district",
                            center={"lat": 45.5517, "lon": -73.7073},
                            map_style="carto-positron", zoom=9)
    map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return map_fig


@app.callback(
    Output("stacked_bar_chart", "figure"),
    [Input("year_slider", "value"),
     Input("region_options", "value")]
)
def make_stacked_bar(year_slider, region_options):
    new_df = df[(df["Year"].dt.year >= year_slider[0]) & (df["Year"].dt.year <= year_slider[1])]
    new_df = new_df[new_df["Region"] == region_options]

    fig = px.bar(new_df, x="Region", y=["Dengue_Cases", "Dengue_Deaths"],
                 title="Dengue Cases and Deaths by Region")

    return fig


# Main
if __name__ == "__main__":
    app.run_server(debug=True)