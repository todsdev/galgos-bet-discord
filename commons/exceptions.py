from commons.constants import Constants


class GalgosBetException(Exception):
    def __init__(self, message=Constants.Errors.GALGOS_EXCEPTION):
        super().__init__(message)
