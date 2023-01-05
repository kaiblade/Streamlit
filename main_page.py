import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
from requests import Session
import plotly.express as px
import altair as alt
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects,ReadTimeout
import json
import os
from millify import millify
from PIL import Image
from streamlit_server_state import server_state, server_state_lock



def luna_data(url, label, sql):
    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
    else:
        response = None

    df=pd.DataFrame.from_records(response_json)
    
    if "%" in label:
        st.metric(f"[{label}]({sql})", f"{millify(df.at[0,label], precision=2)}%")
    else:
        st.metric(f"[{label}]({sql})", millify(df.at[0,label], precision=2))


def image_fetch(image, caption,link):
    st.text("")
    st.markdown("---")
    st.text("")
    st.markdown(f'[{caption}]({link})')
    image = Image.open(image)

    st.image(image, caption=caption)
    
    
def luna_info():
    key=st.secrets['CMC_API_KEY']
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': key,
    }
    parameters = {
    'symbol':'LUNA'

    }

    session = Session()
    session.headers.update(headers)
    

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        cir_supply = data['data']['LUNA']['circulating_supply']
        tot_supply = data['data']['LUNA']['total_supply']
        price = data['data']['LUNA']['quote']['USD']['price']
        server_state.price=price

    except (ConnectionError, Timeout, TooManyRedirects,ReadTimeout) as e:             
        print(e)
        cir_supply=127475474.310907
        tot_supply=1004262701
        price =  server_state.price

    return cir_supply, tot_supply,price

def tables(url, x, y, title,sql):

    
    st.text("")
    st.markdown("---")
    st.text("")

    st.markdown(f'[{title}]({sql})')
    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
    else:
        response = None

    df=pd.DataFrame.from_records(response_json)  
    df.set_index('#', inplace=True, drop=True) 
    st.dataframe(df,use_container_width=True)

    
def bar_charts(url, x, y,title,sql,z=None):
    
    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
    else:
        response = None

    df=pd.DataFrame.from_records(response_json)
    

    if 'Rewards' in title:
        print(luna_info()[2])
        df[y] = df[y]*float(luna_info()[2])
        if 'Total' in title:
            return df[y].sum()
    
   
    st.markdown("---")
    st.text("")

    st.markdown(f'[{title}]({sql})')

    df[x] = pd.to_datetime(df[x])
   

    if not z:
        alt_chart = alt.Chart(df)\
        .mark_bar()\
        .encode(
        x=alt.X(x, type = "temporal", axis=alt.Axis(format="%b %d, %Y")),
        y=y
        ).properties(
        width='container',
        height=500,
        ).interactive()
    else:
        alt_chart = alt.Chart(df)\
        .mark_bar()\
        .encode(
        x=alt.X(x, type = "temporal", axis=alt.Axis(format="%b %d, %Y")),
        y=y,
        color=z,
        ).properties(
        width='container',
        height=500,
        ).interactive()

    st.altair_chart(alt_chart, theme = 'streamlit', use_container_width=True)
    

    
def line_charts(url, x, y, title,sql):
    
    st.text("")
    st.text("")
    
    st.markdown(f'[{title}]({sql})')

    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
    else:
        response = None

    df=pd.DataFrame.from_records(response_json)
    df[x] = pd.to_datetime(df[x])
    # url = 'https://app.flipsidecrypto.com/velocity/queries/f8cf2192-3efc-4584-b2c4-965937f721a6'
    alt_chart = alt.Chart(df)\
    .mark_line()\
    .encode(
    x=alt.X(x, type = "temporal", axis=alt.Axis(format="%b %d, %Y")),
    y=y

    ).properties(
    width='container',
    height=500,
    ).interactive()

    alt_chart.configure_bar(href='https://app.flipsidecrypto.com/velocity/queries/f8cf2192-3efc-4584-b2c4-965937f721a6')

    st.altair_chart(alt_chart, theme = 'streamlit', use_container_width=True)

    

