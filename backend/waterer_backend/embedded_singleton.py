from waterer_backend.embedded_arduino import EmbeddedArduino

global _ARD
_ARD = None


def get_embedded_device() -> EmbeddedArduino:

    global _ARD

    if _ARD is None:
        _ARD = EmbeddedArduino()
        _ARD.connect()

    return _ARD
