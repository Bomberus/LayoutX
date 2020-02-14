from layoutx        import app
from layoutx.store  import create_store
from layoutx.view   import View, ResizeOption

store = create_store({}, {
  "facts": [],
  "loading": False
})

class LoadFacts(View):
  geometry  = "800x600+200+200"
  title     = "FactLoader"
  resizable = ResizeOption.BOTH
  template = """\
ScrollFrame
  Label(if="{loading}") Loading, please wait ...
  Button(command="{load_facts}") load facts
  Box(for="{fact in facts if fact.type == 'cat'}")
    Box(orient="horizontal")
      Label(background="{'grey' if fact.deleted else 'green'}") {fact.text}
"""

  async def load_facts(self):
    self.store.dispatch("SET_VALUE", {
      "path": ["loading"],
      "value": True
    })
    import aiohttp
    session = aiohttp.ClientSession()
    facts_list = []
    async with session.get("https://cat-fact.herokuapp.com/facts/random?animal_type=horse&amount=5") as facts:
      facts_list += await facts.json()
    
    async with session.get("https://cat-fact.herokuapp.com/facts/random?animal_type=cat&amount=5") as facts:
      facts_list += await facts.json()

    await session.close()

    self.store.dispatch("SET_VALUE", {
      "path": ["loading"],
      "value": False
    })

    self.store.dispatch("SET_VALUE", {
      "path": ["facts"],
      "value": facts_list
    })

if __name__ == "__main__":
  app.setup(store=store, rootView=LoadFacts)
  app.run()