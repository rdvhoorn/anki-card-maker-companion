import genanki
import random
import os

def get_models():
    fill_in_blank_model = genanki.Model(
        1749236500001,
        'Fill-in-the-Blank',
        fields=[
            {'name': 'Sentence'},
            {'name': 'Clue'},
            {'name': 'Image'},
            {'name': 'Filler'}
        ],
        templates=[{
            'name': 'Fill in the blank',
            'qfmt': """<div>Fill in the blank</div><br>
<div>{{Sentence}} ({{Clue}})</div><br>
<div>{{Image}}</div><br>""",
            'afmt': """<div>{{Filler}}</div><br>""",
        }],
        css="""
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}
"""
    )

    vocab_model = genanki.Model(
        1749236500002,
        'Vocab',
        fields=[
            {'name': 'Word'},
            {'name': 'Article (for nouns)'},
            {'name': 'IPA spelling'},
            {'name': 'Image'},
            {'name': 'Pronunciation audio'},
            {'name': 'Additional hint'},
            {'name': 'Additional info'}
        ],
        templates=[
            {
                'name': 'Meaning',
                'qfmt': """<div>What does this mean?</div><br>
<div>{{Word}}</div><br>
<div>{{Additional hint}}</div><br>""",
                'afmt': """<div>{{Article (for nouns)}} {{Word}}</div><br>
<div>{{IPA spelling}}</div><br>
<div>{{Image}}</div><br>
<div>{{Pronunciation audio}}</div><br>
<div>{{Additional info}}</div><br>""",
            },
            {
                'name': 'Word recall',
                'qfmt': """<div>What's the word for this picture?</div><br>
<div>{{Image}}</div><br>
<div>{{Additional hint}}</div><br>""",
                'afmt': """<div>{{Article (for nouns)}} {{Word}}</div><br>
<div>{{IPA spelling}}</div><br>
<div>{{Pronunciation audio}}</div><br>
<div>{{Additional info}}</div><br>""",
            },
            {
                'name': 'Spelling',
                'qfmt': """<div>How do you spell this word?</div><br>
<div>{{Image}}</div><br>
<div>{{IPA spelling}}</div><br>
<div>{{Pronunciation audio}}</div><br>""",
                'afmt': """<div>{{Article (for nouns)}} {{Word}}</div><br>""",
            },
        ],
        css="""
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}
"""
    )

    return fill_in_blank_model, vocab_model

def export_cards_to_apkg(cards, output_filename='exported_deck.apkg'):
    fill_in_blank_model, vocab_model = get_models()
    deck = genanki.Deck(
        deck_id=random.randrange(1 << 30, 1 << 31),
        name='Exported Spanish Deck'
    )
    media_files = []

    for card in cards:
        if card['type'] == 'blank':
            img_html = f"<img src='{card['image_url']}'>" if card.get('image_url') else ''

            note = genanki.Note(
                model=fill_in_blank_model,
                fields=[
                    card['sentence'],
                    card.get('clue', ''),
                    img_html,
                    card['back']
                ]
            )
            deck.add_note(note)

            if card.get('image_url') and not card['image_url'].startswith("http"):
                media_files.append(card['image_url'])

        elif card['type'] == 'definition':
            img_html = f"<img src='{card['image_url']}'>" if card.get('image_url') else ''
            audio_markup = f"[sound:{os.path.basename(card['audio_url'])}]" if card.get('audio_url') else ''

            note = genanki.Note(
                model=vocab_model,
                fields=[
                    card['word'],
                    card.get('article', ''),
                    card.get('ipa', ''),
                    img_html,
                    audio_markup,
                    card.get('additional_hint', ''),
                    card.get('additional_info', '')
                ]
            )
            deck.add_note(note)

            if card.get('image_url') and not card['image_url'].startswith("http"):
                media_files.append(card['image_url'])
            if card.get('audio_url'):
                media_files.append(card['audio_url'])

    genanki.Package(deck, media_files=media_files).write_to_file(output_filename)
