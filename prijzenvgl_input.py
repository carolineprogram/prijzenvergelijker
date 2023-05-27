import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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
        st.write(conn)
        with conn.cursor(buffered=True) as cur:
            st.write(cur)
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
        return cur.fetchall()


def selecteer_product():
    qry1_select_product = "SELECT Product_ID, Product_Naam FROM Product ORDER BY Product_Naam"
    results_prod = []
    try:
        results1 = run_query(qry1_select_product)
#        results1_set = results1.fetchall()
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
            results2 = run_query(qry2_select_product_id, (select_product,))
            st.write(results2)
            product_id = results2[0][0]
            qry3_select_prijzen = "SELECT Prijs, Winkel, Datum FROM Product_Prijs_Winkel WHERE Product_ID = %s"
            results3 = run_query(qry3_select_prijzen, (product_id,))
            st.write(results3)
            #results3_set = results3.fetchall()
            winkels = set(w[1] for w in results3)
            df = pd.DataFrame(results3, columns=["Prijs", "Winkel", "Datum"])
            st.write(df)
            df['Datum'] = pd.to_datetime(df['Datum'], errors='ignore').dt.date
            #df['Datum'] = df['Datum'].apply(mdates.date2num)
            #date_form = DateFormatter("%d-%m-%Y")
            df.set_index('Datum').sort_index(ascending=True, inplace=True)
            df['Prijs'] = df['Prijs'].astype(float)
            #df_last = df.groupby(['Winkel', 'Prijs']).Datum.max()
            #st.write(df_last)

##            years = mdates.YearLocator()   # every year
            months = mdates.MonthLocator()  # every month
            days = mdates.DayLocator()
            years_fmt = mdates.DateFormatter('%m/%Y')

            fig, ax = plt.subplots()
            colors = "bgrcmyk"
            for winkel in winkels:
                i = random.randint(len(colors))
                ax.plot(df.loc[df["Winkel"] == winkel, "Prijs"], 'ro', c=colors[i], label=winkel)

            # format the ticks
            ax.xaxis.set_major_locator(months)
            ax.xaxis.set_major_formatter(years_fmt)
            ax.xaxis.set_minor_locator(days)

            # round to nearest years.
            datemin = np.datetime64(df['Datum'].min())
            datemax = np.datetime64(df['Datum'].max())
            ax.set_xlim(datemin, datemax)

            # format the coords message box
            ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
            ax.format_ydata = lambda x: '$%1,2f' % x  # format the price.
            ax.grid(False)

            # rotates and right aligns the x labels, and moves the bottom of the
            # axes up to make room for them
            fig.autofmt_xdate()

            #ax.set_xticks(df["Datum"])
            #ax.set_xticklabels(df["Datum"], rotation=45)
            # Convert x-axis limits back to date format
##            xmin = df['Datum'].min()
##            xmax = df['Datum'].max()
##            ax.xaxis.set_major_formatter(date_form)
##            ax.xaxis.set_minor_formatter(date_form)
##            ax.set_xlim(xmin, xmax)
##            ax.xaxis.get_majorticklabels()
##            ax.set_xlabel("Datum")
##            ax.set_ylabel("Prijs")
##            ax.set_ylim(0, df["Prijs"].max())
##            ax.xaxis.set_minor_locator(mdates.WeekLocator())
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.write(e)
    
def voegtoe_prijs_winkel():
    qry_select_ingredient = "SELECT Product_Naam FROM Product ORDER BY Product_Naam"
    qry_select_winkel = "SELECT DISTINCT Winkel FROM Product_Prijs_Winkel ORDER BY Winkel"
    results_prod = []
    results_winkel = []
    winkel_andere = "Andere winkel..."

    try:
        results1 = run_query(qry_select_ingredient)
        for i in results1.fetchall():
            results_prod.append(i[0])
        results2 = run_query(qry_select_winkel)
        for j in results2.fetchall():
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
            results_select = run_query(qry_select_product_id, (select_product,))
            product_id = results_select.fetchone()[0]
            try:
                qry_insert_winkel_prijs = "INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES (%s, %s, %s, %s)"
                query_insert = run_query(qry_insert_winkel_prijs, (product_id, prijs, winkel_insert, datum_prijs))
            except Exception as e:
                st.write(e)
        except Exception as e:
            st.write(e)

##def voegtoe_prijswinkel(product):
##    with st.form("Voeg winkel-prijs-datum toe:"):
##        winkel = st.text_input('Winkel', '')
##        prijs  = st.number_input('Prijs in €')
##        datum = st.date_input('Datum')
##        submitted = st.form_submit_button("Submit")
##        if submitted:
##            qry_selecteer_product = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
##            try:
##                st.write('try 1')
##                product_id = run_query(qry_selecteer_product, (product,))
##                qry_insert_prijswinkel = "INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES(%s, %s, %s, %s)"
##                try:
##                    st.write('try 2')
##                    query = run_query(qry_insert_prijswinkel, (product_id, prijs, winkel, datum))
##                    st.write(winkel, ' ', prijs, '€ ', datum, 'toegevoegd')
##                except Exception as e:
##                    st.write('Probleem bij het invoegen van prijs en winkel bij product: ', e)
##            except Exception as e:
##                st.write('Probleem bij het selecteren van het product: ', e)


def voegtoe_product():
    with st.form(key="Voeg product toe",  clear_on_submit=True):
        textbox = st.text_input('Product', '')
        submitted = st.form_submit_button("Submit")
        if submitted:
            qry_insert_ingredient = "INSERT INTO Product (Product_Naam) VALUES (%s)"
            try:
                query = run_query(qry_insert_ingredient, (textbox,))
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

