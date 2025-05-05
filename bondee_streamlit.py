import streamlit as st
import pandas as pd
import openai
import os
client = openai.OpenAI()

# Kullanıcı verisi
users = [
    {"id": 1, "name": "Ali", "segment": "silver", "invest_menu_visits": 5, "has_investment": 0, "age": 45, "job": "beyaz yakalı"},
    {"id": 2, "name": "Zeynep", "segment": "silver", "invest_menu_visits": 3, "has_investment": 1, "age": 38, "job": "beyaz yakalı"},
    {"id": 3, "name": "Mert", "segment": "silver", "invest_menu_visits": 5, "has_investment": 0, "age": 22, "job": "üniversite öğrencisi"},
]
df = pd.DataFrame(users)

# Kural tabanlı öneri
def base_suggestion(row):
    if row["has_investment"] == 1:
        return "Yatırım hesabını başarıyla açtın, yatırım ürünleriyle ilgili bilgi almak istersen bana dilediğin zaman ulaşabilirsin veya İşCep ve isbank.com.tr'den de bilgi alabilirsin."
    elif row["invest_menu_visits"] >= 3:
        return "Yatırım yapmayı sıkça düşündüğünü görüyoruz. Sizin için en uygun yatırım hesabını birlikte oluşturalım."
    else:
        return "Şu an için öneri yok."

# GPT destekli empatik mesaj üretimi
def generate_gpt_message(message):
    if message.startswith("Şu an") or message.startswith("Yatırım hesabını başarıyla"):
        return message

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir banka müşteri danışmanısısın. Kullanıcılara empatik, kişisel ve teşvik edici bir dille yatırım önerileri sunuyorsun."},
            {"role": "user", "content": f"{message} mesajını empatik ve cesaretlendirici hale getir."}
        ]
    )
    return response.choices[0].message.content.strip()

# Yatırıma başlama rehberi
def generate_investment_guide():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen halkın anlayacağı dilden, sade ve güven veren bir ekonomi uzmanısın."},
            {"role": "user", "content": "Yatırıma başlamak isteyen ama hiç tecrübesi olmayan birine sade ve yol gösterici bir yatırım rehberi hazırla."}
        ]
    )
    return response.choices[0].message.content.strip()

# Yatırım yolu açıklamaları
def generate_path_response(path):
    if path == "Yatırım Fonu":
        return ("Yatırım fonlarıyla başlamak küçük adımlarla birikim yapmak için ideal. İşCep'teki Robofon Danışmanı sayesinde 6 adımda risk profiline uygun fon önerisi alabilir,\n"
                "Temkinli, Dengeli veya Atak fonlardan birini seçebilirsin. İşCep üzerinden yatırımına hemen başlayabilirsin.")
    elif path == "Altın":
        return "Altın, ekonomik belirsizliklerde güvenli limandır. Vadesiz altın hesabı veya altın fonlarıyla yatırım yapabilirsin. İşCep'te altın alımı çok kolay."
    elif path == "Hisse Senedi":
        return "Hisse senetleri uzun vadede kazanç sağlayabilir. Şirketleri araştırarak pozisyon alabilir, İşCep üzerinden kademeli yatırımlara başlayabilirsin."
    return "Daha fazla bilgi için İşCep'i ziyaret edebilirsin."

# Streamlit arayüzü
st.title("Bondee.AI - Empatik Öneri ve Öğrenen Rehber Demo")

if "clicked_users" not in st.session_state:
    st.session_state.clicked_users = set()
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "path_choice" not in st.session_state:
    st.session_state.path_choice = {}
if "show" not in st.session_state:
    st.session_state.show = False

if st.button("Önerileri Göster"):
    st.session_state.show = True
    df["öneri"] = df.apply(base_suggestion, axis=1)
    empatik_mesajlar = df["öneri"].apply(generate_gpt_message)
    st.session_state.empatik_mesajlar = empatik_mesajlar.tolist()

if st.session_state.show:
    if "empatik_mesajlar" not in st.session_state:
        st.error("Empatik mesajlar yüklenemedi. Lütfen 'Önerileri Göster' butonuna tekrar basın.")
    else:
        df["empatik_mesaj"] = st.session_state.empatik_mesajlar
        for _, row in df.iterrows():
            st.markdown(f"**Kullanıcı {row['id']} ({row['name']})**: {row['empatik_mesaj']}")

            if row['has_investment'] == 0 and not row['empatik_mesaj'].startswith("Şu an"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"Evet, ilgileniyorum ({row['id']})"):
                        st.session_state.clicked_users.add(row['id'])
                with col2:
                    if st.button(f"Hayır, ilgilenmiyorum ({row['id']})"):
                        st.session_state.feedback[row['id']] = "negative"

            if row['has_investment'] == 1:
                if st.button(f"Yatırım Ürünlerini Gör ({row['id']})"):
                    st.session_state.clicked_users.add(row['id'])

            if row['id'] in st.session_state.clicked_users:
                if row['id'] == 3:
                    st.markdown("### 💰 Bütçe Aralığını Seç")
                    budget = st.radio(
                        "Yatırım yapmayı düşündüğün bütçe aralığını belirt:",
                        ["0 - 1.000 TL", "1.000 - 5.000 TL", "5.000 TL ve üzeri"],
                        key=f"budget_{row['id']}"
                    )
                    st.success(f"Seçilen bütçe: {budget}")

                st.subheader(f"📘 Yatırıma Başlama Rehberi (Kullanıcı {row['id']})")
                st.markdown(generate_investment_guide())

                st.write("Yatırım tercihini seç:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Altın ({row['id']})"):
                        st.session_state.path_choice[row['id']] = "Altın"
                with col2:
                    if st.button(f"Yatırım Fonu ({row['id']})"):
                        st.session_state.path_choice[row['id']] = "Yatırım Fonu"
                with col3:
                    if st.button(f"Hisse Senedi ({row['id']})"):
                        st.session_state.path_choice[row['id']] = "Hisse Senedi"

                if row['id'] in st.session_state.path_choice:
                    st.success(f"Seçiminiz: {st.session_state.path_choice[row['id']]}")
                    st.markdown(generate_path_response(st.session_state.path_choice[row['id']]))

            if row['id'] in st.session_state.feedback and st.session_state.feedback[row['id']] == "negative":
                st.info("Yatırım şu an ilgi alanında olmayabilir ama unutma, fırsatlar her zaman kapıda! Hazır hissettiğinde yanında olacağım. 🌱")


