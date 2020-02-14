import pypugjs
from pypugjs.parser     import Parser
from pypugjs.nodes      import Tag
from typing import List
from operator import itemgetter
import ast


class XMLElement:
  def __init__(self, tag: str, attrib: dict):
    self._tag = tag
    self._attrib = attrib
    self._children: List = []
    self._text = None

  @property
  def count_children(self):
    return len(self._children)

  @property
  def children(self):
    return self._children

  @property
  def tag(self):
    return self._tag

  @property
  def text(self):
    return self._text
  
  @text.setter
  def text(self, value):
    self._text = value

  def add_child(self, child):
    if not self.has_child(child):
      self._children.append(child)

  def remove_child(self, child):
    if self.has_child(child):
      self._children.remove(child)

  def has_child(self, child):
    return child in self._children

  @property
  def attributes(self):
    return self._attrib

  def get_attribute(self, key, default= None):
    return self._attrib.get(key, default)

  def set_attribute(self, key, value):
    self._attrib[key] = value

  def remove_attribute(self, key):
    if self.has_attrib(key):
      del self._attrib[key]

  def has_attribute(self, key):
    return key in self._attrib


class Compiler(object):
  def __init__(self, node):
    self._node = node
    self._buffer = None

  def compile(self):
    self.visit(self._node, root=self._buffer)
    return self._buffer
  
  def visit(self, node, **kwargs):
    self.visitNode(node, **kwargs)

  def visitNode(self, node, **kwargs):
    name = node.__class__.__name__
    visit_fn = getattr(self, f"visit{name}", None)
    if visit_fn:
      visit_fn(node, **kwargs)
    else:
      raise NotImplementedError(f"Node {name} not supported")

  def visitBlock(self, block, **kwargs):
    for node in block.nodes:
      self.visit(node, **kwargs)

  def visitTag(self, tag, **kwargs):
    attrs = {}
    for attr in tag._attrs:
      name, value = itemgetter("name", "val")(attr)
      attrs[name] = ast.literal_eval(value)
    element = XMLElement(tag.name, attrs)
    
    if kwargs.get("root"):
      kwargs.get("root").add_child(element)
    else:
      self._buffer = element
    
    self.visit(tag.block, root=element)
    if tag.text:
      self.visit(tag.text, root=element)

  def visitText(self, text, **kwargs):
    if kwargs.get("root").text:
      kwargs.get("root").text += '\n' + ''.join(text.nodes).strip()
    else:
      kwargs.get("root").text = ''.join(text.nodes).strip()

  def visitString(self, text, **kwargs):
    self.visitText(text, **kwargs)


def parse_pug_to_obj(template: str):
  try:
    block = Parser(template).parse()
    return Compiler(block).compile()
  except Exception as e:
    raise ValueError(str(e))