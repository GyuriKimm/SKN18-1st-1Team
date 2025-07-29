from pydoc import text
from typing import Container
import streamlit as st

row1 = st.columns(3)
row2 = st.columns(3)

for col in row1 + row2:
    tile = col.container(height=120)
    tile.title(":balloon:")

st.subheader("use height to control the height of the container")

long_text = "Lorem ipsum." *1000
with st.container(height=300):
    st.markdown(long_text) 