import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px

import mysql.connector

from numpy import random
from datetime import datetime

# Handle date time conversions between pandas and matplotlib
#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()

# Initialize connection.
# Uses st.cache_resource to only run once.
#@st.cache_resource
def get_connection():
        return mysql.connector.connect(**st.secrets["mysql"])

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 s.
@st.cache_data(ttl=10)
def run_query(query, params=None):
    with get_connection() as conn:
        with conn.cursor(buffered=True) as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            if query.strip().lower().startswith('insert'):
                conn.commit()
        return cur


def selecteer_product():
    qry1_select_product = "SELECT Product_ID, Product_Naam FROM Product ORDER BY Product_Naam"
    results_prod = []
    try:
        results1 = run_query(qry1_select_product).fetchall()
        for i in results1:
            results_prod.append(i[1])
    except Exception as e:
        st.write(e)

    with st.form(key="Selecteer product", clear_on_submit=True):
        select_product = st.selectbox(
            "Welk product?",
            results_prod,
            label_visibility = 'visible',
            )
        submitted = st.form_submit_button("Submit")

    if submitted:
        try:
            qry2_select_product_id = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
            results2 = run_query(qry2_select_product_id, (select_product,)).fetchall()
            product_id = results2[0][0]
            qry3_select_prijzen = "SELECT Prijs, Prijs_eenheid, Bio, Voor_gewicht, Type, Winkel, Datum FROM Product_Prijs_Winkel WHERE Product_ID = %s"
            results3 = run_query(qry3_select_prijzen, (product_id,)).fetchall()
            #winkels = set(w[1] for w in results3)
            df = pd.DataFrame(results3, columns=["Prijs", "Eenheid", "Bio", "Voor_gewicht", "Type", "Winkel", "Datum"])
            df['Datum'] = pd.to_datetime(df['Datum'], errors='ignore')
            df = df.sort_values(by='Datum')
            df.set_index('Datum', inplace=True)
            df['Prijs'] = df['Prijs'].astype(float)
            df_simple = df.copy()
            if len(df_simple["Voor_gewicht"]) > 0:
                bio = ""
                if df_simple["Bio"].all():
                    bio = "bio"
                df_simple["Bio + Type + Gewicht"] = bio + df["Type"] + ' - ' + df["Voor_gewicht"] + ' g'
            else:
                df_simple["Bio + Type + Gewicht"] = bio + df["Type"] + ' - ' + df["Voor_gewicht"]
            #Zoek meest recente prijs per winkel
            df_laatste_prijs = df_simple.groupby(['Winkel', 'Eenheid', 'Bio + Type + Gewicht']).tail(1)
            st.write(df_laatste_prijs)

            #colors = "bgrcmyk"
            
            winkels_unique = df["Winkel"].unique()
            eenheid_unique = df["Eenheid"].unique()
            biotypegewicht_unique = df_simple["Bio + Type + Gewicht"]
            sns.set_style("darkgrid")

            #print titel
            st.title(select_product)

            # Divide the available space into multiple columns
            columns = st.columns(len(eenheid_unique))

            
            # Loop through the data subsets for each "Eenheid" value
            for i,x in enumerate(eenheid_unique):
                fig, ax  = plt.subplots()
                data_subset = df_simple[df_simple["Eenheid"] == x]

                # Create a dictionary to store unique colors and line styles for each "btg"
                btg_styles = {}

                for w in winkels_unique:
                    for btg in biotypegewicht_unique:
                        data_subsubset = data_subset[(data_subset['Winkel'] == w) & (data_subset['Bio + Type + Gewicht'] == btg)]
                      
                        # Get a unique color and line style for the current "btg"
                        if btg not in btg_styles:
                            btg_styles[btg] = {
                                'color': sns.color_palette("tab10")[len(btg_styles) % 10],
                                'linestyle': '-' if len(btg_styles) % 2 == 0 else '--'  # Alternate between solid and dashed lines
                            }

                        
                        if len(data_subsubset) > 0:
                            plot_function = sns.lineplot if len(data_subsubset) > 1 else sns.scatterplot
                            g = plot_function(
                                    data=data_subsubset,
                                    x=data_subsubset.index,
                                    y="Prijs",
                                    label = btg,
                                    color = btg_styles[btg]['color'],
                                    linestyle=btg_styles[btg]['linestyle'],
                                    marker = 'o',
                                    ax=ax                        
                            )
                            # Add values in the area of the graph for the latest items (highest index)
                            latest_data = data_subsubset.iloc[-1]
                            ax.annotate(f"{latest_data['Prijs']:.2f}", (latest_data.name, latest_data['Prijs']), textcoords="offset points", xytext=(0, 10), ha='center')
                                                        
                ax.set(ylim=0) 
                ax.set_xticklabels(ax.get_xticklabels(), rotation = 30)
                sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
                st.pyplot(fig)
            
        except Exception as e:
            st.write(e)
    
