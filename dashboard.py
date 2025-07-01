import streamlit as st
from PIL import Image
import base64


def app():

    col1, col2 = st.columns(2)

    with col1:
        # st.subheader("Tentang Aplikasi ")
        st.subheader("Deskripsi aplikasi")
        st.markdown(
            """
                <style>
                    .justified-text {
                        text-align: justify;
                    }
                </style>
                <div class="justified-text">
                Aplikasi Web Sentimen Analisis ini diperuntukkan dalam melihat sentimen kepuasan pelanggan 
                dalam menggunakan aplikasi jasa. Algoritma yang digunakan dalam sentimen analisis ini ialah Support Vector Machine (SVM) dan seleksi fitur menggunakan Query Expansion Rangking (QER).
                Sistem ini akan mengklasifikasikan sebuah teks maupun dokumen kepada 3 kelas yang tersedia yaitu, negatif, netral dan positif. 
                
                Ada dua fitur yang ditawarkan, yaitu :
                1. Klasifikasi dokumen = Menampilkan  sebuah dashboard informasi dokumen dan hasil klasifikasi 
                2. Klasifikasi teks = Menampilkan hasil klasifikasi teks dan data bersih

                </div>
                """,
            unsafe_allow_html=True)

        with st.expander("**PENJELASAN PENGGUNAAN APLIKASI**"):
            st.markdown(
                """
                <style>
                    .justified-text {
                        text-align: justify;
                    }
                </style>
                <div class="justified-text"> 

                🎯 Cara penggunaan fitur **klasifikasi dokumen** adalah dengan memasukkan dokumen file (CSV/Excel), lalu selanjutnya 
                menunggu file di proses selama 1 - 3 menit, sesuai dengan *ukuran file*. Selanjutnya akan tampil :red-background[dashboard] 
                mulai dari rentang waktu, distribusi kelas sentimen dan tabel  hasil klasifikasi.

                📌 Cara penggunaan fitur **klasifikasi teks** adalah dengan memasukkan inputan cuitan X tentang kepuasan layanan bagian jasa,
                maka sistem akan memproses teks. Hasil dari proses ini adalah :red-background[data bersih] dan :red-background[label sentimen]
                </div>
                """,
                unsafe_allow_html=True)

    with col2:

        with open("emotional.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

            st.markdown(
                f"""
        <style>
        .center-image {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}
        .center-image img {{
            width: 60%;
            height: auto;
            border-radius: 10px;
        }}
        </style>
        <div class="center-image">
            <img src="data:image/png;base64,{img_base64}" alt="Image">
        </div>
        """,
                unsafe_allow_html=True
            )
