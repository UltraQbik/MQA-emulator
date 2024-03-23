class Extensions:
    """
    Class containing all the extensions
    """

    LIST: dict[str, type] = {}


def load_extension(ext: type):
    Extensions.LIST[ext.__name__] = ext
