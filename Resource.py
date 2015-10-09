

class Resource:

    def __init__(self, **kwargs):
        for key in kwargs:
            self[key] = kwargs[key]
