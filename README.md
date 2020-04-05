# Subnotebook

Run a notebook as you would call a Python function, pass parameters and get
results back, including widgets.

Say you have a main notebook `main_notebook.ipynb`:

```python
from subnotebook import open_nb

# open your notebook
nb = open_nb('sub_notebook.ipynb')

# execute your notebook, pass parameters, get back results
ab, ba, slider, output = nb.run(a='c', b='d')

# you can manipulate the subnotebook's returned values
print(ab, ba)

# show the slider widget
slider

# the output of this cell will print the slider's value
output
```

And a subnotebook `sub_notebook.ipynb`:

```python
import ipywidgets
from subnotebook import default_value, Return

# give default values to the input arguments
default_value(a='a', b='b')

# here we create a slider widget, observe its value
# and print it in an output widget
slider = ipywidgets.IntSlider()
output = ipywidgets.Output()
def on_value_change(change):
    with output:
        print(change['new'])
slider.observe(on_value_change, names='value')

# you can also return values which depend on the input arguments
ab = a + b
ba = b + a

# return the results of the subnotebook
Return(ab, ba, slider, output)
```
