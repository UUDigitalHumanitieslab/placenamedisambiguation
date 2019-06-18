import os, json
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
    expected = ['Simple O', 'line O', 'with O', 'one O', 'Entity LOC']
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
    expected = ['Simple O', 'line O', 'with O', 'one O', 'TWO LOC', 'WORDS LOC']
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
        'Simple O', 'line O', 'with O', 'one O', 'Entity LOC', 'in O', 'the O', 'middle O', 
        'and O', 'ANOTHER PER', 'ONE PER', 'much O', 'further O', 'on. O']

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
    expected = ['Simple O', 'ENTITY ORG', 'THREE ORG', 'WORDS ORG', 'and O', 'more O', 'words O']

    assert bio == expected

def test_convert_to_bio_real_example(tmpdir):
    test_files_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_files')
    
    with open(os.path.join(test_files_folder, 'urn=ddd_000010470_mpeg21_p002_alto.alto.xml.txt'), 'r') as fh:
        text = fh.read()

    with open(os.path.join(test_files_folder, 'urn=ddd_000010470_mpeg21_p002_alto.alto.xml.entities.json'), 'r') as fh:
        entities_full = json.load(fh)
        entities = entities_full['entities']

    bio = convert_to_bio(text, entities)
   
    temp_file = tmpdir.join('tempout.bio')
    with open(temp_file, 'w') as fh:
        for line in bio:
            fh.write("%s\n" % line)

    with open(temp_file, 'r') as fh:
        actual = fh.readlines()
    
    with open(os.path.join(test_files_folder, 'urn=ddd_000010470_mpeg21_p002_alto.alto.xml.bio'), 'r') as fh:
        expected = fh.readlines()
    
    assert actual == expected
