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
        conn.close()

    except Exception as e:
        st.write(e)

    option = st.selectbox(
        'Welk ingredient?',
        results_prod)

    st.write('Ingredient:', option)

    st.write(results_prod)

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

page_names_to_funcs = {
    "Selecteer Product": selecteer_product,
    "Voeg Product toe": voegtoe_product,
    "Verwijder Product": verwijder_product,
}

selected_page = st.sidebar.selectbox("Kies een optie", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

