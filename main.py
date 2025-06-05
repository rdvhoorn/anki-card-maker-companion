import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image

from helpers.image_searcher import ImageSearcher
from helpers.context_creator import ContextCreator

# Load environment variables
load_dotenv()

# --- Directory setup for uploads ---
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
            }

    # -- Definition option
    with col2:
        if st.button("📘 Definition"):
            urls, _ = st.session_state.image_searcher.search_images_from_word(selected_word)

            st.session_state.image_results = urls
            st.session_state.pending_definition_card = {
                'type': 'definition',
                'word': selected_word,
                'sentence': sentence,
                'article': None,
                'ipa': None,
                'audio_url': None,
                'image_url': None,
            }

# --- Step 4a: Image selection for fill-in-the-blank card ---
if st.session_state.pending_blank_card and st.session_state.image_results:
    st.markdown("### 🖼️ Select an image for the card")

    cols = st.columns(len(st.session_state.image_results))
    for i, (col, url) in enumerate(zip(cols, st.session_state.image_results)):
        with col:
            st.image(url, use_container_width=True)
            if st.button("Select", key=f"select_image_{i}"):
                card = st.session_state.pending_blank_card.copy()
                card['image_url'] = url
                st.session_state.cards.append(card)

                # Reset
                st.session_state.pending_blank_card = None
                st.session_state.image_results = []
                st.session_state.selected_word = None

                st.success(f"Added card for: '{card['back']}'")
                st.rerun()

    # Optional upload
    uploaded_file = st.file_uploader("Or upload your own image for this card", type=["png", "jpg", "jpeg"], key="upload_blank")
    if uploaded_file:
        image_path = os.path.join(UPLOAD_DIR, f"blank_{uploaded_file.name}")
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        card = st.session_state.pending_blank_card.copy()
        card['image_url'] = image_path
        st.session_state.cards.append(card)

        # Reset
        st.session_state.pending_blank_card = None
        st.session_state.image_results = []
        st.session_state.selected_word = None

        st.success(f"Added card for: '{card['back']}' with uploaded image")
        st.rerun()

# --- Step 4b: Image selection for definition card ---
if st.session_state.pending_definition_card and st.session_state.image_results:
    st.markdown("### 🖼️ Select an image for the definition card")

    cols = st.columns(len(st.session_state.image_results))
    for i, (col, url) in enumerate(zip(cols, st.session_state.image_results)):
        with col:
            st.image(url, use_container_width=True)
            if st.button("Select", key=f"select_def_image_{i}"):
                card = st.session_state.pending_definition_card.copy()
                card['image_url'] = url

                article, ipa = st.session_state.context_creator.get_context(card['word'])
                card['article'] = article
                card['ipa'] = ipa

                st.session_state.cards.append(card)

                # Reset
                st.session_state.pending_definition_card = None
                st.session_state.image_results = []
                st.session_state.selected_word = None

                st.success(f"Added definition card for: '{card['word']}'")
                st.rerun()

    # Optional upload
    uploaded_file = st.file_uploader("Or upload your own image for this card", type=["png", "jpg", "jpeg"], key="upload_def")
    if uploaded_file:
        image_path = os.path.join(UPLOAD_DIR, f"def_{uploaded_file.name}")
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        card = st.session_state.pending_definition_card.copy()
        card['image_url'] = image_path

        article, ipa = st.session_state.context_creator.get_context(card['word'])
        card['article'] = article
        card['ipa'] = ipa

        st.session_state.cards.append(card)

        # Reset
        st.session_state.pending_definition_card = None
        st.session_state.image_results = []
        st.session_state.selected_word = None

        st.success(f"Added definition card for: '{card['word']}' with uploaded image")
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
                    st.markdown(f"**{idx+1}.** 📘 {card['word']}")
                    if card.get('article') or card.get('ipa'):
                        st.caption(f"{card.get('article', '')} / {card.get('ipa', '')}")
            with col2:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.cards.pop(idx)
                    st.rerun()
    else:
        st.info("No cards added yet.")
