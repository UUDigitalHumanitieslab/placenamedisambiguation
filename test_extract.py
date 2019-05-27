from extract import convert_to_bio


def test_convert_to_bio():
    text = "Simple line with one Entity"

    entities = [{
        "ner_src": ["spotlight", "stanford", "polyglot", "spacy"],
        "type_certainty": 4,
        "left_context": "with one",
        "type": "LOCATION",
        "pos": 22,
        "ne": "Entity",
        "right_context": "",
        "alt_nes": []
    }]

    bio = convert_to_bio(text, entities)
    expected = ['Simple O', 'line O', 'with O', 'one O', 'Entity B-LOC']
    assert bio == expected
