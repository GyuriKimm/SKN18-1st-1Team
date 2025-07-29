import streamlit as st
import numpy as np

col1, col2 = st.columns([3,1])
data = np.random.randn(10, 1)

col1.subheader("와이드 차트")
col1.line_chart(data)

col2.subheader("작은 차트")
col2.write(data)