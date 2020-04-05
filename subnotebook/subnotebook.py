import nbformat
import inspect


def open_nb(path):
    nb = nbformat.read(path, nbformat.NO_CONVERT)
    subnb = SubNotebook(nb)
    return subnb


def default_value(**kwargs):
    frame = inspect.currentframe()
    try:
        out_locals = frame.f_back.f_locals
    finally:
        del frame
    for k, v in kwargs.items():
        if k not in out_locals:
            out_locals[k] = v


class Return:
    Result_i = 0
    def __init__(self, *args):
        frame = inspect.currentframe()
        try:
            out_locals = frame.f_back.f_locals
        finally:
            del frame
        for i, arg in enumerate(args):
            result_i = self.Result_i + i
            out_locals[f'__result_{result_i}__'] = arg
        Return.Result_i += len(args)


class SubNotebook:

    def __init__(self, nb):
        self.nb = nb
        self.kwargs = {}

    def run(self, **kwargs):
        self.namespace = kwargs
        for cell in self.nb.cells:
            if cell['cell_type'] == 'code':
                exec(cell['source'], self.namespace)
        results = self.get_results()
        return results

    def get_results(self):
        results = [self.namespace[name] for name in self.namespace if name.startswith('__result_')]
        if len(results) == 1:
            return results[0]
        return tuple(results)
