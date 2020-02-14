import platform
from typing import List, Callable
from copy import deepcopy, copy
import ast
from functools import reduce


__all__ = [ "get_os", "is_windows", "safe_get", "safe_set", "safer_eval", "safe_list", "safe_dict" ]

class Singleton:
  def __init__(self, decorated):
    self._decorated = decorated

  def instance(self, **kwargs):
    try:
      return self._instance
    except AttributeError:
      self._instance = self._decorated(**kwargs)
      return self._instance

  def __call__(self):
    raise TypeError('Singletons must be accessed through `instance()`.')

def get_os():
  return platform.system()

def is_windows():
  return get_os() == "Windows"

def safe_get(data, keys: List[str]):
  for key in keys:
    try:
      data = data[int(key)] if isinstance(data, list) else data[key]
    except KeyError:
      return None
  return data

def safe_set(data, keys: List[str], value):
  data_copy = deepcopy(data)
  dic = data_copy
  for key in keys[:-1]:
    dic = dic[int(key)] if isinstance(dic, list) else dic.setdefault(key, {})
  dic[int(keys[-1]) if isinstance(dic, list) else keys[-1]] = value
  return data_copy

safe_list = [
  'abs', 'all', 'any', 'ascii', 'bin', 'callable', 
  'chr', 'dir', 'divmod', 'format', 'getattr',
  'hasattr', 'hash', 'hex', 'id', 'input', 'isinstance', 
  'issubclass', 'iter', 'len', 'max', 'min', 'next', 'oct', 
  'ord', 'pow', 'repr', 'round', 'sorted', 'sum', 'bool', 
  'bytearray', 'bytes', 'complex', 'dict', 'enumerate', 
  'filter', 'float', 'frozenset', 'int', 'list', 'map', 'object', 
  'range', 'reversed', 'set', 'slice', 'str', 'tuple', 'type', 'zip', 'partial'
]

safe_dict = dict([ (k, globals()["__builtins__"].get(k)) for k in safe_list ])
from functools import partial
safe_dict["partial"] = partial

def safer_eval(exp: str, variables={}):
  return eval(exp, {"__builtins__":None}, dict(copy(safe_dict), **variables))

def security_check_ast(tree: ast.AST, allowed_internal_names = []):
  for node in ast.walk(tree):
    # Block Assignments, Imports, Deletion, etc.
    if isinstance(node, (
      ast.Assign, ast.Assert, ast.AnnAssign, ast.AugAssign,
      ast.alias, ast.FunctionDef, ast.Import, ast.ImportFrom, ast.Del, ast.Delete, ast.Global, ast.Nonlocal)):
      raise ValueError(f"Illegal Expression Type: { node.__class__.mro()[0].__name__}")
    
    import sys
    # Python 3.8 
    if sys.version_info >= (3, 8) and isinstance(node, ast.NamedExpr):
      raise ValueError(f"Illegal Expression Type: { node.__class__.mro()[0].__name__}")

    if isinstance(node, ast.Name):
      if node.id not in allowed_internal_names and node.id.startswith("_"):
        raise ValueError(f"Internal Name cannot be used!")

    if isinstance(node, (ast.NameConstant, ast.Constant)):
      if str(node.value).startswith("_"):
        raise ValueError(f"Internal Name cannot be used!")
    
    if isinstance(node, ast.Attribute):
      if node.attr.startswith("_"):
        raise ValueError(f"Internal Name cannot be used!")

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
      if node.func.id.startswith("_"):
        raise ValueError(f"Function { node.func.id } cannot be used!")
    
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
      raise ValueError(f"Cannot use object methods")


def compile_exp(exp: str, path_mapping={}, allowed_names=[], attr2sub=False, mode="eval"):
  return compile_ast(ast.parse(exp).body[0].value, path_mapping=path_mapping, allowed_names=allowed_names, attr2sub=attr2sub, mode=mode)

def compile_ast(tree: ast.AST, path_mapping={}, allowed_names=[], attr2sub=False, mode="eval"):
  #allowed_names += ["_r", "_s"]
  # Security Check
  security_check_ast(tree, allowed_internal_names=allowed_names)

  reslv_abs_mod = ResolveAbsolutePath(name_mapping=path_mapping, no_name_replace=attr2sub, reserved_names=allowed_names)
  attr2sub_mod  = Attribute2Subscribe()
  tree = reslv_abs_mod.visit(tree)
  tree = attr2sub_mod.visit(tree)

  if mode == "eval":
    expr = ast.Expression(body=tree)
  elif mode == "exec":
    tree.ctx = ast.Store()
    expr = ast.Module(body=[
      ast.Assign(
        targets=[tree],
        value =ast.Name(
          id='_value', 
          ctx=ast.Load())
      )
    ], type_ignores=[])
  expr = ast.fix_missing_locations(expr)
  return compile(expr, filename="<ast>", mode=mode)

def eval_compiled(comp, variables={}):
  return eval(comp, {"__builtins__":None}, dict(copy(safe_dict), **variables))

def set_state(comp, variables, value):
  exec(comp, {"__builtins__":None, "_value": value}, variables)

class ResolveAbsolutePath(ast.NodeTransformer):
  def __init__(self, name_mapping=None, reserved_names=[], no_name_replace=False):
    super().__init__()
    self._no_name_replace = no_name_replace
    self._name_mapping = name_mapping
    self._ignore_built_in = safe_list + reserved_names

  def visit_Name(self, node: ast.Name):
    if node.id in self._ignore_built_in or self._no_name_replace:
      return self.generic_visit(node)  

    if self._name_mapping and node.id in self._name_mapping:
      return self.generic_visit(self._name_mapping[node.id])

    return self.generic_visit(node)

class Attribute2Subscribe(ast.NodeTransformer):
  def visit_Attribute(self, node: ast.Attribute):
    attr  = ast.Str(s=node.attr)
    index = ast.copy_location(ast.Index(
      value=ast.copy_location(attr, node)
    ), node)
      
    return self.generic_visit(ast.copy_location(
      ast.Subscript(
        value = node.value,
        ctx= ast.Load(),
        slice=index
      ),node))

