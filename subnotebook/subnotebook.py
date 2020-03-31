from IPython.display import clear_output
import asyncio
import nbformat
from nbclient import NotebookClient
import scrapbook
import nest_asyncio
import inspect
import json
from binascii import b2a_base64


def open_nb(path):
    nb = nbformat.read(path, nbformat.NO_CONVERT)
    subnb = SubNotebook(nb)
    return subnb


def _run_sync(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    nest_asyncio.apply(loop)
    loop.run_until_complete(coro)


def run(subnb, **kwargs):
    if isinstance(subnb, SubNotebook):
        _run_sync(subnb(**kwargs))
    elif inspect.isawaitable(subnb):
        raise RuntimeError('Call run(coro, **kwargs)')
    else:
        subnb = open_nb(subnb)
        _run_sync(subnb(**kwargs))
    results = subnb.get_results()
    return results


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
    def __init__(self, *args, display=False):
        for i, arg in enumerate(args):
            result_i = self.Result_i + i
            if display:
                scrapbook.glue(f'__display_{result_i}__', arg, 'display')
            else:
                scrapbook.glue(f'__data_{result_i}__', arg)
        Return.Result_i += len(args)


class SubNotebook:

    def __init__(self, nb):
        # insert place-holder for the parameter initialization cell
        nb['cells'].insert(0, None)
        self.nb = nb
        self.kwargs = {}
        self.kwargs_display = {}

    def pass_display(self, **kwargs):
        self.kwargs_display.update(kwargs)

    def _init_params(self, **kwargs):
        kwargs.update(self.kwargs)

        # pass parameters to subnotebook
        # we glue the parameter values in this cell (caller notebook)
        # and catch the output so that we can put it in the first cell of the subnotebook
        # then we clear the output of this cell
        outputs = []
        for k, v in kwargs.items():
            data, metadata = scrapbook.glue(k, v)
            outputs.append({'data': data, 'metadata': metadata, 'output_type': 'display_data'})
        for k, v in self.kwargs_display.items():
            data, metadata = scrapbook.glue(k, v, 'display')
            for k2, v2 in data.items():
                if isinstance(v2, bytes):
                    data[k2] = b2a_base64(v2).decode('ascii').replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace("'", "\\'")
            outputs.append({'data': data, 'metadata': metadata, 'output_type': 'display_data'})
        nb = json.dumps(nbformat.v4.new_notebook(
            metadata={
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                }
            },
            cells=[nbformat.v4.new_code_cell('', outputs=outputs)]
        ))
        init_code = [
            'import scrapbook',
            'import nbformat',
            'from subnotebook import Reglued',
            f"nb = '{nb}'",
            'nb = nbformat.reads(nb, nbformat.NO_CONVERT)',
            'nb = scrapbook.read_notebook(nb)'
        ]
        init_code += [f"{k} = nb.scraps.get('{k}').data" for k in kwargs]
        init_code += [f"nb.reglue('{k}')" for k in self.kwargs_display]
        init_code = '\n'.join(init_code)
        init_cell = nbformat.v4.new_code_cell(init_code)
        self.nb['cells'][0] = init_cell

    def run(self, **kwargs):
        self._init_params(**kwargs)
        NotebookClient(nb=self.nb, nest_asyncio=True).execute()
        results = self.get_results()
        clear_output()
        return results

    def run_async(self, **kwargs):
        self._init_params(**kwargs)
        NotebookClient(nb=self.nb).async_execute()
        results = self.get_results()
        return results

    def get_results(self):
        nb = scrapbook.read_notebook(self.nb)
        scraps = [scrap for scrap in nb.scraps if scrap.startswith(('__data_', '__display_'))]
        results = (
            nb.scraps[scrap].data if scrap.startswith('__data_') else
            Reglued(nb.reglue, scrap)
            for scrap in scraps
        )
        return results


class Reglued:
    def __init__(self, reglue, scrap):
        self.reglue = reglue
        self.scrap = scrap
    def __repr__(self):
        self.reglue(self.scrap)
        return ''
