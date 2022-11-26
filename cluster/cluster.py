"""Root class for clusters"""


class Singletone:
    """Singletone implementation"""
    _instance: dict = {}

    def __new__(cls, *args, **kwargs):
        if cls not in Singletone._instance:
            Singletone._instance[cls] = \
                super(Singletone, cls).__new__(cls, *args, **kwargs)
        return Singletone._instance[cls]


class Cluster(Singletone):
    """Root class for clusters"""
