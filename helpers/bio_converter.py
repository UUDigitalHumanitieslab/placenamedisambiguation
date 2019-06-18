

def convert_to_bio(text, entities):
    text_index = 1
    current_entity_index = 0

    bio_tagged = []

    for word in text.split():
        if current_entity_index < len(entities) and is_part_of_entity(text_index, entities[current_entity_index]):
            tag_entity(bio_tagged, entities[current_entity_index], word)

            if (ends_entity(word, entities[current_entity_index])):
                current_entity_index = current_entity_index + 1
        else:
            tag_non_entities(bio_tagged, word)

        text_index = text_index + len(word) + 1

    # prev_entity_end = 0

    # for entity in entities:
    #     index = entity['pos']
    #     entity_to_end = len(text) - index + 1

    #     text_in_between_entities = text[prev_entity_end:-entity_to_end]
    #     prev_entity_end = index + len(entity['ne'])

    #     tag_non_entities(bio_tagged, text_in_between_entities)
    #     tag_entity(bio_tagged, entity)

    # text_after_last_entity = text[prev_entity_end:]

    # print(len(bio_tagged))

    # tag_non_entities(bio_tagged, text_after_last_entity)

    return bio_tagged


def is_part_of_entity(text_index, entity):
    return entity['pos'] <= text_index and text_index <= entity['pos'] + len(entity['ne'])

def ends_entity(word, entity):
    return entity['ne'].endswith(word)


def tag_non_entities(bio_tagged, text):
    for word in text.split(' '):
        bio_tagged.append("{} O".format(word))


def tag_entity(bio_tagged, entity, word):
    tag = translate_to_bio(entity['type'])
    bio_tagged.append("{} {}".format(word, tag))


def translate_to_bio(entity_type):
    if (entity_type == 'LOCATION'):
        return 'LOC'
    if (entity_type == 'PERSON'):
        return 'PER'
    if (entity_type == 'ORGANIZATION'):
        return 'ORG'
    return 'OTHER'
