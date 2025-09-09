import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🔑 Admin Panel", layout="wide")

# Folder data
if not os.path.exists("data"):
    os.makedirs("data")

# File akun admin
akun_file = "data/admin_accounts.xlsx"
if not os.path.exists(akun_file):
    df_akun = pd.DataFrame(columns=["Username", "Password"])
    df_akun.to_excel(akun_file, index=False, engine="openpyxl")

# Load akun admin
df_akun = pd.read_excel(akun_file, engine="openpyxl")

# Pastikan kolom Username & Password bersih (string, tanpa spasi)
df_akun["Username"] = df_akun["Username"].astype(str).str.strip()
df_akun["Password"] = df_akun["Password"].astype(str).str.strip()


# Session state
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ====================
# HALAMAN LOGIN / REGISTER
# ====================
if not st.session_state.admin_logged_in:

    if st.session_state.show_register:
        st.title("📝 Registrasi Admin Baru")

        with st.form("RegisterForm"):
            new_username = st.text_input("Username Baru")
            new_password = st.text_input("Password Baru", type="password")
            register_btn = st.form_submit_button("Daftar")

            if register_btn:
                if not new_username or not new_password:
                    st.warning("⚠️ Username dan Password wajib diisi.")
                elif new_username in df_akun["Username"].values:
                    st.error("❌ Username sudah terdaftar.")
                else:
                    new_row = pd.DataFrame([[new_username, new_password]], columns=["Username", "Password"])
                    df_akun = pd.concat([df_akun, new_row], ignore_index=True)
                    df_akun.to_excel(akun_file, index=False, engine="openpyxl")
                    st.success("✅ Registrasi berhasil! Silakan login.")
                    st.session_state.show_register = False
                    st.rerun()

        if st.button("🔙 Kembali ke Login"):
            st.session_state.show_register = False
            st.rerun()

    else:
        st.title("🔑 Login Admin")

        with st.form("LoginForm"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

            if login_btn:
                if ((df_akun["Username"] == str(username).strip()) & (df_akun["Password"] == str(password).strip())).any():
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("✅ Login berhasil!")
                    st.rerun()
                else:
                    st.error("❌ Username / Password salah")

        if st.button("📝 Daftar Akun Admin"):
            st.session_state.show_register = True
            st.rerun()
    st.stop()

# ====================
# PANEL ADMIN (SETELAH LOGIN)
# ====================
st.title("📂 Admin Panel – Kelola Data Kuliner")
st.write(f"👤 Login sebagai: **{st.session_state.admin_username}**")

menu_admin = st.sidebar.radio("📌 Menu Admin", ["📊 Lihat Data", "➕ Tambah Data", "❌ Hapus Data", "🚪 Logout"])

kuliner_file = "data/kec.kra kuliner.xlsx"
try:
    df = pd.read_excel(kuliner_file, engine="openpyxl")
except:
    df = pd.DataFrame(columns=['No','Nama_Tempat','Menu_Spesial','Rating','Ulasan','Jam_Buka','Alamat','Gambar'])

if menu_admin == "📊 Lihat Data":
    st.subheader("📊 Daftar Kuliner")

    if not df.empty:
        for _, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                # Kolom gambar
                with col1:
                    img_path = os.path.join("foto", str(row["Gambar"]))
                    if os.path.exists(img_path):
                        st.image(img_path, width=150)
                    else:
                        st.write("📷 (No Image)")
                
                # Kolom informasi
                with col2:
                    st.markdown(f"### {row['Nama_Tempat']}")
                    st.markdown(f"🍽️ **Menu Spesial:** {row['Menu_Spesial']}")
                    st.markdown(f"⭐ **Rating:** {row['Rating']} ({row['Ulasan']} Ulasan)")
                    st.markdown(f"🕒 **Jam Buka:** {row['Jam_Buka']}")
                    st.markdown(f"[📍 Lihat Lokasi]({row['Alamat']})", unsafe_allow_html=True)

                st.markdown("---")  # garis pemisah tiap item
    else:
        st.info("⚠️ Belum ada data kuliner.")

elif menu_admin == "➕ Tambah Data":
    st.subheader("➕ Tambah Data Kuliner")

    # Tambahkan state untuk cek apakah data berhasil disubmit
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

            # langsung preview setelah pilih file
            gambar_nama = ""
            if gambar_file:
                if not os.path.exists("foto"):
                    os.makedirs("foto")
                gambar_nama = gambar_file.name
                save_path = os.path.join("foto", gambar_nama)

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

# ===== tampilkan pesan sukses jika ada =====
if "success_message" in st.session_state and st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = ""  # kosongkan setelah ditampilkan


elif menu_admin == "❌ Hapus Data":
    st.subheader("✏️ Edit / ❌ Hapus Data Kuliner")

    if not df.empty:
        # Dropdown pilih nama tempat
        pilihan = st.selectbox("Pilih Nama Tempat Kuliner", df["Nama_Tempat"].tolist())

        # Ambil baris sesuai pilihan
        row_index = df[df["Nama_Tempat"] == pilihan].index[0]
        row = df.loc[row_index]

        # Tampilkan informasi
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

        # Mode edit
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

        # Mode konfirmasi hapus
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

elif menu_admin == "🚪 Logout":
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = ""
    st.success("✅ Anda sudah logout.")
    st.switch_page("home.py")
