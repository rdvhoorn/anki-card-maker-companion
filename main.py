import streamlit as st

st.title("🧩 Fill-in-the-Blank Card Builder")

# Step 1: Enter sentence
sentence = st.text_input("Enter a Spanish sentence", "")

if sentence:
    words = sentence.strip().split()
    st.markdown("### 🔍 Select a word to blank out")

    # Show buttons for each word
    cols = st.columns(len(words))
    for i, word in enumerate(words):
        with cols[i]:
            if st.button(word, key=f"word_{i}"):
                # Add selected card to session
                front = ' '.join(['_____' if j == i else w for j, w in enumerate(words)])
                back = word
                new_card = {
                    'sentence': sentence,
                    'front': front,
                    'back': back,
                    'blank_index': i
                }
                if 'blank_cards' not in st.session_state:
                    st.session_state.blank_cards = []
                st.session_state.blank_cards.append(new_card)
                st.success(f"Card created for: '{word}'")

# Show cards in this session
if 'blank_cards' in st.session_state and st.session_state.blank_cards:
    st.markdown("### 🧾 Cards in this session")
    for idx, card in enumerate(st.session_state.blank_cards):
        st.markdown(f"**{idx+1}.** {card['front']} → **{card['back']}**")
