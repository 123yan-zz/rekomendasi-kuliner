import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============= CONFIGURASI =============
st.set_page_config(page_title="📍 Wisata Kuliner Karanganyar", layout="wide")

kuliner_file = "data1/kec.kra kuliner.xlsx"

# Cek file data kuliner
try:
    df = pd.read_excel(kuliner_file, engine="openpyxl")
except:
    df = pd.DataFrame(columns=['No','Nama_Tempat','Menu_Spesial','Rating','Ulasan','Jam_Buka','Alamat','Gambar'])

# === File akun admin ===
akun_admin_file = "data/admin_accounts.xlsx"

# Buat folder data jika belum ada
if not os.path.exists("data"):
    os.makedirs("data")

# Akun default (selalu ada minimal 1 akun)
DEFAULT_ACCOUNTS = pd.DataFrame([["admin", "123"]], columns=["Username", "Password"])

# Kalau file akun belum ada → buat baru dengan akun default
if not os.path.exists(akun_admin_file):
    DEFAULT_ACCOUNTS.to_excel(akun_admin_file, index=False)
else:
    df_admin = pd.read_excel(akun_admin_file)
    if df_admin.empty:
        DEFAULT_ACCOUNTS.to_excel(akun_admin_file, index=False)

# === Inisialisasi session state ===
if "role" not in st.session_state:
    st.session_state.role = None

# Fungsi untuk cek login
def check_login(username, password):
    df_admin = pd.read_excel(akun_admin_file)
    if ((df_admin["Username"] == username) & (df_admin["Password"] == password)).any():
        return True
    return False

# ============= LOGIN PAGE =============
if st.session_state.role is None:
    st.title("🍜 Wisata Kuliner Karanganyar")
    st.subheader("Masuk ke Sistem")

    # Tab utama: Pengguna & Admin
    tab1, tab2 = st.tabs(["👤 Pengguna", "🔑 Admin"])

    # ---------------- PENGGUNA ----------------
    with tab1:
        st.info("Masuk sebagai **Pengguna** untuk melihat kuliner.")
        if st.button("Masuk sebagai Pengguna"):
            st.session_state.role = "Pengguna"
            st.rerun()

    # ---------------- ADMIN ----------------
    with tab2:
        # Sub-tab untuk admin
        login_tab, reg_tab = st.tabs(["Login Admin", "Registrasi Admin"])

        # Login Admin
        with login_tab:
            username = st.text_input("Username Admin", key="login_admin_user")
            password = st.text_input("Password Admin", type="password", key="login_admin_pass")
            if st.button("Login Admin"):
                if check_login(username, password):
                    st.session_state.role = "Admin"
                    st.success("✅ Login berhasil sebagai Admin")
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")

        # Registrasi Admin
        with reg_tab:
            new_admin = st.text_input("Buat Username Admin", key="reg_admin_user")
            new_pass = st.text_input("Buat Password Admin", type="password", key="reg_admin_pass")
            if st.button("Daftar Admin"):
                if new_admin and new_pass:
                    df_admin = pd.read_excel(akun_admin_file)
                    if new_admin in df_admin["Username"].values:
                        st.warning("⚠️ Username Admin sudah ada, silakan pilih yang lain.")
                    else:
                        new_row = pd.DataFrame([[new_admin, new_pass]], columns=["Username", "Password"])
                        df_admin = pd.concat([df_admin, new_row], ignore_index=True)
                        df_admin.to_excel(akun_admin_file, index=False)
                        st.success("✅ Registrasi Admin berhasil! Silakan login.")
                else:
                    st.error("❌ Username dan Password tidak boleh kosong.")


