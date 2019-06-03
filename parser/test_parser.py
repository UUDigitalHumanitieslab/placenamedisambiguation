import os
import pytest
import xml.etree.ElementTree as ET
from parser import collect_text, parse_route, extract_text


def test_parse_route_attribute():
    route = 'root#child#contentnode[content]'
    actual = parse_route(route, True)
    assert actual == {'attr': 'content',
                      'query': './/child/contentnode[@content]'}


def test_parse_route_no_attribute():
    route = 'root#child#contentnode'
    actual = parse_route(route, True)
    assert actual == {'attr': None, 'query': './/child/contentnode'}


def test_parse_route_no_skip():
    route = 'child#anotherchild#contentnode'
    actual = parse_route(route, False)
    assert actual == {'attr': None,
                      'query': './/child/anotherchild/contentnode'}


def test_parse_route_single_tag():
    route = 'contentnode'
    actual = parse_route(route, False)
    assert actual == {'attr': None, 'query': './/contentnode'}


def test_parse_route_wildcard():
    route = 'child#*#contentnode'
    actual = parse_route(route, False)
    assert actual == {'attr': None, 'query': './/child/*/contentnode'}


def test_collect_text_single_full_route_no_attribute():
    xml = ET.fromstring(
        '<root><child><contentnode>TEXT</contentnode></child></root>')
    actual = collect_text(xml, 'root#child#contentnode')
    assert actual == "TEXT"


def test_collect_text_single_no_full_route_no_attribute():
    xml = ET.fromstring(
        '<root><child><contentnode>TEXT</contentnode></child></root>')
    actual = collect_text(xml, 'contentnode')
    assert actual == "TEXT"


def test_collect_text_single_full_route_attribute():
    xml = ET.fromstring(
        '<root><child><contentnode content="TEXT"></contentnode></child></root>')
    actual = collect_text(xml, 'root#child#contentnode[content]')
    assert actual == "TEXT"


def test_collect_text_single_no_full_route_attribute():
    xml = ET.fromstring(
        '<root><child><contentnode content="TEXT"></contentnode></child></root>')
    actual = collect_text(xml, 'contentnode[content]')
    assert actual == "TEXT"


def test_collect_text_multiple_text_nodes():
    xml = ET.fromstring(
        '<root><child><contentnode>TEXT</contentnode><contentnode>TEXT2</contentnode></child></root>')
    actual = collect_text(xml, 'contentnode')
    assert actual == "TEXT TEXT2"


def test_collect_text_multiple_text_attributes():
    xml = ET.fromstring(
        '<root><child><contentnode content="TEXT"></contentnode><contentnode content="TEXT2"></contentnode></child></root>')
    actual = collect_text(xml, 'contentnode[content]')
    assert actual == "TEXT TEXT2"


def test_collect_text_complex_structure():
    xml = ET.fromstring("""<root>
                            <parent>
                                <child>
                                    <grandchild>
                                        <content>Text</content>
                                    </grandchild>
                                </child>
                                <anotherchild>
                                    <grandchild>
                                        <content>Text2</content>
                                    </grandchild>
                                </anotherchild>
                            </parent>
                        </root>""")
    actual = collect_text(xml, 'content')
    assert actual == "Text Text2"


def test_collect_text_complex_structure_wildcard():
    xml = ET.fromstring("""<root>
                            <parent>    
                                <child>
                                    <contentnode content="TEXT"></contentnode>
                                </child>
                                <anotherchild>                                
                                    <contentnode content="TEXT2"></contentnode>
                                </anotherchild>
                            </parent>
                        </root>""")
    actual = collect_text(xml, 'parent#*#contentnode[content]')
    assert actual == "TEXT TEXT2"


def test_collect_text_nonexisting_in_route():
    xml = ET.fromstring(
        '<root><child><contentnode>TEXT</contentnode></child></root>')
    actual = collect_text(xml, 'nonexisting')
    assert actual == ""


def test_collect_text_nonsense_in_route():
    xml = ET.fromstring(
        '<root><child><contentnode>TEXT</contentnode></child></root>')
    
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        collect_text(xml, '@#!')

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


@pytest.mark.xfail(raises=ET.ParseError)
def test_collect_text_html_character():
    '''
    This test exists to prove that ElementTree cannnot handle the presence of HTML characters
    in the XML. This is why `extract_text` unescapes these first.
    '''

    xml = ET.fromstring(
        '<root><child><contentnode content="Itali&euml;"></contentnode></contentnode></child></root>')
    collect_text(xml, 'contentnode[content]')


def test_extract_text_europeana_one_textline():
    actual = extract_text(os.path.join(basepath(), "test_files/europeana_one_textline.xml"),
                          '{http://schema.ccs-gmbh.com/ALTO}string[content]')
    assert actual == "Indien men Italië in zijn geheel kon neutraliseren ,"


def test_extract_text_europeana_one_textbox():
    print(os.path.join(basepath(), "test_files/europeana_one_textbox.txt"))

    with open(os.path.join(basepath(), "test_files/europeana_one_textbox.txt"), "r") as txt:
        expected = txt.read()
    actual = extract_text(os.path.join(basepath(), "test_files/europeana_one_textbox.xml"),
                          '{http://schema.ccs-gmbh.com/ALTO}string[content]')
    assert actual == expected


def test_extract_text_icabish():
    actual = extract_text(os.path.join(
        basepath(), "test_files/icab-ish.xml"), 'TEXT')
    assert actual == "Some text to test"


def basepath():
    return os.path.dirname(os.path.realpath(__file__))
