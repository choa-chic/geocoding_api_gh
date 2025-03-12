import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote_plus

def geocode_address(address):
    response = requests.get(f"http://flask:9080/geocode?address={quote_plus(address)}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def main():
    st.title("Geocode Address")
    
    address = st.text_input("Enter an address:")
    
    if st.button("Geocode"):
        result = geocode_address(address)
        if result:
            st.write("Geocoding Result:")
            df = pd.DataFrame(result)
            st.dataframe(df)
            
            lat, lon = result[0]['lat'], result[0]['lon']
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
        else:
            st.error("Geocoding failed")

if __name__ == '__main__':
    main()