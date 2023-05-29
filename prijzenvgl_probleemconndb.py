# streamlit_app.py

import streamlit as st
import mysql.connector
#import pandas as pd

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

qry1_select_product = "SELECT Product_ID, Product_Naam FROM Product ORDER BY Product_Naam"
results_prod = []
results1 = run_query(qry1_select_product)
for i in results1:
    #results_prod.append(i[1])
    st.write(i)

##with st.form(key="Selecteer product", clear_on_submit=True):
##    select_product = st.selectbox(
##        "Welk product?",
##        results_prod,
##        label_visibility = 'visible',
##        )
##    submitted = st.form_submit_button("Submit")
##
##if submitted:
##    try:
##        qry2_select_product_id = "SELECT Product_ID FROM Product WHERE Product_Naam = %s"
##        results2 = run_query(qry2_select_product_id, (select_product,))
##        st.write(results2)
##        product_id = results2[0][0]
##        qry3_select_prijzen = "SELECT Prijs, Winkel, Datum FROM Product_Prijs_Winkel WHERE Product_ID = %s"
##        results3 = run_query(qry3_select_prijzen, (product_id,))
##        st.write(results3)
##        winkels = set(w[1] for w in results3)
##        df = pd.DataFrame(results3, columns=["Prijs", "Winkel", "Datum"])
##        st.write(df)
##        df['Datum'] = pd.to_datetime(df['Datum'], errors='ignore').dt.date
##        df.set_index('Datum').sort_index(ascending=True, inplace=True)
##        df['Prijs'] = df['Prijs'].astype(float)
##
##        months = mdates.MonthLocator()  # every month
##        days = mdates.DayLocator()
##        years_fmt = mdates.DateFormatter('%m/%Y')
##
##        fig, ax = plt.subplots()
##        colors = "bgrcmyk"
##        for winkel in winkels:
##            i = random.randint(len(colors))
##            ax.plot(df.loc[df["Winkel"] == winkel, "Prijs"], 'ro', c=colors[i], label=winkel)
##
##        # format the ticks
##        ax.xaxis.set_major_locator(months)
##        ax.xaxis.set_major_formatter(years_fmt)
##        ax.xaxis.set_minor_locator(days)
##
##        # round to nearest years.
##        datemin = np.datetime64(df['Datum'].min())
##        datemax = np.datetime64(df['Datum'].max())
##        ax.set_xlim(datemin, datemax)
##
##        # format the coords message box
##        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
##        ax.format_ydata = lambda x: '$%1,2f' % x  # format the price.
##        ax.grid(False)
##
##        # rotates and right aligns the x labels, and moves the bottom of the
##        # axes up to make room for them
##        fig.autofmt_xdate()
##        ax.legend()
##        st.pyplot(fig)
##    except Exception as e:
##        st.write(e)
##
##st.write("Nu staat er toch iets")
    
