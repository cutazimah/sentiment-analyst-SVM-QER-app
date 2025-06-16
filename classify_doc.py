import streamlit as st
from io import StringIO
import pandas as pd

import streamlit as st
import time
import re
import emoji
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
from translate import Translator
import nltk
import pandas as pd
import joblib
import numpy as np
from scipy.sparse import hstack
import plotly.express as px
from datetime import datetime

# Download stopwords jika belum
nltk.download('stopwords')

# === Inisialisasi ===
stemmer = StemmerFactory().create_stemmer()
stop_words = set(stopwords.words('indonesian'))
translator = Translator(to_lang="id")  # opsional
label_map = {0: 'Negatif', 1: 'Netral', 2: 'Positif'}
color_map = {
    'Positif': 'green',
    'Negatif': 'red',
    'Netral': 'yellow'
}

# Emoticon mapping
emot_map = {
    ":-)": "senyum", ":)": "senyum", ":-D": "tertawa", ":D": "tertawa", ":'\\)": "menangis bahagia",
    ":-(": "sedih", ":(": "sedih", ":'‑(": "menangis", ":'(": "menangis", ":‑O": "terkejut", ":O": "terkejut",
    ":|": "datar", ":-/": "bingung", ":/": "bingung", ":-*": "cium", ":*": "cium", ";-)": "kedipan mata",
    ";)": "kedipan mata", ">:(": "marah", ":P": "menjulurkan lidah", ":-P": "menjulurkan lidah", ":3": "imut",
    "-_-": "kesal", "o_O": "bingung", "O_o": "bingung", ">.<": "frustrasi", "<3": "cinta", "</3": "patah hati",
}
escaped_keys = list(map(re.escape, emot_map.keys()))
emot_regex = re.compile("|".join(escaped_keys))


# === Fungsi Pembersihan ===
def full_cleaning_pipeline(text, kamus_tidak_baku):
    if not isinstance(text, str) or not text.strip():
        return ""

    # Basic cleaning
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'@[^\s]+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d+', '', text)
    text = emot_regex.sub(lambda m: emot_map[m.group()], text)
    text = emoji.demojize(text).replace(":", "")
    text = text.lower().strip()

    # Translate emoji alias (opsional)
    words = re.split(r'(:[^:]+:)', text)
    translated_words = []
    for word in words:
        if word.startswith(':') and word.endswith(':'):
            try:
                clean = word.strip(':').replace('_', ' ')
                translated = translator.translate(clean)
                translated_words.append(translated)
            except:
                translated_words.append(clean)
        else:
            translated_words.append(word)
    text = ' '.join(translated_words)

    # Normalisasi kata tidak baku
    tokens = text.split()
    normalized_tokens = [kamus_tidak_baku.get(w, w) for w in tokens]

    # Stopword removal + stemming
    filtered_tokens = [t for t in normalized_tokens if t not in stop_words]
    stemmed_tokens = [stemmer.stem(t) for t in filtered_tokens]

    return ' '.join(stemmed_tokens)


# === Load Resource ===
@st.cache_resource
def load_resources():
    kamus_df = pd.read_excel("kamuskatabaku.xlsx")
    kamus_tidak_baku = dict(zip(kamus_df['tidak_baku'], kamus_df['kata_baku']))

    model = joblib.load("model_svm_qer_best.pkl")
    vectorizer = joblib.load("vectorizer_tfidf_best.pkl")

    return kamus_tidak_baku, model, vectorizer


