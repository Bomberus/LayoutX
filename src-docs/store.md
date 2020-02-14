The store is powered by RxPY. If you want to get a deeper look, see  [official documentation](https://rxpy.readthedocs.io/en/latest/).

## Reducers

When creating the store you can additionally assign some reducers.

``` python
def set_name(state, payload):
  return {**state, **{"name": payload}}

reducers = {
  SET_NAME: set_name 
}

store = create_store(reducers, { "name": "" })
```

Then you can call the reducers via dispatch function:

``` python
# dispatch(REDUCER_NAME, PAYLOAD)
store.dispatch("SET_NAME", "My name")
```

## Subscribe to data changes
You can subscribe on store changes:

``` python
def on_change(value):
  print(value)

observer = store.subscribe(on_change)
observer.dispose() # Stop watching
```

## Watch a property

``` python
data = { "users" : [ { "name": "Test" } ] }

# Watch first user name
def on_first_user_name_changed(value):
  print(value)

observer = store.select_by_path("users.0.name")
observer.subscribe(on_first_user_name_changed)
observer.dispose() # stop watching
```