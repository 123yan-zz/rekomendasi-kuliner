import streamlit as st
import os
import base64

st.set_page_config(page_title="🏠 Kuliner Karanganyar", layout="wide")
st.markdown("## 🔍Sistem Rekomendasi Kuliner Karanganyar")

#memuat Foto pada sistem
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_path = 'foto/cover (1).jpg'
img_base64 = get_base64_of_bin_file(img_path)

# Styling CSS
st.markdown(f"""
    <style>
    .header-box {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        padding: 100px 20px;
        border-radius: 20px;
        height: 420px;
        color: white;
        text-align: left;
    }}
    .button-container {{
        display: flex;
        justify-content: left;
        gap: 30px;
        margin-top: 20px;
    }}
    .button-custom {{
        background-color: #fff;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
    }}
    </style>
""", unsafe_allow_html=True)

# Header Box
st.markdown(f"""
<div class="header-box">
    <h1>🍜Wisata Kuliner Karanganyar</h1><br>
    <p style="font-size: 18px;">Sistem Rekomendasi Kuliner Karanganyar berbasis website yang dapat digunakan sebagai
            preferensi untuk mencoba kuliner yang ada di Karanganyar.<br> Sistem rekomendasi ini berdasarkan menu spesial
            rating dan ulasan dari pengguna lain.</p> 
    <div class="button-container"><br>
        <a href='/Data_Kuliner' target='_self' class="button-custom">📍 Lihat Data Kuliner</a>
        <a href='/Rekomendasi' target='_self' class="button-custom">🍽️ Lihat Rekomendasi Kuliner</a>
    </div>
</div>
""", unsafe_allow_html=True)
