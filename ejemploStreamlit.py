import pickle
from pathlib import Path
import numpy as np

import pandas as pd  
import plotly.express as px 
import streamlit as st 

import streamlit_authenticator as stauth
import dataBaseData as db


st.set_page_config(page_title="SuperMarket Sales Dashboard", page_icon=":bar_chart:", layout="wide")



# --- USER AUTHENTICATION ---
users = db.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]


authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "sales_dashboard", "abcdef", cookie_expiry_days=1)


name, authentication_status, username = authenticator.login("Iniciar Sesión", "main")    #login form from module login. main/sidebar


if authentication_status == False:
    st.error("Usuario/Password incorrecto")

if authentication_status == None:
    st.warning("Por favor ingresar usuario y password")

if authentication_status:
    # ---- READ EXCEL ----
    @st.cache_data
    def get_data_from_excel():
        df = pd.read_excel(
            io="supermarkt_sales.xlsx",
            engine="openpyxl",
            sheet_name="Sales",
            skiprows=3,
            usecols="B:R",
            nrows=1000,
        )
        # Add 'hour' column to dataframe
        df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
        return df

    df = get_data_from_excel()


    authenticator.logout("Cerrar Sesión", "sidebar")
    # ---- SIDEBAR ----
    st.sidebar.title = (f" Bienvenido {name}")
    st.sidebar.header("Filtrar campos:")
    city = st.sidebar.multiselect(
        "Seleccionar la Ciudad:",
        options=df["City"].unique(),
        default=df["City"].unique()
    )

    customer_type = st.sidebar.multiselect(
        "Seleccionar tipo de Cliente:",
        options=df["Customer_type"].unique(),
        default=df["Customer_type"].unique(),
    )

    gender = st.sidebar.multiselect(
        "Seleccionar el Genero:",
        options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )

    payment = st.sidebar.multiselect(
        "Seleccionar el tipo de Pago",
        options=df["Payment"].unique(),
        default=df["Payment"].unique()
    )
    
    selected_month = st.sidebar.multiselect(
    'Seleccionar un mes', 
    options=df['Date'].dt.month.unique(),
    default=df["Date"].dt.month.unique()
    )
   
    df_selection = df.query(
        "City == @city & Customer_type ==@customer_type & Gender == @gender & Payment == @payment & Date.dt.month== @selected_month"
    )

    # ---- MAINPAGE ----
    st.title(":bar_chart: SuperMarket Sales Dashboard")
    st.markdown("##")

    # TOP KPI's
    total_sales = int(df_selection["Total"].sum())
    average_rating = round(df_selection["Rating"].mean(), 1)
    if np.isnan(average_rating):
        average_rating =0

        star_rating = ":star:" * int(round(average_rating, 0))
    star_rating = ":star:" * int(round(average_rating, 0))    
    average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Total Sales:")
        st.subheader(f"US $ {total_sales:,}")
    with middle_column:
        st.subheader("Average Rating:")
        st.subheader(f"{average_rating} {star_rating}")
    with right_column:
        st.subheader("Average Sales Per Transaction:")
        st.subheader(f"US $ {average_sale_by_transaction}")

    st.markdown("""---""")

    # SALES BY PRODUCT LINE [BAR CHART]
    sales_by_product_line = (
        df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
    )
    fig_product_sales = px.bar(
        sales_by_product_line,
        x="Total",
        y=sales_by_product_line.index,  ###########print(sales_by_product_line["Product line"])  len(sales_by_product_line) df.info()
        orientation="h",
        title="<b>Sales by Product</b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white",
    )
    fig_product_sales.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    # SALES BY GENDER
    sales_by_gender = (
        df_selection.groupby(by=["Gender"]).sum()[["Total"]].sort_values(by="Total")
    )
    fig_gender_sales = px.bar(
        sales_by_gender,
        x="Total",
        y=sales_by_gender.index,  ###########print(sales_by_product_line["Product line"])  len(sales_by_product_line) df.info()
        orientation="h",
        title="<b>Sales by Gender</b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white",
    )
    fig_gender_sales.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    # SALES BY DATE
    sales_by_month = (
        df_selection.groupby(by=["Date"]).sum()[["Total"]].sort_values(by="Total")
    )
    fig_by_month = px.bar(
        sales_by_month,
        x="Total",
        y=sales_by_month.index,  ###########print(sales_by_product_line["Product line"])  len(sales_by_product_line) df.info()
        orientation="h",
        title="<b>Sales by Date</b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white",
    )
    fig_by_month.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )




    #Box Plot
    fig_city_Total = px.box(df,x="City",y="Total", title="<b>Box Plot City</b>", color_discrete_sequence=["#C62268"])
    fig_city_Total.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),)
    
    

    
  


    # SALES BY HOUR [BAR CHART]
    sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
    fig_hourly_sales = px.bar(
        sales_by_hour,
        x=sales_by_hour.index,
        y="Total",
        title="<b>Sales by hour</b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white",
    )
    fig_hourly_sales.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )


    left_column, middle_column, right_column = st.columns(3)
    with st.container():
        left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
        middle_column.plotly_chart(fig_city_Total, use_container_width=True)
        right_column.plotly_chart(fig_product_sales, use_container_width=True)

    far_right_Column,far_farright_Column = st.columns(2)
    with st.container():    
        far_right_Column.plotly_chart(fig_gender_sales, use_container_width=True)
        far_farright_Column.plotly_chart(fig_by_month, use_container_width=True)

    



    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)