def donuts(url,x,y,title,sql):


    st.markdown(f'[{title}]({sql})')

    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
    else:
        response = None

    df=pd.DataFrame.from_records(response_json)
    df[x]=df[x].apply(lambda col: f'{col[0:18]}...' if len(col) > 21 else col)

  
    fig = px.pie(df[x], values = df[y], hole = 0.55,
        names = df[x],
    )

    fig.update_layout(
        autosize=True,
        width=300,
        height=300,
        showlegend=True, margin={"l":0,"r":5,"t":0,"b":0}
    )

    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='percent', textfont_size=14)

    st.plotly_chart(fig, theme=None, use_container_width=True)

    # alt_chart=alt.Chart(df)\
    # .encode(
    # theta=alt.Theta(field=y,type="quantitative", stack= True),
    # color=alt.Color(field=x, type="nominal"))
    
    # pie = alt_chart.mark_arc(outerRadius=160, innerRadius=120)
    # alt_text = alt_chart.mark_text(radius=130, size=12).encode()
    

    # st.altair_chart(pie + alt_text, theme = 'streamlit', use_container_width=True)


st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.8,8,1.2])

with col2:
    st.title("Terradash, Part 4: Bringing It All Together")

st.text("")
st.markdown("- Dashboard Github link: https://github.com/kaiblade/Streamlit")
st.text("")
selected = option_menu(
        menu_title=None,  
        options=["Transactions", "Wallets", "Developments", "Supply"],  
        icons=["file-ruled", "wallet", "code", "file-plus"],  
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal",
    )

if selected == "Transactions":

    with open('transactions.md', 'r', encoding='utf-8-sig') as f:
        st.markdown(f.read())

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/e85d4272-3bfd-42ac-9b3b-2bec8f4c8467/data/latest",
    "Weeks","Average Transaction Fee in Luna","Average Transaction Fee per Transaction per Week", "https://app.flipsidecrypto.com/velocity/queries/e85d4272-3bfd-42ac-9b3b-2bec8f4c8467")

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/6e0599d5-77aa-4382-b717-99856ed5a4f4/data/latest",
    "Weeks","Total Transaction Fees in Luna","Total Transaction Fee per Week", "https://app.flipsidecrypto.com/velocity/queries/6e0599d5-77aa-4382-b717-99856ed5a4f4")

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/5beee8f9-8bb5-4ec3-82a0-391f384aaa60/data/latest",
    "Weeks","Total Number of Transactions","Total Number of Transactions per Week","https://app.flipsidecrypto.com/velocity/queries/5beee8f9-8bb5-4ec3-82a0-391f384aaa60")

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/85223683-0459-4273-a4bf-f2368971d4aa/data/latest",
    "Weeks","Average TPS","Average TPS per Week", "https://app.flipsidecrypto.com/velocity/queries/85223683-0459-4273-a4bf-f2368971d4aa")

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/c5389bb2-ba0f-4397-bdfd-e2fe35ab240e/data/latest",
    "Weeks","Average Block Time in seconds","Average Block Time per Week", "https://app.flipsidecrypto.com/velocity/queries/c5389bb2-ba0f-4397-bdfd-e2fe35ab240e")

    

