import nbformat
import inspect
#import voila.app
#import nest_asyncio
import subprocess
from IPython.display import IFrame, display
import atexit


voila_processes = []


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


def get_lines(std_pipe):
    '''Generator that yields lines from a standard pipe as there are printed.'''
    for line in iter(std_pipe.readline, ''):
        yield line
    std_pipe.close()


def display_nb(path, server_address='http://*:*/', width='100%', height=1000):
    #nest_asyncio.apply()
    #voila_app = voila.app.Voila()
    #voila_app.initialize([path, '--no-browser', "--Voila.tornado_settings={'headers':{'Content-Security-Policy':\"frame-ancestors 'self' " + server_address + "\"}}"])
    #voila_app.start()
    #print(voila_app.server_url)

    cmd = ['voila', '--no-browser', "--Voila.tornado_settings={'headers':{'Content-Security-Policy':\"frame-ancestors 'self' " + server_address + "\"}}", path]
    voila = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    voila_processes.append(voila)

    # wait until server is ready and get the address
    for line in get_lines(voila.stderr):
        if line.startswith('http://'):
            voila_address = line.strip()
            break

    display(IFrame(src=voila_address, width=width, height=height))


def kill_processes(processes):
    for p in processes:
        p.kill()


atexit.register(kill_processes, voila_processes)
