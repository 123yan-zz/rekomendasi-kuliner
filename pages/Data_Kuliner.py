import streamlit as st
import pandas as pd
import os

#konfigurasi awal halaman
st.set_page_config(page_title=" 📍 Data Kuliner Karanganyar", layout="wide")

# awal Judul utama dan deskripsi
st.title("📍 Kuliner Karanganyar")
st.write("""
Kuliner karanganyar sendiri memiliki berbagai macam. Contohnya ada salah Satu kuliner khas dari Karanganyar 
         yaitu Soto Karang, dan lain-lainnya.
         Berikut merupakan macam macam kuliner Karanganyar.
""")
# akhir Judul utama dan deskripsi

st.markdown("## 📍 Daftar Kuliner")

# Membaca Data yang ada di Excel
try:
    df = pd.read_excel("data/kec.kra kuliner.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"❌ Gagal membaca file Excel: {e}")
    st.stop()

# Menampilkan kolom data kuliner dengan jumlah 3 kolom
kolom = 3
baris = [st.columns(kolom) for _ in range((len(df) + kolom - 1) // kolom)]

row_index = 0
col_index = 0

#looping untuk menampilkan data yang ada diexcel
for idx, (_, row) in enumerate(df.iterrows()):
    if col_index >= kolom:
        col_index = 0
        row_index += 1
    if row_index >= len(baris):
        baris.append(st.columns(kolom))

    #awal menampilkan gambar kuliner dengan tinggi kotak 500
    col = baris[row_index][col_index]
    with col.container(height=500):  # Tinggi kotak setiap item
        image_path = os.path.join("foto", row["Gambar"])
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.write("📷 Gambar tidak ditemukan.")
    #akhir menampilkan gambar kuliner dengan tinggi kotak 500
    #awal menampilkan detail informasi
        st.markdown(f"### {row['Nama_Tempat']}")
        st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
        st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} Ulasan)")
        st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
        st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
    #akhir menampilkan detail informasi
    col_index += 1 # digunakan untuk menggeser penempatan jika kolom sudah memenuhi
