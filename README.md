# Subnotebook

Run a notebook as you would call a Python function.

Two modes are currently supported:

- An in-process mode, where the subnotebook is executed in the same kernel your
interpreter is running in (but in a different name space). This allows to pass
parameters and get results back, including widgets.
```python
from subnotebook import open_nb

# open your notebook
nb = open_nb('sub_notebook.ipynb')

# execute your notebook, pass parameters, get back results
ab, ba, slider, output = nb.run(a='c', b='d')
```

- An out-of-process mode, where the subnotebook is executed and served using
[Voila](https://voila.readthedocs.io), and included in the main notebook as an
IFrame. This mode only allows to display the outputs of the subnotebook, which
is useful for offloading the main notebook but also to offer a UI to resources
you would not have access to, such as big data or protected data.
```python
from subnotebook import display_nb

display_nb('widget_notebook.ipynb')
```
