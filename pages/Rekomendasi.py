import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="🍽️ Rekomendasi Kuliner", layout="wide")
st.title("🍽️ Rekomendasi Kuliner Karanganyar")

#Membaca data Excel
try:
    df = pd.read_excel("data/kec.kra kuliner.xlsx", engine="openpyxl")
except Exception as e:
    st.error(f"❌ Gagal membaca file Excel: {e}")
    st.stop()

# Validasi kolom yang ada pada excel
required_cols = ['Nama_Tempat', 'Menu_Spesial', 'Rating', 'Ulasan', 'Jam_Buka', 'Alamat', 'Gambar']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Format Excel tidak sesuai. Pastikan kolom: " + ", ".join(required_cols))
    st.stop()
df['Menu_Spesial'] = df['Menu_Spesial'].fillna('')

# Ambil daftar menu spesial
keyword_set = set()
for menu in df['Menu_Spesial']:
    for item in menu.split(","):
        kata = item.strip()
        if kata:
            keyword_set.add(kata)
sorted_keywords = sorted(keyword_set)

# input yang dilakukan oleh pengguna
st.markdown("### 📌 Silakan pilih kata kunci dari menu spesial yang tersedia di bawah ini:")
options = ["📌 Pilih menu spesial..."] + sorted_keywords
menu_input = st.selectbox("🍜 Pilih kata kunci menu spesial yang Anda inginkan:", options)

# inisialisasi variabel
rekomendasi_relevan = pd.DataFrame()
rekomendasi_lain = pd.DataFrame()

# dilakukan filtering berdasarkan menu spesial
if menu_input != "📌 Pilih menu spesial...":
    df_filtered = df[df['Menu_Spesial'].str.contains(menu_input, case=False, na=False)].copy()

    if df_filtered.empty:
        st.warning(f"❌ Tidak ada tempat dengan menu spesial '{menu_input}'")
    else:
        # Perhitungan content-based dengan cosine similarity
        semua_menu = df['Menu_Spesial'].tolist() + [menu_input]
        vectorizer = CountVectorizer().fit_transform(semua_menu)
        cosine_sim = cosine_similarity(vectorizer)
        hasil_cosine_sim = cosine_sim[-1][:-1]
        df["cosine"] = hasil_cosine_sim

        # Normalisasi rating
        normalisasi_rating = (df['Rating'] - df['Rating'].min()) / (df['Rating'].max() - df['Rating'].min())
        df["norm_rating"] = normalisasi_rating

        # Perhitungan collaborative filtering (dengan weighted sum)
        df["Hasil_CF_Pembilang"] = hasil_cosine_sim * normalisasi_rating * df["Ulasan"]
        df["Hasil_CF_Penyebut"] = hasil_cosine_sim * df["Ulasan"]
        collaborative_score = df["Hasil_CF_Pembilang"] / df["Hasil_CF_Penyebut"]
        collaborative_score = collaborative_score.fillna(0)

        # Perhitungan skor akhir Hybrid
        df["Skor Hybrid"] = 0.6 * hasil_cosine_sim + 0.4 * collaborative_score

        # Rekomendasi utama
        rekomendasi_relevan = df[df['Menu_Spesial'].str.contains(menu_input, case=False, na=False)].copy()
        rekomendasi_relevan = rekomendasi_relevan[rekomendasi_relevan["Skor Hybrid"] > 0]
        # Dilakukan pembulatan skor hybrid agar sama dan adil
        rekomendasi_relevan["Hybrid_Round"] = rekomendasi_relevan["Skor Hybrid"].round(3)
        # Apabila skor hybrid sama diurutkan dengan: Hybrid bulat → Rating → Ulasan
        rekomendasi_relevan = rekomendasi_relevan.sort_values(by=["Hybrid_Round", "Rating", "Ulasan"],
        ascending=[False, False, False]).drop(columns=["Hybrid_Round"])

        # Untuk menampilkan Rekomendasi lain yang dianggap masih relevan dengan pemilahan menu pengguna
        rekomendasi_lain = df[~df['Menu_Spesial'].str.contains(menu_input, case=False, na=False)].copy()
        rekomendasi_lain = rekomendasi_lain[rekomendasi_lain["Skor Hybrid"] > 0.5]
        rekomendasi_lain = rekomendasi_lain[rekomendasi_lain["Rating"] > 4.0]
        rekomendasi_lain = rekomendasi_lain.sort_values(by='Skor Hybrid', ascending=False)

        # Untuk menampilkan rekomendasi utama (relevan)
        if not rekomendasi_relevan.empty:
            st.subheader(f"📍 Rekomendasi Tempat Kuliner dengan menu spesial '{menu_input}':")
            for _, row in rekomendasi_relevan.iterrows():
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
                        #st.markdown(f"📊 **Skor Hybrid:** `{row['Skor Hybrid']:.4f}`")
                        st.markdown("---")

        # Untuk menampilkan rekomendasi lain jika ada (yang masih ada relevansi)
        if not rekomendasi_lain.empty:
            st.subheader("🔍 Rekomendasi Lain yang Mungkin Anda Suka:")
            for _, row in rekomendasi_lain.iterrows():
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
                        #st.markdown(f"📊 **Skor Hybrid:** `{row['Skor Hybrid']:.4f}`")
                        st.markdown("---")
