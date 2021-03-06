Useful Resources:
* Latest Blender API: https://docs.blender.org/api/current/
* https://docs.blender.org/api/2.79/info_tips_and_tricks.html
* https://www.blender.org/api/blender_python_api_2_77_release/bpy.types.RenderEngine.html?

Paste this into your code to drop into an interactive Python interpreter in this line:
```python
__import__('code').interact(local=dict(globals(), **locals()))
```

If you want to edit a Blender property without triggering it's update function, 
access it like in this example:
```python
class Test:
    def update_a(self, context):
        # Wrong, would cause endless recursion
        # self.b = str(self.a)
        # Correct, does not trigger b's update method
        self["b"] = str(self.a)
        
    def update_b(self, context):
        self["a"] = int(self.b)

    a = IntProperty(update=update_a)
    b = StringProperty(update=update_b)
```