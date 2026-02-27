import requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='FactoryIQ Portal', layout='wide')
base_url = st.sidebar.text_input('API URL', 'http://localhost:8000')
token = st.sidebar.text_input('JWT Token', type='password')
headers = {'Authorization': f'Bearer {token}'} if token else {}

st.title('Nexgile – FactoryIQ Manufacturing Excellence Portal')
page = st.sidebar.selectbox('Page', ['Executive Dashboard', 'Portfolio View', 'Project Detail View', 'Production Dashboard', 'Quality Dashboard', 'Supply Chain View', 'After-Sales View', 'Reports Page'])


def get(path):
    try:
        return requests.get(f'{base_url}{path}', headers=headers, timeout=10).json()
    except Exception as exc:
        return {'error': str(exc)}

if page == 'Executive Dashboard':
    data = get('/analytics/executive')
    st.metric('On-time Delivery %', data.get('on_time_delivery', 0))
    st.metric('Capacity Utilization %', data.get('capacity_utilization', 0))
elif page == 'Portfolio View':
    rows = get('/projects')
    st.dataframe(pd.DataFrame(rows if isinstance(rows, list) else []))
elif page == 'Project Detail View':
    pid = st.text_input('Project ID')
    if pid:
        st.json(get(f'/projects/{pid}/health'))
elif page == 'Production Dashboard':
    metrics = get('/production/metrics')
    st.json(metrics)
elif page == 'Quality Dashboard':
    spc = get('/quality/spc')
    df = pd.DataFrame(spc.get('chart', []))
    if not df.empty:
        st.plotly_chart(px.line(df, x='sample', y='value', title='SPC Control Chart'))
elif page == 'Supply Chain View':
    st.subheader('Inventory')
    st.dataframe(pd.DataFrame(get('/inventory')))
    st.subheader('Shipments')
    st.dataframe(pd.DataFrame(get('/shipments')))
elif page == 'After-Sales View':
    st.dataframe(pd.DataFrame(get('/rmas')))
elif page == 'Reports Page':
    payload = {'report_type': 'executive', 'metrics': {'otd': 93, 'yield': 98}}
    if st.button('Generate Report'):
        st.json(requests.post(f'{base_url}/reports/generate', headers=headers, json=payload, timeout=10).json())
