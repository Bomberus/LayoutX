from rx.subject   import BehaviorSubject
from rx           import operators as rxop
from typing       import Dict, Callable, List
from functools    import reduce, partial
from copy         import deepcopy
from operator     import itemgetter
import logging
from .utils import safe_get, safe_set, safer_eval, eval_compiled
from traceback import format_exc

__all__ = [ "Store", "create_store" ]

def apply_middleware(middlewares: [Callable]):
  def createStore(*args, **kwargs):
    store = createStore(*args, **kwargs)
    store.dispatch()
  return createStore


def set_value_reducer(state, payload):
  path, value = itemgetter("path", "value")(payload)

  return safe_set(state, path, value)


class Store:
  def __init__(self, reducer: Dict, init_value: Dict):
    self._reducer = reducer
    #Default Setter
    if "SET_VALUE" in self._reducer:
      raise KeyError("Reducer name 'SET_VALUE' is reserved")
    self._reducer["SET_VALUE"] = set_value_reducer

    self._state = BehaviorSubject({})
    self._state.on_next(init_value)

  def dispatch(self, name: str, payload: Dict = None):
    if name in self._reducer:
      self._state.on_next(
          self._reducer[name](
            self.state, payload 
          )
      )

  def get_reducers(self):
    return {name : partial(self.dispatch, name) for name in self._reducer}

  def select_compiled(self, comp, built_in=None, logger=None):
    def wrapper(state):
      built_in.update(state)
      try:
        return eval_compiled(comp, variables=built_in)
      except:
        # Could not evaluate, probably wrong binding
        if logger:
          logger.warn(f"Error could not evaluate binding", exp)
          logger.warn(format_exc(limit=2))
        return None
    return self.select([wrapper])

  def select(self, selectors: List):
    if len(selectors) == 1 and callable(selectors[0]):
      return self._state.pipe(
        rxop.map(selectors[0]),
        rxop.distinct_until_changed()
      )
    else:
      return self._state.pipe(
        rxop.map(lambda data: safe_get(data, selectors)),
        rxop.distinct_until_changed()
      )

  def select_by_path(self, path):
    return self.select(path.split("."))

  def subscribe(self, subscriber):
    return self._state.subscribe(subscriber)  

  @property
  def state(self) -> Dict:
    return self._state.value

def create_store(reducer: Dict, init_value: Dict, enhancer: Callable = None):
  store = Store(reducer, init_value)
  store = enhancer(store)(reducer, init_value)  if callable(enhancer) else store
  store.dispatch("INIT")
  return store