if selected == "Wallets":

    with open('wallets.md', 'r', encoding='utf-8-sig') as f:
        st.markdown(f.read())

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/e1879001-a5c1-4276-9a07-742a8cc25b41/data/latest",
    "Weeks", "Total Number of New Wallets", "Total Number of New Wallets per Week", "https://app.flipsidecrypto.com/velocity/queries/e1879001-a5c1-4276-9a07-742a8cc25b41")
    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/7281402f-3fae-473d-af97-749f0f749e41/data/latest",
    "Weeks", "Total Number of Active Wallets", "Total Number of Active Wallets","https://app.flipsidecrypto.com/velocity/queries/7281402f-3fae-473d-af97-749f0f749e41")
    st.markdown("___")
    st.text("")
    st.text("")
    tab1, tab2 = st.tabs(["Cumulative Number of Active Wallets", "Cumulative Number of New Wallets"])
    
    with tab1:
        line_charts("https://node-api.flipsidecrypto.com/api/v2/queries/eed7aa5b-03b2-497e-b7bc-0cd35c4978c6/data/latest",
        "Weeks", "Cumulative Number of Active Wallets", "Cumulative Number of Active Wallets over Time", "https://app.flipsidecrypto.com/velocity/queries/eed7aa5b-03b2-497e-b7bc-0cd35c4978c6" )

    with tab2:    
        line_charts("https://node-api.flipsidecrypto.com/api/v2/queries/8a394356-836b-4be1-ad41-998942010002/data/latest",
        "Weeks", "Cumulative Number of New Wallets", "Cumulative Number of New Wallets over Time","https://app.flipsidecrypto.com/velocity/queries/8a394356-836b-4be1-ad41-998942010002")
    
if selected == "Developments":
    
    with open('developments.md', 'r', encoding='utf-8-sig') as f:
        st.markdown(f.read())

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/e7aa3c9c-20f1-4f80-b5a7-758c2c5d4cc2/data/latest",
    "Weeks", "Number of New Contracts Deployed", "New Contracts Deployed each Week","https://app.flipsidecrypto.com/velocity/queries/e7aa3c9c-20f1-4f80-b5a7-758c2c5d4cc2")
    
    st.markdown("___")
    st.text("")
    
    line_charts("https://node-api.flipsidecrypto.com/api/v2/queries/c505653e-3e3a-4c67-928f-df2ecc9b4397/data/latest",
    "Weeks", "Cumulative Contracts Deployed", "Total Contracts Deployed each Week", "https://app.flipsidecrypto.com/velocity/queries/c505653e-3e3a-4c67-928f-df2ecc9b4397")

    # st.markdown("___")
    # st.text("")

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/5b9a936a-f3c2-4dd9-96fa-08501ec326ed/data/latest",
    "Weeks","Number of Unique Contracts Used", "Number of Unique Contracts Used each Week", "https://app.flipsidecrypto.com/velocity/queries/5b9a936a-f3c2-4dd9-96fa-08501ec326ed")
    
    st.markdown("---")
    st.text("")
    don1, don2 = st.columns(2)
    with don1:
        donuts("https://node-api.flipsidecrypto.com/api/v2/queries/6c588eaf-eaf0-43a5-b483-ea1afb61b218/data/latest",
        "Contract Types", "Number of Contract Calls", "Contract Usage Distribution Grouped By Contract Types", "https://app.flipsidecrypto.com/velocity/queries/6c588eaf-eaf0-43a5-b483-ea1afb61b218")

    with don2:
        donuts("https://node-api.flipsidecrypto.com/api/v2/queries/a15e7804-4ed9-4a64-b67c-a18c6bf445fa/data/latest",
    "Project Names","Number of Contract Calls","Top 10 Most Popular Contracts", "https://app.flipsidecrypto.com/velocity/queries/a15e7804-4ed9-4a64-b67c-a18c6bf445fa")
    
