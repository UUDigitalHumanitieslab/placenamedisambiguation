import os
import pytest
from bs4 import BeautifulSoup
from parser import collect_text, parse_route, extract_text


def test_parse_route_attribute():
    route = 'root#child#contentnode[content]'
    actual = parse_route(route)
    assert actual == {'attr': 'content',
                      'query': 'root child contentnode[content]'}


def test_parse_route_no_attribute():
    route = 'root#child#contentnode'
    actual = parse_route(route)
    assert actual == {'attr': None, 'query': 'root child contentnode'}


def test_parse_route_single_tag():
    route = 'contentnode'
    actual = parse_route(route)
    assert actual == {'attr': None, 'query': 'contentnode'}


def test_parse_route_wildcard():
    route = 'child#*#contentnode'
    actual = parse_route(route)
    assert actual == {'attr': None, 'query': 'child * contentnode'}


def test_collect_text_single_full_route_no_attribute():
    soup = BeautifulSoup(
        '<root><child><contentnode>TEXT</contentnode></child></root>', features="html.parser")
    actual = collect_text(soup, 'root#child#contentnode')
    assert actual == "TEXT"


def test_collect_text_single_no_full_route_no_attribute():
    soup = BeautifulSoup(
        '<root><child><contentnode>TEXT</contentnode></child></root>', features="html.parser")
    actual = collect_text(soup, 'contentnode')
    assert actual == "TEXT"


def test_collect_text_single_full_route_attribute():
    soup = BeautifulSoup(
        '<root><child><contentnode content="TEXT"></contentnode></child></root>', features="html.parser")
    actual = collect_text(soup, 'root#child#contentnode[content]')
    assert actual == "TEXT"


def test_collect_text_single_no_full_route_attribute():
    soup = BeautifulSoup(
        '<root><child><contentnode content="TEXT"></contentnode></child></root>', features="html.parser")
    actual = collect_text(soup, 'contentnode[content]')
    assert actual == "TEXT"


def test_collect_text_multiple_text_nodes():
    soup = BeautifulSoup(
        """<root>
            <child>
                <contentnode>TEXT</contentnode>
                <contentnode>TEXT2</contentnode>
            </child>
        </root>""", features="html.parser")
    actual = collect_text(soup, 'contentnode')
    assert actual == "TEXT TEXT2"


def test_collect_text_multiple_text_attributes():
    soup = BeautifulSoup(
        """<root>
            <child>
                <contentnode content="TEXT"></contentnode>
                <contentnode content="TEXT2"></contentnode>
            </child>
        </root>""", features="html.parser")
    actual = collect_text(soup, 'contentnode[content]')
    assert actual == "TEXT TEXT2"


def test_collect_text_complex_structure():
    soup = BeautifulSoup("""<root>
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
                        </root>""", features="html.parser")
    actual = collect_text(soup, 'content')
    assert actual == "Text Text2"


def test_collect_text_complex_structure_wildcard():
    soup = BeautifulSoup("""<root>
                            <parent>    
                                <child>
                                    <contentnode content="TEXT"></contentnode>
                                </child>
                                <anotherchild>                                
                                    <contentnode content="TEXT2"></contentnode>
                                </anotherchild>
                            </parent>
                        </root>""", features="html.parser")
    actual = collect_text(soup, 'parent#*#contentnode[content]')
    assert actual == "TEXT TEXT2"


def test_collect_text_nonexisting_in_route():
    soup = BeautifulSoup(
        '<root><child><contentnode>TEXT</contentnode></child></root>', features="html.parser")
    actual = collect_text(soup, 'nonexisting')
    assert actual == ""


def test_collect_text_nonsense_in_route():
    soup = BeautifulSoup(
        '<root><child><contentnode>TEXT</contentnode></child></root>', features="html.parser")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        collect_text(soup, '@#!')

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_text_europeana_one_textline():
    actual = extract_text(os.path.join(basepath(), "test_files/europeana_one_textline.xml"),
                          'string[content]')
    assert actual == "Indien men Italië in zijn geheel kon neutraliseren ,"


def test_extract_text_europeana_one_textbox():
    print(os.path.join(basepath(), "test_files/europeana_one_textbox.txt"))

    with open(os.path.join(basepath(), "test_files/europeana_one_textbox.txt"), "r") as txt:
        expected = txt.read()
    actual = extract_text(os.path.join(basepath(), "test_files/europeana_one_textbox.xml"),
                          'string[content]')
    assert actual == expected
   

def test_extract_text_icabish():
    actual = extract_text(os.path.join(
        basepath(), "test_files/icab-ish.xml"), 'TEXT')
    assert actual == "Some text to test"


def basepath():
    return os.path.dirname(os.path.realpath(__file__))
