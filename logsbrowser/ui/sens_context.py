class Sensitive:
    def __init__(self, sens_func):
        self.sens_func = sens_func

    def __enter__(self):
        self.sens_func(False)

    def __exit__(self, *args):
        self.sens_func(True)
