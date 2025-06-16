import streamlit as st
from PIL import Image
import base64
import os


def app():

    col1, col2 = st.columns(2)

    with col1:
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
            dalam menggunakan aplikasi jasa. Pembuatan modelnya menggunakan data training yang diambil 
            dari twitter pada salah satu aplikasi ojek online, @GrabID. Algoritma yang digunakan 
            dalam sentimen analisis ini ialah Support Vector Machine (SVM) dan seleksi fitur melalui penekanan
            pembobotan fitur menggunakan Query Expansion Rangking (QER). 
            </div>
            """,
            unsafe_allow_html=True)

    with col2:
        # Gunakan path relatif, agar bisa dibaca di Streamlit Cloud
        image_path_2 = os.path.join(os.path.dirname(__file__), "emotional.png")

        with open(image_path_2, "rb") as img_file:
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
