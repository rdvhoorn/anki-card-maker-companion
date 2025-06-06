import streamlit as st
from dotenv import load_dotenv
import os
import re
import random
from PIL import Image

from helpers.image_searcher import ImageSearcher
from helpers.context_creator import ContextCreator

# Load environment variables
load_dotenv()

# --- Directory setup ---
UPLOAD_IMG_DIR = "uploaded_images"
UPLOAD_AUDIO_DIR = "uploaded_audio"
os.makedirs(UPLOAD_IMG_DIR, exist_ok=True)
os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)

# --- Initialize session state ---
if 'image_searcher' not in st.session_state:
    st.session_state.image_searcher = ImageSearcher()

if 'context_creator' not in st.session_state:
    st.session_state.context_creator = ContextCreator()

if 'cards' not in st.session_state:
    st.session_state.cards = []

if 'selected_word' not in st.session_state:
    st.session_state.selected_word = None

if 'image_results' not in st.session_state:
    st.session_state.image_results = []

if 'pending_blank_card' not in st.session_state:
    st.session_state.pending_blank_card = None

if 'pending_definition_card' not in st.session_state:
    st.session_state.pending_definition_card = None

if 'definition_card_ready' not in st.session_state:
    st.session_state.definition_card_ready = False

if 'selected_image_url' not in st.session_state:
    st.session_state.selected_image_url = None

# --- Title ---
st.title("🧩 Spanish Card Builder")

# --- Step 1: Sentence input ---
sentence = st.text_input("Enter a Spanish sentence", "")
words = sentence.strip().split() if sentence else []

# --- Step 2: Word buttons ---
if words:
    st.markdown("### ✏️ Choose a word")
    cols = st.columns(len(words))
    for i, (col, word) in enumerate(zip(cols, words)):
        with col:
            if st.button(word, key=f"word_{i}"):
                st.session_state.selected_word = i

# --- Step 3: Card type selection ---
if st.session_state.selected_word is not None:
    selected_index = st.session_state.selected_word
    selected_word = words[selected_index]

    st.markdown(f"### 📍 Options for: **{selected_word}**")
    col1, col2 = st.columns(2)

    # -- Fill in the blank option
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

    # -- Definition option
    with col2:
        if st.button("📘 Definition"):
            base_form = st.session_state.context_creator.get_word_base_form(selected_word)
            urls, _ = st.session_state.image_searcher.search_images(base_form)

            st.session_state.image_results = urls
            st.session_state.pending_definition_card = {
                'type': 'definition',
                'word': base_form,
                'original_word': selected_word,
                'sentence': sentence,
                'article': None,
                'ipa': None,
                'audio_url': None,
                'image_url': None
            }
            st.session_state.selected_image_url = None
            st.session_state.definition_card_ready = False

# --- Step 4: Shared image selection block ---
def handle_image_selection():
    st.markdown("### 🖼️ Select an image")
    cols = st.columns(len(st.session_state.image_results))
    for i, (col, url) in enumerate(zip(cols, st.session_state.image_results)):
        with col:
            st.image(url, use_container_width=True)
            if st.button("Select", key=f"select_image_{i}"):
                st.session_state.selected_image_url = url

    uploaded_file = st.file_uploader("Or upload your own image", type=["png", "jpg", "jpeg"], key="upload_img")
    if uploaded_file:
        img_path = os.path.join(UPLOAD_IMG_DIR, f"custom_{uploaded_file.name}")
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.selected_image_url = img_path

    if st.session_state.selected_image_url:
        st.markdown("**✅ Selected Image:**")
        st.image(st.session_state.selected_image_url, width=150)

# --- Fill-in-the-blank flow ---
if st.session_state.pending_blank_card and st.session_state.image_results:
    handle_image_selection()

    if st.session_state.selected_image_url:
        st.session_state.pending_blank_card['image_url'] = st.session_state.selected_image_url

    # Preview before adding
    st.markdown("### 🧾 Card Preview")
    st.text_input("Front", value=st.session_state.pending_blank_card['front'], key="preview_front")
    st.text_input("Back", value=st.session_state.pending_blank_card['back'], key="preview_back")
    st.text_input("Clue", value=st.session_state.pending_blank_card['clue'], key="preview_clue")

    if st.button("➕ Add Card"):
        st.session_state.cards.append(st.session_state.pending_blank_card)
        st.session_state.pending_blank_card = None
        st.session_state.image_results = []
        st.session_state.selected_word = None
        st.session_state.selected_image_url = None
        st.success("Card added!")
        st.rerun()

