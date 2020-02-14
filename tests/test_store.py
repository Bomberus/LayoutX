import unittest
import unittest.mock
from layoutx.store import create_store


class TestStore(unittest.TestCase):
  
  def test_simple(self):
    observer = unittest.mock.MagicMock()
    store= create_store({}, {"name": "Test"})
    assert store.state == {"name": "Test"}
    
    store.subscribe(observer.subscribe)
    assert len(observer.method_calls) == 1
    
    store.dispatch("SET_VALUE", {"path": ["name"], "value": "Test2"})
    assert len(observer.method_calls) == 2
    
    assert store.state == {"name": "Test2"}

  def test_dispose(self):
    store= create_store({}, {"name": "Test"})
    
    mock = unittest.mock.MagicMock()

    observer = store.subscribe(mock)
    assert len(mock.method_calls) == 1
    
    observer.dispose()

    store.dispatch("SET_VALUE", {"path": ["name"], "value": "Test2"})
    assert len(mock.method_calls) == 1
  
  def test_reducer(self):
    def name_reducer(state, payload):
      return {**state, **{ "name": payload }}

    store = create_store({ "NAME_REDUCER" : name_reducer }, {"name": "Test"})
    store.dispatch("NAME_REDUCER", "Test2")
    
    assert store.state == {"name": "Test2"}

  def test_select(self):
    store = create_store({},{
      "hosts": [{
        "url": "1"
      },{
        "url": "2"
      }]
    })

    mock = unittest.mock.MagicMock()

    observer = store.select_by_path("hosts.1.url")
    observer.subscribe(mock)
    assert len(mock.method_calls ) == 1
    assert mock.method_calls[0][0] == "on_next"
    assert mock.method_calls[0][1][0] == "2"

    store.dispatch("SET_VALUE", {"path": ["hosts", "0", "url"], "value": "3"})
    assert len(mock.method_calls ) == 1
    assert store.state == { "hosts": [{ "url": "3" },{ "url": "2" }] }

  
  def test_select_exp(self):
    pass

if __name__ == '__main__':
  unittest.main()