import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os
import mysql.connector

from numpy import random
from datetime import datetime


def get_connection():
    return mysql.connector.connect(**st.secrets["mysql"])


@st.cache_data(ttl=600)
def run_query(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()


def selecteer_product():
    qry1_select_product = "SELECT Product_ID, Product_Naam FROM Product"
    results_prod = []
    try:
        results1 = run_query(qry1_select_product)
        for i in results1:
            results_prod.append(i[1])
    except Exception as e:
        st.write(e)

    with st.form(key="Selecteer product", clear_on_submit=True):
        select_product = st.selectbox(
            "Welk product?",
            results_prod,
            label_visibility='visible',
        )
        submitted = st.form_submit_button("Submit")

    if submitted:
        try:
            qry2_select_product_id = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
            results2 = run_query(qry2_select_product_id, (select_product,))
            product_id = results2[0][0]
            qry3_select_prijzen = "SELECT Prijs, Winkel, Datum FROM Product_Prijs_Winkel WHERE Product_ID = %s"
            results3 = run_query(qry3_select_prijzen, (product_id,))
            
            winkels = set(w[1] for w in results3)
            df = pd.DataFrame(results3, columns=["Prijs", "Winkel", "Datum"])
            df['Datum'] = pd.to_datetime(df['Datum'], errors='ignore').dt.normalize()
            df.set_index('Datum').sort_index(ascending=True, inplace=True)
            df['Prijs'] = df['Prijs'].astype(float)
            df_last = df.groupby(['Winkel', 'Prijs']).Datum.max()
            st.write(df_last)
            
            fig, ax = plt.subplots()
            colors = "bgrcmyk"
            for winkel in winkels:
                i = random.randint(len(colors))
                ax.plot(df.loc[df["Winkel"] == winkel, "Prijs"], c=colors[i], label=winkel)
            ax.set_xticks(df["Datum"])
            ax.set_xticklabels(df["Datum"], rotation=45)
            ax.set_xlim(df["Datum"].min(), df["Datum"].max())
            ax.set_xlabel("Datum")
            ax.set_ylabel("Prijs")
            ax.set_ylim(0, df["Prijs"].max())
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.write(e)


def voegtoe_prijs_winkel():
    qry_select_ingredient = "SELECT Product_Naam FROM Product"
    qry_select_winkel = "SELECT DISTINCT Winkel FROM Product_Prijs_Winkel"
    results_prod = []
    results_winkel = []
    winkel_andere = "Andere winkel..."

    try:
        results1 = run_query(qry_select_ingredient)
        for i in results1:
            for j in i:
                results_prod.append(j)
        qry_select2 = run_query(qry_select_winkel)
        for i in results2:
            for j in i:
                results_winkel.append(j)
        results_winkel.append(winkel_andere)
    
    except Exception as e:
        st.write(e)

    with st.form(key="Prijs en winkel product", clear_on_submit=True):
        select_product = st.selectbox(
            "Welk product?",
            results_prod,
            label_visibility='visible',
        )
        # These exist within the form but won't wait for the submit button
        placeholder_for_select_winkel = st.empty()
        placeholder_for_text_andere_winkel = st.empty()

        prijs = st.number_input("Prijs (€)")
        datum_prijs = st.date_input("Datum van prijs: ")
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
            qry_insert_winkel_prijs = "INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES (%s, %s, %s, %s)"
            query_insert = run_query(qry_insert_winkel_prijs, (product_id, prijs, winkel_insert, datum_prijs))
        except Exception as e:
            st.write(e)


def voegtoe_product():
    with st.form("Voeg product toe"):
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


def voegtoe_prijswinkel(product):
    with st.form("Voeg winkel-prijs-datum toe:"):
        winkel = st.text_input('Winkel', '')
        prijs = st.number_input('Prijs in €')
        datum = st.date_input('Datum')
        submitted = st.form_submit_button("Submit")
        if submitted:
            qry_selecteer_product = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
            try:
                product_id = run_query(qry_selecteer_product, (product,))
                qry_insert_prijswinkel = "INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES(%s, %s, %s, %s)"
                try:
                    query = run_query(qry_insert_prijswinkel, (product_id, prijs, winkel, datum))
                    st.write(winkel, ' ', prijs, '€ ', datum, 'toegevoegd')
                except Exception as e:
                    st.write('Probleem bij het invoegen van prijs en winkel bij product: ', e)
            except Exception as e:
                st.write('Probleem bij het selecteren van het product: ', e)


page_names_to_funcs = {
    "Selecteer Product": selecteer_product,
    "Voeg Product toe": voegtoe_product,
    "Voeg Prijs en winkel toe aan een product": voegtoe_prijs_winkel,
    "Verwijder Product": verwijder_product,
}

selected_page = st.sidebar.selectbox("Kies een optie", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
