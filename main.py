import streamlit as st
from dotenv import load_dotenv
import os
import re
import random
from datetime import datetime
from PIL import Image

from helpers.anki_exporter import export_cards_to_apkg
from helpers.image_searcher import ImageSearcher
from helpers.context_creator import ContextCreator

# Load environment variables
load_dotenv()

# --- Directory setup ---
UPLOAD_IMG_DIR = "uploaded_images"
UPLOAD_AUDIO_DIR = "uploaded_audio"
os.makedirs(UPLOAD_IMG_DIR, exist_ok=True)
os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)

DEFAULT_STATES = {
    'image_searcher': ImageSearcher(),
    'context_creator': ContextCreator(),
    'cards': [],
    'selected_word': None,
    'image_results': [],
    'pending_blank_card': None,
    'pending_definition_card': None,
    'definition_card_ready': False,
    'selected_image_url': None,
}

# --- Helper Functions ---
def reset_card_state():
    for key in ["pending_blank_card", "pending_definition_card", "selected_image_url", "selected_word", "image_results"]:
        if key in st.session_state:
            st.session_state[key] = DEFAULT_STATES[key]

def tokenize_spanish(sentence):
    return re.findall(r"\w+|[¿¡?.,;:!]", sentence, re.UNICODE)

# --- Image Selection ---
def handle_image_selection():
    selected_image_url = st.session_state.get("selected_image_url")
    st.markdown("### 🖼️ Select an image")
    cols = st.columns(len(st.session_state.image_results))
    for i, (col, url) in enumerate(zip(cols, st.session_state.image_results)):
        with col:
            st.image(url, use_container_width=True)
            if st.button("Select", key=f"select_image_{i}"):
                st.session_state.selected_image_url = url
    uploaded = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png"], key="upload_img")
    if uploaded:
        img_path = os.path.join(UPLOAD_IMG_DIR, f"custom_{uploaded.name}")
        with open(img_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.session_state.selected_image_url = img_path
    if st.session_state.selected_image_url:
        st.markdown("**✅ Selected Image:**")
        st.image(st.session_state.selected_image_url, width=150)

# --- Initialize session state ---
def init_state():
    for k, v in DEFAULT_STATES.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- Title ---
st.title("🧩 Spanish Card Builder")

# --- Step 1: Sentence input ---
sentence = st.text_input("Enter a Spanish sentence", "")
words = tokenize_spanish(sentence) if sentence else []

# --- Step 2: Word buttons ---
if words:
    st.markdown("### ✏️ Choose a word")
    cols = st.columns(len(words))
    for i, (col, word) in enumerate(zip(cols, words)):
        with col:
            if st.button(word, key=f"word_{i}"):
                reset_card_state()
                st.session_state.selected_word = i

# --- Step 3: Card type selection ---
if st.session_state.selected_word is not None:
    selected_index = st.session_state.selected_word
    selected_word = words[selected_index]
    st.markdown(f"### 📍 Options for: **{selected_word}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧩 Fill in the blank"):
            front = ' '.join(['_____' if j == selected_index else w for j, w in enumerate(words)])
            back = selected_word
            clue = st.session_state.context_creator.create_clue(back)
            urls, _ = st.session_state.image_searcher.search_images(sentence)
            st.session_state.image_results = urls
            st.session_state.pending_blank_card = {
                'type': 'blank', 
                'sentence': sentence,
                'front': front, 
                'back': back,
                'clue': clue, 
                'blank_index': selected_index,
                'image_url': None
            }
            st.session_state.selected_image_url = None
    with col2:
        if st.button("📘 Definition"):
            base_form = st.session_state.context_creator.get_word_base_form(selected_word, sentence)
            urls, _ = st.session_state.image_searcher.search_images(base_form)
            st.session_state.image_results = urls
            st.session_state.pending_definition_card = {
                'type': 'definition', 'word': base_form, 'original_word': selected_word,
                'sentence': sentence, 'article': None, 'ipa': None,
                'audio_url': None, 'image_url': None
            }
            st.session_state.selected_image_url = None
            st.session_state.definition_card_ready = False

# --- Fill-in-the-blank flow ---
if st.session_state.pending_blank_card is not None:
    handle_image_selection()
    if st.session_state.selected_image_url:
        st.session_state.pending_blank_card['image_url'] = st.session_state.selected_image_url
    st.markdown("### 🧾 Card Preview")
    st.text_input("Front", value=st.session_state.pending_blank_card['front'], key="preview_front")
    st.text_input("Back", value=st.session_state.pending_blank_card['back'], key="preview_back")
    st.text_input("Clue", value=st.session_state.pending_blank_card['clue'], key="preview_clue")
    if st.button("➕ Add Card"):
        st.session_state.cards.append(st.session_state.pending_blank_card)
        reset_card_state()
        st.success("Card added!")
        st.rerun()

# --- Definition flow ---
if st.session_state.pending_definition_card is not None:
    base_word = st.session_state.pending_definition_card['word']
    handle_image_selection()
    if st.session_state.selected_image_url:
        st.session_state.pending_definition_card['image_url'] = st.session_state.selected_image_url
    st.markdown("### 🔊 Pronunciation")
    forvo_word = random.choice(base_word.split("/")).strip() if "/" in base_word else base_word
    forvo_url = f"https://forvo.com/word/{forvo_word}/#es"
    st.markdown(f"[🔗 Open Forvo page for **{forvo_word}**]({forvo_url})")
    audio_file = st.file_uploader("Upload audio file from Forvo", type=["mp3", "ogg"], key="upload_audio")
    if audio_file:
        safe_name = re.sub(r"[^\wáéíóúüÁÉÍÓÚÜñÑ]+", "_", base_word)
        audio_path = os.path.join(UPLOAD_AUDIO_DIR, f"{safe_name}_{audio_file.name}")
        with open(audio_path, "wb") as f:
            f.write(audio_file.getbuffer())
        st.session_state.pending_definition_card['audio_url'] = audio_path
        st.success(f"Audio added: {audio_file.name}")

    st.markdown("### 🧾 Card Preview")

    article, ipa = st.session_state.context_creator.get_context(base_word)
    article = st.text_input("Article", value=article, key="edit_article")
    ipa = st.text_input("IPA Spelling", value=ipa, key="edit_ipa")
    st.session_state.pending_definition_card['article'] = article
    st.session_state.pending_definition_card['ipa'] = ipa
    st.text_input("Word", value=base_word, key="preview_word")
    if st.session_state.pending_definition_card.get('image_url'):
        st.image(st.session_state.pending_definition_card['image_url'], width=150)
    if st.session_state.pending_definition_card.get('audio_url'):
        st.markdown(f"**Audio:** `{os.path.basename(st.session_state.pending_definition_card['audio_url'])}`")
    if st.button("➕ Add Card"):
        st.session_state.cards.append(st.session_state.pending_definition_card)
        reset_card_state()
        st.success("Card added!")
        st.rerun()

# --- Sidebar: Card Overview ---
with st.sidebar:
    st.markdown("### 🧾 Cards in session")
    if st.session_state.cards:
        for idx, card in enumerate(st.session_state.cards):
            col1, col2 = st.columns([5, 1])
            with col1:
                if card['type'] == 'blank':
                    st.markdown(f"**{idx+1}.** {card['front']} → **{card['back']}**")
                else:
                    label = f"**{idx+1}.** 📘 {card.get('original_word', card['word'])}"
                    st.markdown(label)
                    if card.get('article') or card.get('ipa'):
                        st.caption(f"{card.get('article', '')} / {card.get('ipa', '')}")
            with col2:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.cards.pop(idx)
                    st.rerun()
        if st.button("📤 Export cards to Anki deck"):
            filename = f"exported_deck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.apkg"
            export_cards_to_apkg(st.session_state.cards, output_filename=filename)
            st.success(f"✅ Deck exported as `{filename}`")
    else:
        st.info("No cards added yet.")
