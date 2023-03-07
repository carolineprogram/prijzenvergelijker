import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os
import db_functies as dbf

<<<<<<< HEAD
=======
from numpy import random
from datetime import datetime

>>>>>>> temp-brahnc
conn = dbf.create_connection('../SQL/prijzenvergelijker.db')
st.write(conn)
fig, ax = plt.subplots()

def selecteer_product():
    qry1_select_product = "SELECT Product_ID, Product_Naam FROM Product"
    results_prod = []
    try:
<<<<<<< HEAD
        query = conn.execute(qry_select_ingredient)
        results= query.fetchall()
        for i in results:
            for j in i:
                results_prod.append(j)
        conn.commit()
<<<<<<< HEAD

    except Exception as e:
        st.write(e)
        conn.close()
=======
        conn.close()

=======
        qry1 = conn.execute(qry1_select_product)
        results1 = qry1.fetchall()
        for i in results1:
            results_prod.append(i[1])
>>>>>>> temp-brahnc
    except Exception as e:
        st.write(e)
>>>>>>> 01ef0789e3b742cd6fc0168d73bf184b549ac59c

    with st.form(key="Selecteer product", clear_on_submit=True):
        select_product = st.selectbox(
            "Welk product?",
            results_prod,
            label_visibility = 'visible',
            )
        submitted = st.form_submit_button("Submit")

<<<<<<< HEAD
<<<<<<< HEAD
    voegtoe_prijswinkel(option)
=======
    st.write('Ingredient:', option)

    st.write(results_prod)
>>>>>>> 01ef0789e3b742cd6fc0168d73bf184b549ac59c
=======
    if submitted:
        try:
            st.write("TODO: Hier komt grafiek met prijzen over de tijd en de huidige prijs in elke beschikbare winkel")
            qry2_select_product_id = f"SELECT Product_ID FROM Product WHERE Product_Naam = '{select_product}'"
            try:
                qry2 = conn.execute(qry2_select_product_id)
                results2 = qry2.fetchall()
                product_id = results2[0][0]
                qry3_select_prijzen = f"SELECT Prijs, Winkel, Datum FROM Product_Prijs_Winkel WHERE Product_ID = {product_id}"
                try:
                    qry3 = conn.execute(qry3_select_prijzen)
                    results3 = qry3.fetchall()
#                    results3_sorted = sorted(results3, key=lambda product: product[2], reverse=True)
                    winkels = set(w[1] for w in results3)
                    df = pd.DataFrame(results3, columns=["Prijs", "Winkel", "Datum"])
                    df['Datum'] = pd.to_datetime(df['Datum'], errors='ignore').dt.normalize()
                    df.set_index('Datum').sort_index(ascending=True, inplace=True)
                    df['Prijs'] = df['Prijs'].astype(float)
                    df_last = df.groupby(['Winkel', 'Prijs']).Datum.max()
                    st.write(df_last)
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
            except Exception as e:
                st.write(e)
        
        except Exception as e:
            st.write(e)

>>>>>>> temp-brahnc

def voegtoe_prijs_winkel():

    qry_select_ingredient = "SELECT Product_Naam FROM Product"
    qry_select_winkel = "SELECT DISTINCT Winkel FROM Product_Prijs_Winkel"
    results_prod = []
    results_winkel = []
    winkel_andere = "Andere winkel..."

    try:
        qry_select1 = conn.execute(qry_select_ingredient)
        results1= qry_select1.fetchall()
        for i in results1:
            for j in i:
                results_prod.append(j)
        qry_select2 = conn.execute(qry_select_winkel)
        results2= qry_select2.fetchall()
        for i in results2:
            for j in i:
                results_winkel.append(j)
        results_winkel.append(winkel_andere)
        conn.commit()
    
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
        submitted = st.form_submit_button("Submit")

    # Create selectbox
    with placeholder_for_select_winkel:
        winkel = st.selectbox("Winkel: ",
        options=results_winkel
                            )
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
            qry_select_product_id = f"SELECT Product_ID FROM Product WHERE Product_Naam = '{select_product}'"
            qry_select = conn.execute(qry_select_product_id)
            product_id_array = qry_select.fetchall()
            product_id = product_id_array[0][0]
            st.write(product_id)
            qry_insert_winkel_prijs = f"INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES ('{product_id}', '{prijs}', '{winkel_insert}', '{datum_prijs}')"
            query_insert = conn.execute(qry_insert_winkel_prijs)
            conn.commit()
            conn.close()
        except Exception as e:
            st.write(e)
 
def voegtoe_product():
    with st.form("Voeg product toe"):
        textbox = st.text_input('Product', '')
        submitted = st.form_submit_button("Submit")
        if submitted:
            qry_insert_ingredient = f"INSERT INTO Product (Product_Naam) VALUES ('{textbox}')"
            st.write(qry_insert_ingredient)
            try:
                query = conn.execute(qry_insert_ingredient)
                conn.commit()
                conn.close()
                st.write(textbox, 'toegvoegd')
            except Exception as e:
                st.write(e)

def verwijder_product():
    st.write('tbc')

<<<<<<< HEAD
def voegtoe_prijswinkel(product):
    with st.form("Voeg winkel-prijs-datum toe:"):
        winkel = st.text_input('Winkel', '')
        prijs  = st.number_input('Prijs in €')
        datum = st.date_input('Datum')
        submitted = st.form_submit_button("Submit")
        if submitted:
            qry_selecteer_product = f'SELECT Product_ID FROM Product WHERE Product_Naam = "{product}"'
            st.write(qry_selecteer_product)
            try:
                product_id = conn.execute(qry_selecteer_product)
                conn.commit()
                st.write(product_id)
                qry_insert_prijswinkel = f"INSERT INTO Product_Prijs_Winkel (Product_ID, Prijs, Winkel, Datum) VALUES('{product_id}', '{prijs}', '{winkel}', '{datum}')"
                st.write(qry_insert_prijswinkel)
                try:
                    query = conn.execute(qry_insert_prijswinkel)
                    conn.commit()
                    conn.close()
                    st.write(winkel, ' ',  prijs,  '€ ', datum 
        , 'toegevoegd')
                except Exception as e:
                    conn.close()
                    st.write('Probleem bij het invoegen van prijs en winkel bij product: ', e)
            except Exception as e:
                conn.close()
                st.write('Probleem bij het selecteren van het product: ', e)

=======
>>>>>>> 01ef0789e3b742cd6fc0168d73bf184b549ac59c
page_names_to_funcs = {
    "Selecteer Product": selecteer_product,
    "Voeg Product toe": voegtoe_product,
    "Voeg Prijs en winkel toe aan een product": voegtoe_prijs_winkel,
    "Verwijder Product": verwijder_product,
}

selected_page = st.sidebar.selectbox("Kies een optie", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