# ============= MENU PENGGUNA =============
elif st.session_state.role == "Pengguna":
    st.sidebar.title("🍴 Menu Pengguna")
    st.title("👤 Pengguna - Wisata Kuliner Karanganyar")

    menu_pengguna = st.sidebar.radio(
        "📌 Pilih Menu",
        ["🏠 Home", "📑 Data Kuliner", "🤖 Rekomendasi"]
    )

    # ================= HOME =================
    if menu_pengguna == "🏠 Home":

    # --- fungsi ambil gambar ---
        def get_base64_of_bin_file(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()

        img_path = 'foto/cover (1).jpg'
        if os.path.exists(img_path):
            img_base64 = get_base64_of_bin_file(img_path)
        else:
            img_base64 = ""

        # --- CSS ---
        st.markdown(f"""
        <style>
        .header-box {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
            url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            padding: 60px 20px;
            border-radius: 20px;
            color: white;
            text-align: left;
        }}
        .header-box h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header-box p {{
            font-size: 16px;
            line-height: 1.5;
        }}
        .button-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }}
        .button-custom {{
            background-color: #fff;
            color: #000;
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            text-decoration: none;
        }}
        @media (max-width: 768px) {{
            .header-box {{
                padding: 40px 15px;
                text-align: center;
            }}
            .button-container {{
                justify-content: center;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)

        # --- konten ---
        st.markdown(f"""
    <div class="header-box">
        <h1>🍜 Wisata Kuliner Karanganyar</h1>
        <p>Sistem Rekomendasi Kuliner Karanganyar berbasis website yang dapat digunakan sebagai
           preferensi untuk mencoba kuliner yang ada di Karanganyar.<br>
           Sistem rekomendasi ini berdasarkan menu spesial, rating, dan ulasan dari pengguna lain.<br>
           Jelajahi kuliner Karanganyar berdasarkan Menu Spesial </p>
    </div>
    """, unsafe_allow_html=True)

    # ================= DATA KULINER =================
    elif menu_pengguna == "📑 Data Kuliner":
        st.subheader("📑 Daftar Kuliner")

        if not df.empty:
            for _, row in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        img_path = os.path.join("foto", str(row["Gambar"]))
                        if os.path.exists(img_path):
                            st.image(img_path, width=150)
                        else:
                            st.write("📷 (No Image)")
                    with col2:
                        st.markdown(f"### {row['Nama_Tempat']}")
                        st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
                        st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} ulasan)")
                        st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
                        st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("⚠️ Belum ada data kuliner.")

   # ================= REKOMENDASI =================
    elif menu_pengguna == "🤖 Rekomendasi":
        st.subheader("🤖 Rekomendasi Kuliner")
        st.info("Masukkan menu spesial untuk mendapatkan rekomendasi yang relevan.")

    # --- Normalisasi kolom Menu_Spesial ---
        df['Menu_Spesial'] = df['Menu_Spesial'].fillna('')

    # --- Ambil daftar keyword dari data (asli dari Excel) ---
        keyword_set = set()
        for menu_item in df['Menu_Spesial']:
            for item in menu_item.split(","):
                kata_asli = item.strip()
                if kata_asli:
                    keyword_set.add(kata_asli)

        sorted_keywords = sorted(keyword_set)

    # --- Input dari pengguna ---
        options = ["📌 Masukkan menu spesial..."] + sorted_keywords
        menu_input = st.selectbox("🍜 Masukkan menu spesial:", options)
        submit = st.button("🔍 Cari Rekomendasi")

    # --- Proses rekomendasi ---
        if submit and menu_input != "📌 Masukkan menu spesial...":
        # Gunakan lowercase hanya untuk perhitungan cosine & pencarian
            menu_lower = menu_input.lower()

            semua_menu = df['Menu_Spesial'].tolist() + [menu_lower]
            vectorizer = CountVectorizer().fit_transform([m.lower() for m in semua_menu])
            cosine_sim = cosine_similarity(vectorizer)
            hasil_cosine_sim = cosine_sim[-1][:-1]
            df["cosine"] = hasil_cosine_sim

        # Normalisasi rating
            normalisasi_rating = (df['Rating'] - df['Rating'].min()) / (df['Rating'].max() - df['Rating'].min())
            df["norm_rating"] = normalisasi_rating

        # Collaborative score
            df["Hasil_CF_Pembilang"] = hasil_cosine_sim * normalisasi_rating * df["Ulasan"]
            df["Hasil_CF_Penyebut"] = hasil_cosine_sim * df["Ulasan"]
            collaborative_score = df["Hasil_CF_Pembilang"] / df["Hasil_CF_Penyebut"]
            collaborative_score = collaborative_score.fillna(0)

        # Skor Hybrid
            df["Skor Hybrid"] = 0.6 * hasil_cosine_sim + 0.4 * collaborative_score

        # Rekomendasi relevan (case-insensitive, tapi tampil tetap sesuai Excel)
            rekomendasi_relevan = df[df['Menu_Spesial'].str.lower().str.contains(menu_lower, na=False)].copy()
            rekomendasi_relevan = rekomendasi_relevan[rekomendasi_relevan["Skor Hybrid"] > 0]
            rekomendasi_relevan = rekomendasi_relevan.sort_values(
            by=["Skor Hybrid", "Rating", "Ulasan"], ascending=[False, False, False]
            )

        # Rekomendasi lain
            rekomendasi_lain = df[~df['Menu_Spesial'].str.lower().str.contains(menu_lower, na=False)].copy()
            rekomendasi_lain = rekomendasi_lain[
            (rekomendasi_lain["Skor Hybrid"] > 0.5) & (rekomendasi_lain["Rating"] > 4.0)
            ]
            rekomendasi_lain = rekomendasi_lain.sort_values(by="Skor Hybrid", ascending=False)

        # --- Tampilkan hasil ---
            if rekomendasi_relevan.empty:
                st.warning(f"❌ Tidak ada tempat dengan menu spesial '{menu_input}'")
            else:
                st.subheader(f"📍 Rekomendasi Utama: {menu_input}")
            for _, row in rekomendasi_relevan.iterrows():
                col1, col2 = st.columns([1, 3])
                with col1:
                    img_path = os.path.join("foto", row["Gambar"])
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                with col2:
                    st.markdown(f"### {row['Nama_Tempat']}")
                    st.markdown(f"🍽️ {row['Menu_Spesial']}")  # tampil sesuai Excel
                    st.markdown(f"⭐ {row['Rating']} ({row['Ulasan']} ulasan)")
                    st.markdown(f"🕒 {row['Jam_Buka']}")
                    st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
                st.markdown("---")

            if not rekomendasi_lain.empty:
                st.subheader("🔍 Rekomendasi Lain yang Mungkin Cocok:")
            for _, row in rekomendasi_lain.iterrows():
                col1, col2 = st.columns([1, 3])
                with col1:
                    img_path = os.path.join("foto", row["Gambar"])
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                with col2:
                    st.markdown(f"### {row['Nama_Tempat']}")
                    st.markdown(f"🍽️ {row['Menu_Spesial']}")  # tetap sesuai Excel
                    st.markdown(f"⭐ {row['Rating']} ({row['Ulasan']} ulasan)")
                    st.markdown(f"🕒 {row['Jam_Buka']}")
                    st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
                st.markdown("---")


    # ================= Logout =================
    if st.sidebar.button("🔙 Keluar"):
        st.session_state.role = None
        st.rerun()

# ============= MENU ADMIN =============
elif st.session_state.role == "Admin":
    st.sidebar.title("⚙️ Menu Admin")
    st.title("📌 Admin - Wisata Kuliner Karanganyar")
    
    menu_admin = st.sidebar.radio(
        "📌 Menu Admin",
        ["📊 Lihat Data", "➕ Tambah Data", "❌ Hapus dan Edit Data"]
    )

    # ================= Lihat Data =================
    if menu_admin == "📊 Lihat Data":
        st.subheader("📊 Daftar Kuliner")
        if not df.empty:
            for _, row in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        img_path = os.path.join("foto", str(row["Gambar"]))
                        if os.path.exists(img_path):
                            st.image(img_path, width=150)
                        else:
                            st.write("📷 (No Image)")
                    with col2:
                        st.markdown(f"### {row['Nama_Tempat']}")
                        st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
                        st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} Ulasan)")
                        st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
                        st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("⚠️ Belum ada data kuliner.")

    # ================= Tambah Data =================
    elif menu_admin == "➕ Tambah Data":
        st.subheader("➕ Tambah Data Kuliner")

        if "tambah_selesai" not in st.session_state:
            st.session_state.tambah_selesai = False

        if st.session_state.tambah_selesai:
            st.success("✅ Data berhasil ditambahkan!")
            if st.button("➕ Tambah Data Lagi"):
                st.session_state.tambah_selesai = False
                st.rerun()
        else:
            with st.form("TambahData"):
                nama = st.text_input("Nama Tempat")
                menu = st.text_input("Menu Spesial")
                rating = st.number_input("Rating", 0.0, 5.0, step=0.1)
                ulasan = st.number_input("Jumlah Ulasan", 0, step=1)
                alamat = st.text_input("Alamat (Google Maps Link)")
                jam = st.text_input("Jam Buka")
                gambar_file = st.file_uploader("Upload Gambar", type=["jpg", "jpeg", "png"])

                gambar_nama = ""
                if gambar_file:
                    if not os.path.exists("foto"):
                        os.makedirs("foto")
                    gambar_nama = gambar_file.name
                    save_path = os.path.join("foto", gambar_nama)
                    with open(save_path, "wb") as f:
                        f.write(gambar_file.getbuffer())
                    st.image(save_path, caption="📷 Preview Gambar", width=200)

                submitted = st.form_submit_button("Tambah Data")

                if submitted:
                    if nama and menu and gambar_nama:
                        next_no = 1 if df.empty else df["No"].max() + 1
                        new_row = pd.DataFrame(
                            [[next_no, nama, menu, rating, ulasan, alamat, jam, gambar_nama]],
                            columns=df.columns
                        )
                        df = pd.concat([df, new_row], ignore_index=True)
                        df.to_excel(kuliner_file, index=False, engine="openpyxl")
                        st.session_state.tambah_selesai = True
                        st.rerun()
                    else:
                        st.warning("⚠️ Nama, Menu, dan Gambar wajib diisi!")

    # ================= Edit / Hapus Data =================
    elif menu_admin == "❌ Hapus dan Edit Data":
        st.subheader("✏️ Hapus dan Edit Data")

        if not df.empty:
            pilihan = st.selectbox("Pilih Nama Tempat Kuliner", df["Nama_Tempat"].tolist())
            row_index = df[df["Nama_Tempat"] == pilihan].index[0]
            row = df.loc[row_index]

            col1, col2 = st.columns([1, 3])
            with col1:
                img_path = os.path.join("foto", str(row["Gambar"]))
                if os.path.exists(img_path):
                    st.image(img_path, width=200)
                else:
                    st.write("📷 (No Image)")
            with col2:
                st.markdown(f"### {row['Nama_Tempat']}")
                st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
                st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} ulasan)")
                st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
                st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️ Edit Data"):
                        st.session_state.edit_mode = True
                        st.session_state.row_index = row_index
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Hapus Data"):
                        st.session_state.confirm_delete = True
                        st.session_state.row_index = row_index
                        st.rerun()

            # Mode Edit
            if st.session_state.get("edit_mode", False) and st.session_state.row_index == row_index:
                st.subheader("📝 Edit Data Kuliner")
                with st.form("edit_form"):
                    nama = st.text_input("Nama Tempat", value=row["Nama_Tempat"])
                    menu = st.text_input("Menu Spesial", value=row["Menu_Spesial"])
                    rating = st.number_input("Rating", 0.0, 5.0, value=float(row["Rating"]), step=0.1)
                    ulasan = st.number_input("Jumlah Ulasan", 0, value=int(row["Ulasan"]), step=1)
                    jam = st.text_input("Jam Buka", value=row["Jam_Buka"])
                    alamat = st.text_input("Alamat (Google Maps Link)", value=row["Alamat"])
                    gambar_file = st.file_uploader("Ganti Gambar (Opsional)", type=["jpg", "jpeg", "png"])

                    gambar_nama = row["Gambar"]
                    if gambar_file:
                        if not os.path.exists("foto"):
                            os.makedirs("foto")
                        gambar_nama = gambar_file.name
                        save_path = os.path.join("foto", gambar_nama)
                        with open(save_path, "wb") as f:
                            f.write(gambar_file.getbuffer())
                        st.image(save_path, caption="📷 Preview Baru", width=150)

                    simpan = st.form_submit_button("💾 Simpan Perubahan")
                    if simpan:
                        df.loc[row_index, ["Nama_Tempat", "Menu_Spesial", "Rating", "Ulasan", "Jam_Buka", "Alamat", "Gambar"]] = \
                            [nama, menu, rating, ulasan, jam, alamat, gambar_nama]
                        df.to_excel(kuliner_file, index=False, engine="openpyxl")
                        st.success(f"✅ Data '{nama}' berhasil diperbarui!")
                        st.session_state.edit_mode = False
                        st.rerun()

            # Mode Konfirmasi Hapus
            if st.session_state.get("confirm_delete", False) and st.session_state.row_index == row_index:
                st.error(f"⚠️ Apakah Anda yakin ingin menghapus data '{row['Nama_Tempat']}'?")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Ya, Hapus"):
                        df = df.drop(row_index)
                        df.to_excel(kuliner_file, index=False, engine="openpyxl")
                        st.success(f"✅ Data '{row['Nama_Tempat']}' berhasil dihapus!")
                        st.session_state.confirm_delete = False
                        st.rerun()
                with col_c2:
                    if st.button("❌ Batal"):
                        st.session_state.confirm_delete = False
                        st.rerun()
        else:
            st.info("⚠️ Belum ada data kuliner.")

    # ================= Logout =================
    if st.sidebar.button("🔙 Keluar"):
        st.session_state.role = None
        st.rerun()


