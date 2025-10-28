import streamlit as st
import base64
from styles.custom_css import load_custom_css
from datetime import datetime
import folium
import re
from streamlit_folium import st_folium
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage


#  Konfigurasi Halaman
st.set_page_config(page_title="SIRA", page_icon="logo_sira.png", layout="wide")

# Load CSS
load_custom_css()
# ---- UI state
if "show_personal_modal" not in st.session_state:
    st.session_state["show_personal_modal"] = False

# Header
st.markdown(
    """
<div class="header-container">
    <div class="header-title">Intelligence Integrated System (IIS)</div>
    <div class="header-sub">
        <span class="sub-highlight">Kejaksaan Negeri Banyumas</span>
        <span class="separator">|</span>
        <span class="sub-normal">Bidang Intelijen</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    # Logo
    st.image("logo_kejaksaan.png")

    # Judul Menu
    st.markdown("<h3 class='sidebar-title'>Menu</h3>", unsafe_allow_html=True)

    # Navigasi
    opsi_raw = [
        "Beranda IIS",
        "SIRATA",
    ]
    pilihan = st.radio("", opsi_raw, label_visibility="collapsed", index=0)
    menu = pilihan

    # --- Tambah: reset state saat pindah menu ---
    def _reset_states_on_menu_change():
        prev = st.session_state.get("_active_menu")
        if prev is None:
            st.session_state["_active_menu"] = menu
            return
        if prev != menu:
            # bersihkan semua jejak form & output lintas-menu
            for k in [
                # SIRATA
                "sirata_ready",
                "buat_lapinsus",
                "sirata_payload",
                "lapinsus_perihal",
                "lapinsus_nomor_pengantar",
                "lapinsus_nomor_lik",
            ]:
                st.session_state.pop(k, None)
            st.session_state["_active_menu"] = menu

    _reset_states_on_menu_change()

    # Bagian bawah
    now = datetime.now()
    waktu = now.strftime("%H:%M")
    laporan_hari_ini = 5

    st.markdown(
        f"""
        <div class='sidebar-bottom'>
        <div class='sidebar-time'>{waktu}</div>
        <div class='sidebar-location'>Banyumas, Jawa Tengah</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if menu == "Beranda IIS":
    st.markdown(
        """
    <div class="card" style="padding:15px; margin-bottom:25px;">
    <h4 style="text-align:center;">Peta Sebaran Wilayah Kejaksaan Negeri Banyumas
    </h4>
    """,
        unsafe_allow_html=True,
    )

    # Buat peta (pusat Banyumas)
    map_banyumas = folium.Map(location=[-7.5, 109.3], zoom_start=11, control_scale=True)

    # Titik Kejaksaan
    kejaksaan_points = [
        {
            "name": "Kejaksaan Negeri Purwokerto",
            "lat": -7.4249,
            "lon": 109.2349,
            "color": "red",
        },
        {
            "name": "Kejaksaan Negeri Banyumas",
            "lat": -7.5154,
            "lon": 109.2975,
            "color": "green",
        },
    ]
    for k in kejaksaan_points:
        folium.Marker(
            [k["lat"], k["lon"]],
            popup=f"<b>{k['name']}</b>",
            icon=folium.Icon(color=k["color"], icon="university", prefix="fa"),
        ).add_to(map_banyumas)

    # Titik kecamatan
    kecamatan_coords = {
        "Sumbang": [-7.3582, 109.2551],
        "Kembaran": [-7.4183, 109.2709],
        "Sokaraja": [-7.4548, 109.2783],
        "Kalibagor": [-7.4582, 109.3391],
        "Patikraja": [-7.4950, 109.2640],
        "Banyumas": [-7.5142, 109.2907],
        "Somagede": [-7.5613, 109.3438],
        "Kebasen": [-7.5688, 109.2111],
        "Kemranjen": [-7.5834, 109.2073],
        "Sumpiuh": [-7.6051, 109.3758],
        "Tambak": [-7.6194, 109.4592],
    }
    for kec, coord in kecamatan_coords.items():
        folium.CircleMarker(
            location=coord,
            radius=7,
            color="#00796b",
            fill=True,
            fill_opacity=0.7,
            popup=f"<b>{kec}</b>",
        ).add_to(map_banyumas)

    # Fit ke semua titik (kejaksaan + kecamatan)
    all_points = [[v[0], v[1]] for v in kecamatan_coords.values()] + [
        [k["lat"], k["lon"]] for k in kejaksaan_points
    ]
    if all_points:
        map_banyumas.fit_bounds(all_points)

    # Render responsif
    st_data = st_folium(map_banyumas, use_container_width=True, height=560)

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    # Logo & Profil Kejaksaan
    try:
        with open("logo_kejaksaan.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_img_src = f"data:image/png;base64,{logo_b64}"
    except Exception:
        logo_img_src = ""

    with col1:
        st.markdown(
            f"""
        <div class="card"
            style="
                display:flex;
                flex-direction:column;
                align-items:center;
                justify-content:center;
                text-align:center;
                padding-top:30px;
                text-align:center;
                padding:47px 10px;
            ">
            <img src="{logo_img_src}" width="100" style="margin-bottom:2px;">
            <h4 style="margin:-2px 0; transform:translateX(15px); color:#00796b;">ID : 005634</h4>
            <h3 style="margin:-10px 0; transform:translateX(15px); font-weight:800;">Banyumas</h3>
            <p style="margin:3px 0;">Jl. Ajibarang Secang No.285, Banyumas, Saudagaran</p>
            <p style="margin:3px 0;"><b>Telp:</b> 0281796018</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Performa Satker
    with col2:
        st.markdown(
            """
        <div class="card">
            <h4 style="text-align:center; transform:translateX(15px)">Performa Satker</h4>
            <div class="stat-box">Peringkat Nasional<br><b>11 / 555</b></div>
            <div class="stat-box">Total Poin Kejati<br><b>19770</b></div>
            <div class="stat-box">Total Berita Dipublikasikan<br><b>2334</b></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Performa Agen
    with col3:
        st.markdown(
            """
        <div class="card">
            <h4 style="text-align:center; transform:translateX(15px)">Performa Agen</h4>
            <div class="stat-box">Total Personal<br><b>7</b></div>
            <div class="stat-box">Total Personal Aktif<br><b>7</b></div>
            <div class="stat-box">Personel 10 Besar<br><b>1</b></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

elif menu == "SIRATA":
    import re, os, io
    from datetime import datetime
    from docxtpl import DocxTemplate, InlineImage
    from docx.shared import Mm

    # === Database Pegawai Penandatangan ===
    pegawai_options = {
        "Ario Wibowo, S.H., M.H.": {
            "jabatan": "Kepala Seksi Intelijen pada Kejaksaan Negeri Banyumas",
            "pangkat": "Jaksa Muda",
            "nip": "19820928 200312 1 006",
        },
        "Angkat Poenta Pratama, S.H., M. H.": {
            "jabatan": "Kepala Subseksi II Intelijen pada Kejaksaan Negeri Banyumas",
            "pangkat": "Ajun Jaksa",
            "nip": "20020420 202404 2 001",
        },
        "Angelina Fiska Laurensia Ardana": {
            "jabatan": "Staf Intelijen",
            "pangkat": "Yuana Darma TU ",
            "nip": "20020420 202404 2 001",
        },
    }

    # ---- Session state ----
    st.session_state.setdefault("sirata_ready", False)
    st.session_state.setdefault("buat_lapinsus", False)
    st.session_state.setdefault("sirata_payload", {})

    # === HEADER UI ===
    st.markdown(
        """
        <div style="
            background:#ffffff;border-radius:18px;padding:26px 30px;
            box-shadow:0 8px 22px rgba(0,0,0,0.07);border:1px solid #e5e7eb;
            margin-top:10px;margin-bottom:24px;animation: fadeInUp 0.6s ease-in-out;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <div style="background:linear-gradient(135deg,#00796b,#004d26);color:#fff;
                    padding:10px;border-radius:10px;font-size:18px;box-shadow:0 2px 5px rgba(0,0,0,0.2);">🛰️</div>
                <h4 style="margin:0;color:#004d40;font-size:20px;font-weight:800;">
                    SIRATA (System of Intelligence Report Tracking and Analysis)
                </h4>
            </div>
            <p style="color:#374151;font-size:15px;line-height:1.7;">
                Tempel <b>laporan lengkap</b> di bawah ini. Sistem akan otomatis membaca bagian
                <b>Informasi, Trend, dan Saran</b> untuk membuat <b>Lapinhar</b>.<br>
                Setelah itu, kamu bisa lanjutkan menjadi <b>Lapinsus</b>.
            </p>
            <hr style="border:none; border-top:1px solid #e5e7eb; margin:18px 0;">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # === FORM INPUT LAPINHAR ===
    with st.form("form_sirata"):
        no_surat = st.number_input("Nomor Surat Lapinhar", min_value=1, value=1)
        kategori = st.selectbox(
            "Pilih Kategori",
            [
                "Dsb.1",
                "Dsb.2",
                "Dsb.3",
                "Dsb.4",
                "Dip.1",
                "Dip.2",
                "Dip.3",
                "Dip.4",
                "Dek.1",
                "Dek.2",
                "Dek.3",
                "Dek.4",
                "Dpp.1",
                "Dpp.2",
                "Dpp.3",
                "Dpp.4",
                "Dti.1",
                "Dti.2",
                "Dti.3",
                "Dti.4",
                "Kph.1",
                "Kph.2",
                "Kph.3",
                "Kph.4",
            ],
        )
        penandatangan = st.selectbox(
            "Pilih Penandatangan", list(pegawai_options.keys())
        )
        # 🔹 Tambahan input manual perihal
        perihal_manual = st.text_input(
            "Masukkan Perihal",
            placeholder="Contoh: Monitoring kegiatan sosialisasi ketahanan pangan di wilayah Banyumas",
        )
        foto = st.file_uploader(
            "Upload Foto Dokumentasi (opsional)", type=["jpg", "jpeg", "png"]
        )
        laporan_text = st.text_area(
            "📝 Tempel laporan lengkap di sini:",
            height=420,
            placeholder="Tempel teks laporan lengkap (format seperti laporan lapangan)...",
        )
        submit = st.form_submit_button("🛠️ Konversi ke Template Lapinhar")

    if submit:
        if not laporan_text.strip():
            st.warning("⚠️ Harap tempel laporan terlebih dahulu.")
        else:
            try:
                text = laporan_text

                def extract(pattern, txt):
                    m = re.search(pattern, txt, re.S | re.I | re.M)
                    return m.group(1).strip() if m else ""

                # Ekstraksi perihal otomatis (fallback)
                perihal_text = extract(r"Perihal\s*:\s*(.+)", text)

                informasi_raw = extract(
                    r"I\.\s*INFORMASI YANG DIPEROLEH(.*?)II\.", text
                )
                trend_raw = extract(r"III\.\s*TREND.*?(.*?)IV\.", text)
                m = re.search(
                    r"IV\.\s*(?:SARAN(?:\s*/\s*TINDAKAN)?|TINDAKAN)\s*[:\-–—]?\s*(.*?)\n[A-Z]\.",
                    text,
                    re.S | re.I,
                )
                saran_raw = m.group(1).strip() if m else ""

                informasi_parts = re.findall(
                    r"\d+\.\s*(.+?)(?=\n\d+\.|\Z)", informasi_raw or "", re.S
                )
                informasi_parts = [i.strip() for i in informasi_parts if i.strip()]

                trend_clean = re.sub(
                    r"(?i)PERKEMBANGAN\s*/?\s*PERKIRAAN", "", trend_raw or ""
                ).strip()

                saran_parts = re.findall(
                    r"\d+\.\s*(.+?)(?=\n\d+\.|\Z)", saran_raw or "", re.S
                )
                saran_parts = [s.strip() for s in saran_parts if s.strip()]
                if not saran_parts:
                    saran_parts = [
                        "Agar jajaran Intelijen Kejaksaan Negeri Banyumas memonitor situasi dan berkoordinasi dengan pihak terkait untuk mengantisipasi AGHT."
                    ]

                # Nomor & tanggal
                bulan_tahun = datetime.now().strftime("%m/%Y")
                tanggal_str = datetime.now().strftime("%d %B %Y")
                nomor_full = (
                    f"R – LIH – {int(no_surat)}/M.3.39/{kategori}/{bulan_tahun}"
                )

                # Tentukan perihal final (manual > otomatis > default)
                perihal_final = (
                    perihal_manual.strip() or perihal_text or "(Perihal tidak diisi)"
                )

                # Render dokumen Lapinhar
                doc = DocxTemplate("lapinhar_template.docx")
                foto_bytes = foto.read() if foto else None
                foto_inline = (
                    InlineImage(doc, io.BytesIO(foto_bytes), width=Mm(170))
                    if foto_bytes
                    else ""
                )

                data_ttd = pegawai_options[penandatangan]
                context = {
                    "nomor_surat": nomor_full,
                    "perihal": perihal_final,  # 🔹 masukkan ke template
                    "nama_penandatangan": penandatangan,
                    "jabatan_penandatangan": data_ttd["jabatan"],
                    "pangkat_penandatangan": data_ttd["pangkat"],
                    "nip_penandatangan": data_ttd["nip"],
                    "informasi_list": informasi_parts,
                    "trend": trend_clean,
                    "saran_list": saran_parts,
                    "tanggal": tanggal_str,
                    "foto": foto_inline,
                }

                import re

                # 🔹 Ambil nomor surat Lapinhar (input angka dari pengguna)
                nomor_singkat = str(no_surat)

                # 🔹 Ambil dan bersihkan perihal
                perihal_safe = perihal_final.strip()
                # Hapus teks setelah "I. INFORMASI" jika tidak sengaja ikut terbawa
                perihal_safe = re.split(r"\bI\.\s*INFORMASI", perihal_safe, flags=re.I)[
                    0
                ].strip()
                # Bersihkan karakter ilegal dan newline
                perihal_safe = re.sub(r"\s+", " ", perihal_safe)
                perihal_safe = re.sub(r'[\\/*?:"<>|\n\r]+', "", perihal_safe)
                # Batasi panjang untuk keamanan nama file
                perihal_safe = perihal_safe[:100]

                # 🔹 Bentuk nama file Lapinhar dengan format baru
                output_name = f"Lapinhar {nomor_singkat} Perihal {perihal_safe}.docx"

                # 🔹 Simpan hasil render
                doc.render(context)
                doc.save(output_name)

                # Simpan untuk Lapinsus
                st.session_state["sirata_payload"] = {
                    "no_surat": int(no_surat),
                    "kategori": kategori,
                    "tanggal": tanggal_str,
                    "nomor_full": nomor_full,
                    "informasi_parts": informasi_parts,
                    "trend_clean": trend_clean,
                    "saran_list": saran_parts,
                    "lapinhar_path": output_name,
                    "foto_bytes": foto_bytes,
                    "perihal_default": perihal_final,  # 🔹 disimpan dari input manual
                    "penandatangan": penandatangan,
                    "jabatan_penandatangan": data_ttd["jabatan"],
                    "pangkat_penandatangan": data_ttd["pangkat"],
                    "nip_penandatangan": data_ttd["nip"],
                }
                st.session_state["sirata_ready"] = True
                st.session_state["buat_lapinsus"] = False

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")

    # === OUTPUT LAPINHAR ===
    if st.session_state.get("sirata_ready"):
        payload = st.session_state["sirata_payload"]
        st.success("✅ Lapinhar berhasil dibuat dengan format rapi!")
        try:
            with open(payload["lapinhar_path"], "rb") as f:
                st.download_button(
                    "📥 Download Lapinhar",
                    f,
                    file_name=os.path.basename(payload["lapinhar_path"]),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        except Exception:
            st.warning("⚠️ File Lapinhar tidak ditemukan. Silakan proses ulang.")

        st.markdown("---")
        if st.button(
            "➡️ Jadikan Laporan Ini Sebagai Lapinsus", use_container_width=True
        ):
            st.session_state["buat_lapinsus"] = True

    # === FORM & GENERATE LAPINSUS ===
    if st.session_state.get("buat_lapinsus"):
        st.info("🚀 Konversi ke Lapinsus. Perihal akan diambil otomatis dari Lapinhar.")
        payload = st.session_state["sirata_payload"]

        with st.form("form_lapinsus"):
            nomor_pengantar = st.text_input("Nomor Surat Pengantar (SIPEDE)")
            nomor_lapinsus = st.text_input("Nomor Surat Lapinsus")
            submit_lapinsus = st.form_submit_button("Konversi Sekarang")

        if submit_lapinsus:
            if not nomor_pengantar.strip() or not nomor_lapinsus.strip():
                st.warning(
                    "⚠️ Nomor surat pengantar dan nomor Lapinsus (LIK) wajib diisi."
                )
            else:
                try:
                    doc_lapinsus = DocxTemplate("lapinsus_template.docx")
                    m = re.search(r"Dsb\.(\d+)", payload["kategori"])
                    dpp_kode = f"Dpp.{m.group(1)}" if m else "Dpp.1"
                    dt = datetime.strptime(payload["tanggal"], "%d %B %Y")
                    bulan_digit = dt.strftime("%m")
                    tahun_full = dt.strftime("%Y")

                    perihal_final = payload.get("perihal_default", "").strip()
                    isi_surat = (
                        f"Laporan Informasi Khusus Nomor : R-LIK-{nomor_lapinsus}/M.3.39/"
                        f"{dpp_kode}/{bulan_digit}/{tahun_full} tanggal {payload['tanggal']}, "
                        f"Perihal {perihal_final}"
                    )

                    foto_inline_lapinsus = (
                        InlineImage(
                            doc_lapinsus,
                            io.BytesIO(payload["foto_bytes"]),
                            width=Mm(170),
                        )
                        if payload.get("foto_bytes")
                        else ""
                    )

                    ctx = {
                        "nomor_pengantar": nomor_pengantar,
                        "nomor_surat": nomor_lapinsus,
                        "tanggal": payload["tanggal"],
                        "kode_kategori_pengantar": dpp_kode,
                        "bulan_pengantar": bulan_digit,
                        "tahun_pengantar": tahun_full,
                        "hal": perihal_final,
                        "isi_surat": isi_surat,
                        "pengantar_item": isi_surat,
                        "informasi_list": payload["informasi_parts"],
                        "trend": payload["trend_clean"],
                        "saran_list": payload["saran_list"],
                        "foto": foto_inline_lapinsus,
                    }

                    import re

                    # 🔹 Ambil hanya angka dari nomor pengantar (misal: "Tar-R-1213/M.3.39/Dpp.1/10/2025" → "1213")
                    nomor_match = re.search(r"(\d+)", nomor_pengantar)
                    nomor_singkat = (
                        nomor_match.group(1) if nomor_match else nomor_pengantar
                    )

                    # 🔹 Bersihkan perihal agar aman untuk dijadikan nama file
                    perihal_safe = payload.get("perihal_default", "").strip()
                    perihal_safe = re.sub(
                        r"\s+", " ", perihal_safe
                    )  # hapus newline dan ubah ke spasi tunggal
                    perihal_safe = re.sub(
                        r'[\\/*?:"<>|\n\r]+', "", perihal_safe
                    )  # hapus karakter ilegal
                    perihal_safe = perihal_safe[
                        :100
                    ]  # batasi panjang (opsional, hindari error Windows)

                    # 🔹 Bentuk nama file akhir
                    output_lapinsus = (
                        f"Lapinsus {nomor_singkat} Perihal {perihal_safe}.docx"
                    )

                    doc_lapinsus.render(ctx)
                    doc_lapinsus.save(output_lapinsus)

                    with open(output_lapinsus, "rb") as f2:
                        st.success("✅ Lapinsus berhasil dibuat!")
                        st.download_button(
                            "📥 Download Lapinsus",
                            f2,
                            file_name=output_lapinsus,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )

                    st.session_state["buat_lapinsus"] = False

                except Exception as e:
                    st.error(f"❌ Gagal membuat Lapinsus: {e}")

elif menu == "Tentang SIRA":
    st.subheader("Tentang Sistem")
    st.write(
        "SIRA adalah sistem bantu penyusunan laporan IDPOLHANKAM modern dan efisien."
    )
