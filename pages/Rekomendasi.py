import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Konfigurasi halaman
st.set_page_config(page_title="🍽️ Rekomendasi Kuliner", layout="wide")

st.title("🍽️ Rekomendasi Kuliner Karanganyar")

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

# Load data
try:
    df = pd.read_excel("data/kec.kra kuliner.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"❌ Gagal membaca file Excel: {e}")
    st.stop()

# Validasi kolom
required_cols = ['Nama_Tempat', 'Menu_Spesial', 'Rating', 'Ulasan', 'Jam_Buka', 'Alamat', 'Gambar']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Format Excel tidak sesuai. Pastikan kolom: " + ", ".join(required_cols))
    st.stop()

# Ambil daftar kata kunci unik dari Menu_Spesial
df['Menu_Spesial'] = df['Menu_Spesial'].fillna('')  # isi NaN dengan string kosong

keyword_set = set()
for menu in df['Menu_Spesial']:
    for item in menu.split(","):
        kata = item.strip()
        if kata:
            keyword_set.add(kata)

sorted_keywords = sorted(keyword_set)

#Teks instruksi sebelum input
st.markdown("### 📌 Silakan pilih kata kunci dari menu spesial yang tersedia di bawah ini:")

options = ["📌 Pilih menu spesial..."] + sorted_keywords
menu_input = st.selectbox("🍜 Pilih kata kunci menu spesial yang Anda inginkan:", options)

if menu_input != "📌 Pilih menu spesial...":
    # Filter data yang menu spesial-nya mengandung kata tersebut
    df_filtered = df[df['Menu_Spesial'].str.contains(menu_input, case=False, na=False)].copy()

    if df_filtered.empty:
        st.warning(f"❌ Silahkan untuk memilih berdasarkan menu spesial terlebih dahulu '{menu_input}'")
    else:
        # Vektorisasi menggunakan semua data (untuk menghitung similarity terhadap semua restoran)
        semua_menu = df['Menu_Spesial'].tolist() + [menu_input]
        vectorizer = CountVectorizer().fit_transform(semua_menu)
        cosine_sim = cosine_similarity(vectorizer)
        hasil_cosine_sim = cosine_sim[-1][:-1]  # cosine antara input dan semua restoran
        df["cosine"] = hasil_cosine_sim

        # Normalisasi rating seluruh data (bukan hanya yang difilter)
        normalisasi_rating = (df['Rating'] - df['Rating'].min()) / (df['Rating'].max() - df['Rating'].min())
        df["norm_rating"] = normalisasi_rating

        # Collaborative score
        df["Hasil_CF_Pembilang"] = hasil_cosine_sim * normalisasi_rating * df["Ulasan"]
        df["Hasil_CF_Penyebut"] = hasil_cosine_sim * df["Ulasan"]
        collaborative_score = df["Hasil_CF_Pembilang"] / df["Hasil_CF_Penyebut"]
        collaborative_score = collaborative_score.fillna(0)

        # Skor Hybrid
        hasil_hybrid = 0.6 * hasil_cosine_sim + 0.4 * collaborative_score
        df["Skor Hybrid"] = hasil_hybrid

        # Filter lagi hanya data yang mengandung kata kunci, lalu urutkan
        df_filtered = df[df['Menu_Spesial'].str.contains(menu_input, case=False, na=False)].copy()
        df_filtered["Skor Hybrid"] = df["Skor Hybrid"]
        df_sorted = df_filtered[df_filtered["Skor Hybrid"] > 0].sort_values(by='Skor Hybrid', ascending=False)

        if df_sorted.empty:
            st.warning("❌ Tidak ada rekomendasi yang relevan dengan skor hybrid > 0.")
        else:
            st.subheader(f"📍 Rekomendasi Tempat Kuliner dengan menu spesial '{menu_input}':")

        # Tampilkan hasil
        for _, row in df_sorted.iterrows():
                with st.container():
                    col1, col2 = st.columns([1,3])
                    with col1:
                        image_path = os.path.join("foto", row["Gambar"])
                        if os.path.exists(image_path):
                            st.image(image_path, use_container_width=True)
                        else:
                            st.warning("📷 Gambar tidak ditemukan.")
                    with col2:
                        st.markdown(f"### {row['Nama_Tempat']}")
                        st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
                        st.markdown(f"⭐ **Rating:** {row['Rating']} ({int(row['Ulasan'])} ulasan)")
                        st.markdown(f"🕒 **Jam Operasional:** {row['Jam_Buka']}")
                        st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
                        st.markdown(f"📊 **Skor Hybrid:** `{row['Skor Hybrid']:.4f}`")
                        st.markdown("---")
else:
    st.info("Silakan pilih menu spesial untuk mendapatkan rekomendasi.")