import unittest
from layoutx._parser import parse_pug_to_obj, XMLElement


class TestParser(unittest.TestCase):
  
  def test_simple(self):
    template = \
"""
Button Hello world
"""
    parsed = parse_pug_to_obj(template)
    assert issubclass(parsed.__class__, XMLElement)
    assert parsed.tag == "Button"
    assert parsed.text == "Hello world"


  def test_children(self):
    template = \
"""
Parent
  Child 1
  Child 2
"""
    parsed = parse_pug_to_obj(template)
    assert parsed.tag == "Parent"
    assert parsed.count_children == 2
    assert parsed.children[0].text == '1'
    assert parsed.children[1].text == '2'
  
  def test_attr(self):
    template = \
"""
Parent
  Child(string="attr_a" int=123 obj={'key': 'value'} bool=False)
"""
    parsed = parse_pug_to_obj(template)
    assert parsed.tag == "Parent"
    child = parsed.children[0]
    assert child.tag == "Child"
    assert child.get_attribute("none", None) == None
    assert child.get_attribute("string") == "attr_a"
    assert child.get_attribute("int") == 123
    assert child.get_attribute("obj") == {'key': 'value'}
    assert child.get_attribute("bool") == False
    

if __name__ == '__main__':
  unittest.main()