

def convert_to_bio(text, entities):
    bio_tagged = []

    prev_entity_end = 0

    for entity in entities:
        index = entity['pos']
        entity_to_end = len(text) - index + 1
        
        text_in_between_entities = text[prev_entity_end:-entity_to_end]        
        prev_entity_end = index + len(entity['ne'])

        tag_non_entities(bio_tagged, text_in_between_entities)
        tag_entity(bio_tagged, entity)    
    
    text_after_last_entity = text[prev_entity_end:]
    tag_non_entities(bio_tagged, text_after_last_entity)

    return bio_tagged

def tag_non_entities(bio_tagged, text):
    for word in text.split():
        bio_tagged.append("{} O".format(word))

def tag_entity(bio_tagged, entity):
    tag = translate_to_bio(entity['type'])
    entity_text = entity['ne'].split()

    if len(entity_text) > 1:
        for i in range(len(entity_text)):            
            if i == 0:
                bio_tagged.append("{} B-{}".format(entity_text[i], tag))
            else:
                bio_tagged.append("{} I-{}".format(entity_text[i], tag))
    else:
        bio_tagged.append("{} B-{}".format(entity['ne'], tag))


def translate_to_bio(entity_type):
    if (entity_type == 'LOCATION'):
        return 'LOC'
    if (entity_type == 'PERSON'):
        return 'PER'
    if (entity_type == 'ORGANIZATION'):
        return 'ORG'
    return 'OTHER'
