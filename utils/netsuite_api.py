import os
from requests_oauthlib import OAuth1Session
import streamlit as st
import logging

# NetSuite API Credentials
ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")
CONSUMER_KEY = os.getenv("NETSUITE_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("NETSUITE_CONSUMER_SECRET")
TOKEN_ID = os.getenv("NETSUITE_TOKEN_ID")
TOKEN_SECRET = os.getenv("NETSUITE_TOKEN_SECRET")

# Base URL for NetSuite REST API
BASE_URL = f"https://{ACCOUNT_ID.lower().replace('_', '-')}.suitetalk.api.netsuite.com/services/rest"

def create_netsuite_session():
    try:
        session = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=TOKEN_ID,
            resource_owner_secret=TOKEN_SECRET,
            realm=ACCOUNT_ID,
            signature_method="HMAC-SHA256",
        )
        return session
    except Exception as e:
        st.error("Failed to connect to NetSuite API.")
        logging.error(f"Error in create_netsuite_session: {e}")
        return None

@st.cache_data
def run_suiteql(query, limit=None, offset=None):
    session = create_netsuite_session()
    if not session:
        return None

    url = f"{BASE_URL}/query/v1/suiteql"
    params = {}
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset

    headers = {"Prefer": "transient", "Content-Type": "application/json"}
    payload = {"q": query}

    try:
        response = session.post(url, headers=headers, json=payload, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error("Error fetching data from NetSuite.")
        logging.error(f"Error in run_suiteql: {e}")
        return None