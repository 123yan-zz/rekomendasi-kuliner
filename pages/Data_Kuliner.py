import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title=" 📍 Data Kuliner Karanganyar", layout="wide")

# Judul utama dan Menu-menu yang ada di sistem
st.title("📍 Kuliner Karanganyar")
col1, col2, col3 = st.columns ([1,1,1])
with col1:
    if st.button("🏠 Beranda"):
        st.switch_page("home.py")
with col2:
    if st.button("📍 Lihat Data Kuliner"):
        st.switch_page("pages/Data_Kuliner.py")
with col3:
    if st.button("🍽️ Lihat Rekomendasi Kuliner"):
        st.switch_page("pages/Rekomendasi.py")

st.write("""
Kuliner karanganyar sendiri memiliki berbagai macam. Contohnya ada kuliner khas dari Karanganyar yaitu Sate Kelinci, dan lain-lainnya.
         Berikut merupakan macam macam kuliner Karanganyar.
""")

st.markdown("## 📍 Daftar Kuliner")

# Load data dari Excel
try:
    df = pd.read_excel("data/kec.kra kuliner.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"❌ Gagal membaca file Excel: {e}")
    st.stop()


# Tampilkan data dalam 3 kolom
kolom = 3
baris = [st.columns(kolom) for _ in range((len(df) + kolom - 1) // kolom)]

row_index = 0
col_index = 0

for idx, (_, row) in enumerate(df.iterrows()):
    if col_index >= kolom:
        col_index = 0
        row_index += 1
    if row_index >= len(baris):
        baris.append(st.columns(kolom))

    col = baris[row_index][col_index]
    with col.container(height=500):  # Tinggi kotak per item
        image_path = os.path.join("foto", row["Gambar"])
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.write("📷 Gambar tidak ditemukan.")

        st.markdown(f"### {row['Nama_Tempat']}")
        st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
        st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} Ulasan)")
        st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
        st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)

    col_index += 1