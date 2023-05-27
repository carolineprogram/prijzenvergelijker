# streamlit_app.py

import streamlit as st
import mysql.connector

### Initialize connection.
### Uses st.cache_resource to only run once.
##@st.cache_resource
##def init_connection():
##    return mysql.connector.connect(**st.secrets["mysql"])
##
##conn = init_connection()
##


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
        return cur.fetchall()

### Perform query.
### Uses st.cache_data to only rerun when the query changes or after 10 min.
##@st.cache_data(ttl=600)
##def run_query(query):
##    with conn.cursor() as cur:
##        cur.execute(query)
##        return cur.fetchall()

rows = run_query("SELECT * from mytable;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")
#conn.close()

st.write("Nu staat er toch iets")
    
