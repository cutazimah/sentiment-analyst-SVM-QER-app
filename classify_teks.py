
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

# Download stopwords jika belum
nltk.download('stopwords')

# === Inisialisasi ===
stemmer = StemmerFactory().create_stemmer()
stop_words = set(stopwords.words('indonesian'))
translator = Translator(to_lang="id")  # opsional
label_map = {0: 'Negatif', 1: 'Netral', 2: 'Positif'}

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

# === Streamlit App ===


def app():
    st.header("Klasifikasi Sentimen Ulasan Pelanggan")
    kamus_tidak_baku, model, vectorizer = load_resources()
    input_text = st.text_area("Masukkan teks:", height=70)
    predict_btt = st.button("Prediksi Sentimen")

    if predict_btt:
        if not input_text.strip():
            st.warning("⚠️ Silakan masukkan teks terlebih dahulu.")
            return

        # Pembersihan
        cleaned = full_cleaning_pipeline(input_text, kamus_tidak_baku)
        vectorized = vectorizer.transform([cleaned])
        # Prediksi
        start = time.time()
        prediction_class = model.predict(vectorized)[0]
        end = time.time()

        st.write("Kalimat bersih : ", cleaned)

        if prediction_class == 0:
            st.warning('Ulasan pelanggan ini masuk kategori label negatif')
        elif prediction_class == 1:
            st.info('Ulasan pelanggan ini masuk kategori label netral')
        else:
            st.success('Ulasan pelanggan ini masuk kategori label positif')

        # # Output
        # st.markdown(
        #     f"### 🧾 Prediksi Sentimen: **{label_map[prediction_class]}**")

        # st.markdown(f"⏱️ Waktu prediksi: `{round(end - start, 3)} detik`")

        # if prediction_probs is not None:
        #     st.markdown("### 📊 Probabilitas Prediksi")
        #     st.bar_chart({
        #         'Negatif': prediction_probs[0],
        #         'Netral': prediction_probs[1],
        #         'Positif': prediction_probs[2],
        #     })


if __name__ == "__main__":
    app()
