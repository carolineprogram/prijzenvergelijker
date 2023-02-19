import sqlite3
import streamlit as st
import pandas as pd
import os
import db_functies as dbf

conn = dbf.create_connection('prijzenvergelijker.db')
st.write(conn)

def selecteer_product():

    qry_select_ingredient = "SELECT Product_Naam FROM Product"
    results_prod = []

    try:
        query = conn.execute(qry_select_ingredient)
        results= query.fetchall()
        for i in results:
            for j in i:
                results_prod.append(j)
        conn.commit()

    except Exception as e:
        st.write(e)
        conn.close()

    option = st.selectbox(
        'Welk ingredient?',
        results_prod)

    voegtoe_prijswinkel(option)

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

page_names_to_funcs = {
    "Selecteer Product": selecteer_product,
    "Voeg Product toe": voegtoe_product,
    "Verwijder Product": verwijder_product,
}

selected_page = st.sidebar.selectbox("Kies een optie", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