def app():
    uploaded_file = st.file_uploader(
        "Upload CSV atau Excel", type=("csv", "xlsx"))

    if uploaded_file is not None:

        kamus_tidak_baku, model, vectorizer = load_resources()
        file_type = uploaded_file.name.split('.')[-1]

        try:
            if file_type == 'csv':
                data = pd.read_csv(uploaded_file)
            elif file_type == 'xlsx':
                data = pd.read_excel(uploaded_file)
            else:
                st.error("❌ File type not supported")
                return
        except pd.errors.EmptyDataError:
            st.error("❌ File kosong atau tidak mengandung kolom.")
            return

        # Kolom yang dibutuhkan
        required_columns = ["created_at", "full_text", "username"]

        # Cek apakah semua kolom tersedia
        if not all(col in data.columns for col in required_columns):
            st.error(
                "❌ File tidak memiliki kolom: 'created_at', 'full_text', dan 'username'.")
            return
            # Pembersihan & Prediksi
        with st.spinner("Memproses dan memprediksi..."):
            # st.success(str(data.shape[0]) + ' tweets valid dan siap diproses!✅')
            # st.write("📄 **Data yang Ditampilkan:**")
            # st.dataframe(data[required_columns])

            data['cleaned_text'] = data['full_text'].astype(str).apply(
                lambda x: full_cleaning_pipeline(x, kamus_tidak_baku))
            vectors = vectorizer.transform(data['cleaned_text'])
            data['label'] = model.predict(vectors)
            data['label_text'] = data['label'].map(label_map)
            data['created_at'] = pd.to_datetime(
                data['created_at'], errors='coerce')
            data['created_at'] = data['created_at'].dt.strftime('%Y/%m/%d')

            # Info dasar
            jumlah_tweet = len(data)
            tanggal_awal = pd.to_datetime(
                data['created_at']).min().strftime("%Y-%m-%d")
            tanggal_akhir = pd.to_datetime(
                data['created_at']).max().strftime("%Y-%m-%d")
            # Statistik sentimen
            sentiment_counts = data['label_text'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentimen', 'Jumlah']

            def color_label(val):
                warna = {
                    'Positif': 'background-color: lightgreen; color: black',
                    'Negatif': 'background-color: lightcoral; color: white',
                    'Netral': 'background-color: khaki; color: black'
                }
                return warna.get(val, '')
                # color = color_map.get(val, 'black')
                # return f'color: {color}'

            # ----- Layout -----
            col_left, col_right = st.columns([4, 3])

            # Kiri: Info + Tabel
            with col_left:
                st.subheader("📌 Info Dataset")
                st.write(f"🔢 **Jumlah Tweet:** {jumlah_tweet}")
                st.write(
                    f" 🗓️ **Rentang Tanggal:** {tanggal_awal} s.d {tanggal_akhir}")

                st.subheader(" 📱 Total Sentimen")
                st.table(sentiment_counts)
            import plotly.express as px

            # Misalnya series berisi kategori sentimen: 'Positif', 'Negatif', 'Netral'

            # Kanan: Donut chart
            with col_right:
                st.subheader("📊 Distribusi Sentimen")

                fig = px.pie(
                    sentiment_counts,
                    names='Sentimen',
                    values='Jumlah',
                    hole=0.5,
                    # warna biru lebih kuat
                    color='Sentimen',
                    color_discrete_map=color_map
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("📝 Hasil Klasifikasi")
            # st.dataframe(
            #     data[['created_at', 'full_text', 'cleaned_text', 'label_text']])
            tampil_df = data[['created_at', 'full_text',
                              'cleaned_text', 'label_text']]  # Data asli
            styled_df = tampil_df.style.applymap(
                color_label, subset=['label_text'])
            st.dataframe(styled_df, use_container_width=True)

            # Unduh hasil
            st.markdown("### ⬇️ Download Hasil")
            csv = tampil_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv,
                               "hasil_klasifikasi.csv", "text/csv")

            # # Visualisasi hasil
            # st.markdown("### 📊 Ringkasan Sentimen")
            # sentiment_counts = data['label'].value_counts().rename(index=label_map)
            # st.bar_chart(sentiment_counts)

            # st.markdown("### 📑 Dataframe Hasil")
            # data['label_text'] = data['label'].map(label_map)
            # st.dataframe(data[['full_text', 'cleaned_text', 'label_text']])

            # # Download hasil
            # csv = data.to_csv(index=False).encode("utf-8")
            # st.download_button("📥 Download hasil sebagai CSV",
            #                 csv, "hasil_sentimen.csv", "text/csv")


if __name__ == "__main__":
    app()
