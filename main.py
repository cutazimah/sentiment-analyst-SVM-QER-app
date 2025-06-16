import streamlit as st
from streamlit_option_menu import option_menu
import base64

# Import pages
import dashboard as dashboard
import classify_teks as classify_teks
import classify_doc as classify_doc


st.set_page_config(
    page_title="Analisis Sentimen Kepuasan Pelanggan",
    layout="wide",
    page_icon="🧊",
)


# Ubah path ke lokasi gambarmu
image_path = r"C:\Users\Cut Azimah - Iffah\skripsweet\pencil.png"

# Baca gambar dan ubah ke base64 agar bisa disisipkan dalam HTML
with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

# HTML dan CSS untuk menampilkan gambar kecil di samping judul
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <h1 style="margin: 0;">Analisis Sentimen Kepuasan Pelanggan</h1>
        <img src="data:image/png;base64,{img_base64}" width="40"/>
    </div>
    """,
    unsafe_allow_html=True
)


def main():
    # Display the option menu in the main area (not in the sidebar)
    selected = option_menu(
        menu_title=None,  # No menu title
        options=["Dashboard", "Klasifikasi Dokumen",
                 "Klasifikasi teks"],  # Menu options
        icons=None,  # No icons
        default_index=0,  # Default option
        orientation="horizontal"  # Horizontal menu
    )

    # menu_data  = [
    #     {'id': "Judul", 'icon': "fa--", 'label':"same judul"}
    # ]

    # Display the selected page
    if selected == 'Dashboard':
        dashboard.app()
    elif selected == 'Klasifikasi Dokumen':
        classify_doc.app()
    elif selected == 'Klasifikasi teks':
        classify_teks.app()


# Initialize and run the app
if __name__ == "__main__":
    main()