# --- Definition flow ---
if st.session_state.pending_definition_card and st.session_state.image_results:
    base_word = st.session_state.pending_definition_card["word"]
    handle_image_selection()

    if st.session_state.selected_image_url:
        st.session_state.pending_definition_card["image_url"] = st.session_state.selected_image_url

    # Forvo helper
    st.markdown("### 🔊 Pronunciation")
    choice_base_form = random.choice(base_word.split("/")).strip() if "/" in base_word else base_word
    forvo_url = f"https://forvo.com/word/{choice_base_form}/#es"
    st.markdown(f"[🔗 Open Forvo page for **{choice_base_form}**]({forvo_url})")

    audio_file = st.file_uploader("Upload audio file from Forvo", type=["mp3", "ogg"], key="upload_audio")
    if audio_file:
        # Normalize base_word for filename use
        base_word_clean = st.session_state.pending_definition_card["word"]
        safe_base_word = re.sub(r"[^a-zA-Z0-9áéíóúñüÁÉÍÓÚÑÜ]", "_", base_word_clean)
        audio_path = os.path.join(UPLOAD_AUDIO_DIR, f"{safe_base_word}_{audio_file.name}")
        with open(audio_path, "wb") as f:
            f.write(audio_file.getbuffer())
        st.session_state.pending_definition_card["audio_url"] = audio_path
        st.success(f"Audio added: {audio_file.name}")

    # Context preview + edit inside card preview
    article, ipa = st.session_state.context_creator.get_context(base_word)
    if st.session_state.pending_definition_card:
        st.session_state.pending_definition_card["article"] = article
        st.session_state.pending_definition_card["ipa"] = ipa

    st.markdown("### 🧾 Card Preview")
    st.text_input("Word", value=base_word, key="preview_word")
    article = st.text_input("Article (edit)", value=article, key="preview_article_edit")
    ipa = st.text_input("IPA (edit)", value=ipa, key="preview_ipa_edit")
    st.session_state.pending_definition_card["article"] = article
    st.session_state.pending_definition_card["ipa"] = ipa

    if st.session_state.pending_definition_card.get("image_url"):
        st.image(st.session_state.pending_definition_card["image_url"], width=150)
    if st.session_state.pending_definition_card.get("audio_url"):
        st.markdown(f"**Audio file:** `{os.path.basename(st.session_state.pending_definition_card['audio_url'])[:20]}...`")

    if st.button("➕ Add Card"):
        # Allow incomplete definition cards (e.g., missing audio or image)
        if 'audio_url' not in st.session_state.pending_definition_card:
            st.session_state.pending_definition_card['audio_url'] = None
        if 'image_url' not in st.session_state.pending_definition_card:
            st.session_state.pending_definition_card['image_url'] = None

        st.session_state.cards.append(st.session_state.pending_definition_card)
        st.session_state.pending_definition_card = None
        st.session_state.image_results = []
        st.session_state.selected_word = None
        st.session_state.selected_image_url = None
        st.success("Card added!")
        st.rerun()

# --- Sidebar: Cards in session ---
with st.sidebar:
    st.markdown("### 🧾 Cards in session")
    if st.session_state.cards:
        for idx, card in enumerate(st.session_state.cards):
            col1, col2 = st.columns([5, 1])
            with col1:
                if card['type'] == 'blank':
                    st.markdown(f"**{idx+1}.** {card['front']} → **{card['back']}**")
                elif card['type'] == 'definition':
                    if card.get("original_word") and card["original_word"] != card["word"]:
                        st.markdown(f"**{idx+1}.** 📘 {card['original_word']} → {card['word']}")
                    else:
                        st.markdown(f"**{idx+1}.** 📘 {card['word']}")
                    if card.get('article') or card.get('ipa'):
                        st.caption(f"{card.get('article', '')} / {card.get('ipa', '')}")
            with col2:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.cards.pop(idx)
                    st.rerun()
    else:
        st.info("No cards added yet.")
