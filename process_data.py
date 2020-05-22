#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import plotly.graph_objects as go

mapbox_access_token = "pk.eyJ1IjoiY2hsdWR3aWciLCJhIjoiY2pxM3p6cHp4MWpvaTN4cHBhOTA1aWZ4diJ9.FS-wzKCyyUVqHIADwgTkEw"


def make_plot(criteria, sub_criteria, data, outfile, show=False):
    """
    Creates a map for the specified criteria

    :param criteria:
    :param sub_criteria:
    :param data:
    :param outfile:
    :param show:
    :return:
    """
    color_dict = {"sehr gut": 'rgb(0,104,55)', "gut": 'rgb(102,189,99)', "tendenziell eher gut": 'rgb(217,239,139)',
                  "tendenziell eher schlecht": 'rgb(254,224,139)', "schlecht": 'rgb(244,109,67)',
                  "sehr schlecht": 'rgb(165,0,38)', "-": 'rgb(169,169,169)'}

    sub_data = data.loc[:, sub_criteria]
    sub_data["desc"] = sub_data.apply(lambda row: "<br>".join(["<b>{}</b>: <i>{}</i>".format(k, v)
                                                               for k, v in zip(row.index, row)
                                                               if k not in ["lat", "lon", criteria]]), axis=1)
    fig = go.Figure()
    count = 0
    for key, col in color_dict.items():
        key_data = sub_data.loc[sub_data[criteria] == key]
        count += len(key_data)
        fig.add_trace(go.Scattermapbox(
            lat=key_data["lat"],
            lon=key_data["lon"],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=9,
                color=col,
            ),
            text=key_data["desc"],
            hoverinfo="text",
            name=key))

    fig.update_layout(
        hovermode='closest',
        height=900,
        title=criteria,
        showlegend=True,
        legend_title_text='Bewertung',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=49.408404,
                lon=8.692645
            ),
            zoom=12
        )
    )
    if show:
        fig.show()
    fig.write_html(outfile)

def clean_data(data):
    """
    Clean data from Kobo
    :param data: Pandas DataFrame containing data from Kobo
    :return: Pandas DataFrame
    """

    # Remove unnecessary columns
    drop_cols = ['subscriberid', 'deviceid', '_uuid', '_submission_time', '_validation_status', '_id', 'start', 'end',
                 '_Nehme deinen Standort auf_altitude', '_Nehme deinen Standort auf_precision',
                 'Nehme deinen Standort auf']
    data.drop(drop_cols, axis=1, inplace=True)

    # Convert lat lon to float
    data = data.rename(columns={"_Nehme deinen Standort auf_longitude": "lon",
                                "_Nehme deinen Standort auf_latitude": "lat",
                                'Radwegbreite ': 'Radwegbreite',
                                'Ausstattung ': 'Ausstattung'})
    data["lat"] = data["lat"].astype("float")
    data["lon"] = data["lon"].astype("float")

    # Remove rows without lat, lon and Wie gut findest du den Radweg
    data = data.loc[pd.notnull(data["lat"]) & pd.notnull(data["lon"]) & pd.notnull(data["Wie gut findest du den Radweg?"])]

    # remove trailing spaces
    data = data.applymap(lambda x: x.rstrip() if isinstance(x, str) else x)
    # Replace Nan
    data = data.fillna("-")

    return data


def main():

    filepath = "./data/Meinungsumfrage zu Radwegen - latest version - labels - 2020-05-22-17-50-20.csv"
    plot_dir = "./plots"
    data_dir = "./data"

    #### Read data and reformat
    data = pd.read_csv(filepath, sep=";").set_index("_index")

    # use only data starting on May 22nd
    data["start"] = pd.to_datetime(data["start"])
    data = data.loc[data["start"] >= "2020-05-22"]

    print("clean data ...")
    data = clean_data(data)

    # export to file
    data.to_csv(os.path.join(data_dir, "heidelberger_radwege_umfrage.csv"))

    # Create plots -------------------------------
    print("Create plots...")

    criteria = "Wie gut findest du den Radweg?"
    sub_criteria = [criteria, 'lat', 'lon', 'Wie gut findest du die technische Ausstattung der Radinfrastruktur?',
                   'Wie ist dein generelles Sicherheitsgefühl hier?', 'Wie ist dein generelles Fahrgefühl hier?']
    outfilename = os.path.join(plot_dir, "plot1.html")
    make_plot(criteria, sub_criteria, data, outfilename)

    criteria = "Wie gut findest du die technische Ausstattung der Radinfrastruktur?"
    sub_criteria= [criteria, 'lat', 'lon', 'Ausstattung', 'Bauliche oder markierte Trennung zu FußgängerInnen',
           'Bauliche oder markierte Trennung von Autos', 'Bordsteinabsenkungen',
           'Beleuchtung', 'Radwegbelag', 'Radwegmarkierung', 'Radwegbreite',
           'Rote Markierung an Kreuzungen', 'Gibt es eine zusätzliche technische Ausstattung?']

    outfilename = os.path.join(plot_dir, "plot2.html")
    make_plot(criteria, sub_criteria, data, outfilename)

    criteria = "Wie ist dein generelles Sicherheitsgefühl hier?"
    sub_criteria= [criteria, 'lat', 'lon', 'Gefahren:',
           'Sichtbarkeit für AutofahrerInnen', 'Abstand zu Autos',
           'Abstand zu FußgängerInnen', 'Angemessene Geschwindigkeit der Autos',
           'Gibt es eine zusätzliche Gefahrenquelle? ']
    outfilename = os.path.join(plot_dir, "plot3.html")
    make_plot(criteria, sub_criteria, data, outfilename)

    criteria = "Wie ist dein generelles Fahrgefühl hier?"
    sub_criteria = [criteria, 'lat', 'lon', 'Einflüsse:',
           'Fahrfluss (z.B. grüner Pfeil für Radfahrende, Fahrradampel, ...)',
           'Luftqualität', 'Lärmbelastung', 'Begrünung', 'Übersichtlichkeit',
           'Beschattung', 'Gibt es zusätzliche Einflussfaktoren auf das Fahrgefühl?']
    outfilename = os.path.join(plot_dir, "plot4.html")
    make_plot(criteria, sub_criteria, data, outfilename)

if __name__ == "__main__":
    main()
