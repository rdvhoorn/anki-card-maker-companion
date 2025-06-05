import streamlit as st
from dotenv import load_dotenv
from helpers.image_searcher import ImageSearcher
from helpers.clue_creator import ClueCreator

# Load environment variables (e.g., API keys)
load_dotenv()

# --- Initialize session state ---
if 'image_searcher' not in st.session_state:
    st.session_state.image_searcher = ImageSearcher()

if 'clue_creator' not in st.session_state:
    st.session_state.clue_creator = ClueCreator()

if 'blank_cards' not in st.session_state:
    st.session_state.blank_cards = []

if 'image_results' not in st.session_state:
    st.session_state.image_results = []

if 'selected_image_url' not in st.session_state:
    st.session_state.selected_image_url = None

if 'last_searched_sentence' not in st.session_state:
    st.session_state.last_searched_sentence = ""

# --- Title ---
st.title("🧩 Fill-in-the-Blank Card Builder with Images")

# --- Step 1: Sentence input ---
sentence = st.text_input("Enter a Spanish sentence", "")

# --- Step 2: Automatically search images if new sentence ---
if sentence and sentence != st.session_state.last_searched_sentence:
    urls, _ = st.session_state.image_searcher.search_images(sentence)
    st.session_state.image_results = urls
    st.session_state.last_searched_sentence = sentence
    st.session_state.selected_image_url = None  # reset previous selection

# --- Step 3: Show image results side-by-side ---
if st.session_state.image_results:
    st.markdown("### 🖼️ Select an image")
    cols = st.columns(len(st.session_state.image_results))
    for i, (col, url) in enumerate(zip(cols, st.session_state.image_results)):
        with col:
            st.image(url, use_container_width=True)
            if st.button("Select", key=f"select_image_{i}"):
                st.session_state.selected_image_url = url
                st.success(f"Selected image: {url.split('/')[-1]}")

# --- Step 4: Word selection for fill-in-the-blank cards ---
if sentence:
    words = sentence.strip().split()
    st.markdown("### ✏️ Select word(s) to blank out")

    cols = st.columns(len(words))
    for i, word in enumerate(words):
        with cols[i]:
            if st.button(word, key=f"word_{i}"):
                front = ' '.join(['_____' if j == i else w for j, w in enumerate(words)])
                back = word
                clue = st.session_state.clue_creator.create_clue(back)

                card = {
                    'sentence': sentence,
                    'front': front,
                    'back': back,
                    'clue': clue,
                    'blank_index': i,
                    'image_url': st.session_state.selected_image_url
                }

                st.session_state.blank_cards.append(card)
                st.success(f"Added card for: '{back}'")

# --- Sidebar: Show session card overview ---
with st.sidebar:
    st.markdown("### 🧾 Cards in session")
    if st.session_state.blank_cards:
        for idx, card in enumerate(st.session_state.blank_cards):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{idx+1}.** {card['front']} → **{card['back']}**")
            with col2:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.blank_cards.pop(idx)
                    st.rerun()
    else:
        st.info("No cards added yet.")
