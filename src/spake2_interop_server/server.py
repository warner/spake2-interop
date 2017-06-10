from twisted.python import usage


class Options(usage.Options):
    synopsis = "[options]"
    longdesc = "SPAKE2 interop server"
    optParameters = [
        ["port", "p", "tcp:8705", "listening endpoint"],
        ]

def makeService(config):
    s = service.MultiService()


    return s