def voegtoe_prijs_winkel():
    qry_select_ingredient = "SELECT Product_Naam FROM Product ORDER BY Product_Naam"
    qry_select_winkel = "SELECT DISTINCT Winkel FROM Product_Prijs_Winkel ORDER BY Winkel"
    qry_select_prijseenheid = "SELECT DISTINCT Prijs_eenheid FROM Product_Prijs_Winkel ORDER BY Prijs_eenheid"
    results_prod = []
    results_winkel = []
    results_prijseenheid = []
    winkel_andere = "Andere winkel..."

    try:
        results1 = run_query(qry_select_ingredient).fetchall()
        for i in results1:
            results_prod.append(i[0])
        results2 = run_query(qry_select_winkel).fetchall()
        for j in results2:
            results_winkel.append(j[0])
        results_winkel.append(winkel_andere)
    
    except Exception as e:
        st.write(e)

    with st.form(key="Prijs en winkel product", clear_on_submit=True):
        select_product = st.selectbox(
            "Welk product?",
            results_prod,
            label_visibility = 'visible',
            )
        # These exist within the form but won't wait for the submit button
        placeholder_for_select_winkel = st.empty()
        placeholder_for_text_andere_winkel = st.empty()

        prijs = st.number_input("Prijs (€)")
        prijs_eenheid = st.text_input("Eenheid")
        bio = st.checkbox('BIO')
        voor_gewicht  =st.text_input('Specifiek voor volgend gewicht')
        product_type = st.text_input('nog iets specifiek? (eigenlijk vooral voor Pitpit, zoals bv Europese pompoenpitten vs niet-Europese')
        datum_prijs = st.date_input("Datum van prijs: ")
        datum_prijs = datum_prijs.strftime("%Y-%m-%d")
        submitted = st.form_submit_button("Submit")

    # Create selectbox
    with placeholder_for_select_winkel:
        winkel = st.selectbox("Winkel: ", options=results_winkel)
        
    # Create text input voor alternatieve winkel
    with placeholder_for_text_andere_winkel:
        if winkel == winkel_andere:
            winkel_andere_optie = st.text_input(winkel_andere)
       
    if submitted:
        try:
            if winkel == winkel_andere:
                    winkel_insert = winkel_andere_optie
            else:
                winkel_insert = winkel
            qry_select_product_id = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
            results_select = run_query(qry_select_product_id, (select_product,)).fetchone()
            product_id = results_select[0]
            
            try:
                qry_insert_winkel_prijs = "INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Prijs_eenheid, Bio, Voor_gewicht, Type, Winkel, Datum) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                run_query(qry_insert_winkel_prijs, (product_id, prijs, prijs_eenheid, bio, voor_gewicht, product_type, winkel_insert, datum_prijs))
                st.write(product_id, ' ', prijs, ' ', prijs_eenheid, 'toegevoegd')
            except Exception as e:
                st.write(e)
        except Exception as e:
            st.write(e)

def voegtoe_product():
    with st.form(key="Voeg product toe",  clear_on_submit=True):
        textbox = st.text_input('Product', '')
        bulkkorting_content = st.checkbox('Bulkkorting Content')
        pitpit_url = st.text_input('Url voor PitPit', '')
        delhaize_url = st.text_input('Url voor Delhaize', '')
        submitted = st.form_submit_button("Submit")
        if submitted:
            qry_insert_ingredient = "INSERT INTO Product (Product_Naam, Bulkkorting_content, Pitpit_url, Delhaize_url) VALUES (%s, %s, %s, %s)"
            try:
                query = run_query(qry_insert_ingredient, (textbox, bulkkorting_content, pitpit_url, delhaize_url))
                st.write(textbox, 'toegevoegd')
            except Exception as e:
                st.write(e)
        
def verwijder_product():
    st.write('tbc')

page_names_to_funcs = {
    "Selecteer Product": selecteer_product,
    "Voeg Product toe": voegtoe_product,
    "Voeg Prijs en winkel toe aan een product": voegtoe_prijs_winkel,
    "Verwijder Product": verwijder_product,
}

selected_page = st.sidebar.selectbox("Kies een optie", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
