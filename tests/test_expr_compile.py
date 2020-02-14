import unittest
from layoutx.utils import compile_exp, eval_compiled, set_state

class TestExpCompiler(unittest.TestCase):
  
  def test_security(self):
    try:
      compile_exp("name._internal_")
      assert False, "Exp should not compile"
    except ValueError as e:
      assert str(e) == "Internal Name cannot be used!"

    # Allowed names
    try:
      compile_exp("_s.name", allowed_names=["_s"] )
      assert True
    except:
      assert False, "Variable Names are possible"

    # Normal statement
    try:
      compile_exp("name.value")
      assert True
    except:
      assert False, "Exp should compile"

  def test_simple_expression(self):
    comp = compile_exp("1 + 2")
    assert eval_compiled(comp) == 3

  def test_path_mapping(self):
    state = { 
      "artists": [{
        "songs": [
          {
          "name": "1"
          },{
          "name": "2"
          }
        ]
      }]
    }

    import ast

    path_mapping = {
      "artist": ast.parse('_s.artists[0]').body[0].value,
      "single": ast.parse('artist.songs[0]').body[0].value,
      "singleName": ast.parse('single.name').body[0].value
    }
    
    comp = compile_exp("singleName", path_mapping=path_mapping, allowed_names=["_s"] )
    assert eval_compiled(comp, variables={"_s": state}) == "1"

  def test_set_state(self):
    state = { 
      "artists": [{
        "songs": [
          {
          "name": "1"
          },{
          "name": "2"
          }
        ]
      }]
    }

    variables={"_s": state}

    import ast

    path_mapping = {
      "artist": ast.parse('_s.artists[0]').body[0].value,
      "single": ast.parse('artist.songs[0]').body[0].value,
      "singleName": ast.parse('single.name').body[0].value
    }
    
    comp = compile_exp("singleName", path_mapping=path_mapping, allowed_names=["_s"], mode="exec")
    set_state(comp, variables, "New")
    assert state["artists"][0]["songs"][0]["name"] == "New", "State not set"

if __name__ == '__main__':
  unittest.main()