if selected == "Supply":
    with open('supply.md', 'r', encoding='utf-8-sig') as f:
        st.markdown(f.read())
    
    
    st.markdown("---")

    st.write('')

    col1,col2,col3,col4=st.columns(4)
    circulating, total = luna_info()[0:2]
    print(total,circulating)
    with col1:
        st.metric("[Circulating Supply](https://coinmarketcap.com/currencies/terra-luna-v2/)", millify(circulating, precision=2))
        st.metric("[Total Supply](https://coinmarketcap.com/currencies/terra-luna-v2/)", millify(total, precision=3))
    with col2:
        luna_data("https://node-api.flipsidecrypto.com/api/v2/queries/488ea655-c10e-4d47-86ea-3d59b85de606/data/latest",
        "# LUNA IBC-ed out","https://app.flipsidecrypto.com/velocity/queries/488ea655-c10e-4d47-86ea-3d59b85de606")
        luna_data("https://node-api.flipsidecrypto.com/api/v2/queries/488ea655-c10e-4d47-86ea-3d59b85de606/data/latest",
        "Total Transferred LUNA","https://app.flipsidecrypto.com/velocity/queries/488ea655-c10e-4d47-86ea-3d59b85de606")
    with col3:
        luna_data("https://node-api.flipsidecrypto.com/api/v2/queries/488ea655-c10e-4d47-86ea-3d59b85de606/data/latest",
        "% LUNA IBC-ed out","https://app.flipsidecrypto.com/velocity/queries/488ea655-c10e-4d47-86ea-3d59b85de606")
        luna_data("https://node-api.flipsidecrypto.com/api/v2/queries/434cd3fe-0d92-4be5-b1f6-50b82de890f6/data/latest",
        "# of LUNA staked","https://app.flipsidecrypto.com/velocity/queries/434cd3fe-0d92-4be5-b1f6-50b82de890f6")

    with col4:
        luna_data("https://node-api.flipsidecrypto.com/api/v2/queries/434cd3fe-0d92-4be5-b1f6-50b82de890f6/data/latest",
        "% of LUNA staked","https://app.flipsidecrypto.com/velocity/queries/434cd3fe-0d92-4be5-b1f6-50b82de890f6")

        title= "Total Stake Rewards (USD)"
        sql= "https://app.flipsidecrypto.com/velocity/queries/4270ef09-b468-4bc1-a21e-814c2fab4802"
        total_rewards= bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/4270ef09-b468-4bc1-a21e-814c2fab4802/data/latest",
    "Weeks","Total Stake Rewards in USD",title, sql)
        st.metric(f"[{title}]({sql})", f'${millify(total_rewards, precision=2)}')


    # with col2:  
    tables("https://node-api.flipsidecrypto.com/api/v2/queries/f8cf2192-3efc-4584-b2c4-965937f721a6/data/latest", 
        "Wallets", "Total Balance in Luna", "Top 100 Richlist", "https://app.flipsidecrypto.com/velocity/queries/f8cf2192-3efc-4584-b2c4-965937f721a6") 

    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/4270ef09-b468-4bc1-a21e-814c2fab4802/data/latest",
    "Weeks","Total Stake Rewards in USD","Staking Rewards Distributed in USD each Week", "https://app.flipsidecrypto.com/velocity/queries/4270ef09-b468-4bc1-a21e-814c2fab4802")
    
    bar_charts("https://node-api.flipsidecrypto.com/api/v2/queries/40622345-0900-4ca8-9be1-475c678ce2fb/data/latest",
    "Weeks","# LUNA IBC-ed out","Weekly # of LUNA IBC-ed out Grouped By Recipient Network", "https://app.flipsidecrypto.com/velocity/queries/4270ef09-b468-4bc1-a21e-814c2fab4802","Recipient Networks")

    st.markdown("---")
    st.text("")
    colu1, colu2 = st.columns(2)
    with colu1:
        donuts("https://node-api.flipsidecrypto.com/api/v2/queries/2a3438be-5e49-4d67-ab71-b7e2c84773fa/data/latest",
        "Validators", "Total Stake Rewards", "Top 10 Validators Grouped by Stake Reward Distribution", "https://app.flipsidecrypto.com/velocity/queries/2a3438be-5e49-4d67-ab71-b7e2c84773fa")

    with colu2:
        donuts("https://node-api.flipsidecrypto.com/api/v2/queries/7f50f644-166f-463d-82ba-6dbfa773ec7a/data/latest",
    "Recipient Networks","# LUNA IBC-ed out","# of LUNA IBC-ed out Distribution Grouped By Recipient Network", "https://app.flipsidecrypto.com/velocity/queries/7f50f644-166f-463d-82ba-6dbfa773ec7a")
    
    image_fetch('vestschedule.png', 'LUNA Vesting Schedule', 'https://medium.com/terra-money/terra-2-0-luna-airdrop-calculation-logic-3eb752c25837')

    
        


