import streamlit as st
import pandas as pd
import numpy as np

with st.container():
    st.write("안의 공간")

    st.bar_chart(np.random.randn(50, 3))

    st.write("밖의 공간")

