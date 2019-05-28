from bio_converter import convert_to_bio

def test_convert_to_bio_one_entity():
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

def test_convert_to_bio_one_entity_two_words():
    text = "Simple line with one TWO WORDS"

    entities = [{
        "ner_src": ["spotlight", "stanford", "polyglot", "spacy"],
        "type_certainty": 4,
        "left_context": "with one",
        "type": "LOCATION",
        "pos": 22,
        "ne": "TWO WORDS",
        "right_context": "",
        "alt_nes": []
    }]

    bio = convert_to_bio(text, entities)
    expected = ['Simple O', 'line O', 'with O', 'one O', 'TWO B-LOC', 'WORDS I-LOC']
    assert bio == expected


def test_convert_to_bio_two_entities():
    text = "Simple line with one Entity in the middle and ANOTHER ONE much further on."

    entities = [{
        "ner_src": ["spotlight", "stanford", "polyglot", "spacy"],
        "type_certainty": 4,
        "left_context": "with one",
        "type": "LOCATION",
        "pos": 22,
        "ne": "Entity",
        "right_context": "in the",
        "alt_nes": []
    },
    {
        "ner_src": ["spotlight", "stanford", "polyglot", "spacy"],
        "type_certainty": 4,
        "left_context": "middle and",
        "type": "PERSON",
        "pos": 47,
        "ne": "ANOTHER ONE",
        "right_context": "much further",
        "alt_nes": []
    }]

    bio = convert_to_bio(text, entities)
    expected = [
        'Simple O', 'line O', 'with O', 'one O', 'Entity B-LOC', 'in O', 'the O', 'middle O', 
        'and O', 'ANOTHER B-PER', 'ONE I-PER', 'much O', 'further O', 'on. O']

    assert bio == expected

def test_convert_to_bio_one_entity_three_words():
    text = "Simple ENTITY THREE WORDS and more words"

    entities = [{
        "ner_src": ["spotlight", "stanford", "polyglot", "spacy"],
        "type_certainty": 4,
        "left_context": "simple",
        "type": "ORGANIZATION",
        "pos": 8,
        "ne": "ENTITY THREE WORDS",
        "right_context": "and more words",
        "alt_nes": []
    }]

    bio = convert_to_bio(text, entities)
    expected = ['Simple O', 'ENTITY B-ORG', 'THREE I-ORG', 'WORDS I-ORG', 'and O', 'more O', 'words O']

    print(bio)
    print(expected)
    assert bio == expected
