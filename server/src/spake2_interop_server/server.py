import json
from twisted.python import usage, log
from twisted.application import internet
from twisted.internet import reactor, endpoints
from twisted.web import resource, static, server
import subprocess

# curl --data-binary '{"password_hex": "abac", "msg1_hex": "420a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/A
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "410a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/B
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "53fd036b02cb66af2c4283708b455f45282ef9482640f30923de2584040a929c52"}' http://localhost:8705/Symmetric

class Dispatcher(resource.Resource, object):
    def __init__(self, cmd_path, **kwargs):
        resource.Resource.__init__(self)
        assert isinstance(cmd_path, type(b"")), (cmd_path, type(cmd_path))
        self._cmd_path = cmd_path
        self._extra_args = kwargs
        
    def render_POST(self, request):
        req = json.load(request.content)
        for k,v in self._extra_args.items():
            req[k] = v
        req_data = json.dumps(req)

        p = subprocess.Popen([self._cmd_path],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             )
        (output, err) = p.communicate(req_data)
        rc = p.returncode
        if rc != 0:
            log.msg("error running command '{}': rc={}, err='{}'".format(
                self._cmd_path, rc, err))
            raise ValueError()
        return output

class ABS(resource.Resource, object):
    def __init__(self, cmd_path):
        resource.Resource.__init__(self)
        self.putChild(b"A", Dispatcher(cmd_path, which="A"))
        self.putChild(b"B", Dispatcher(cmd_path, which="B"))
        self.putChild(b"S", Dispatcher(cmd_path, which="Symmetric"))


# 'twist' will load this file and look for 'Options' and 'makeService'

class Options(usage.Options):
    synopsis = "[options]"
    longdesc = "SPAKE2 interop server"
    optParameters = [
        ["port", "p", "tcp:8705", "listening endpoint"],
        ]

def makeService(config):
    root = resource.Resource()
    site = server.Site(root)

    root.putChild(b"", static.Data(b"SPAKE2 interop server", "text/plain"))
    root.putChild(b"0.3", ABS("ve-p03/bin/spake2_interop_python_0_3"))
    root.putChild(b"0.7", ABS("ve-p07/bin/spake2_interop_python_0_7"))

    ep = endpoints.serverFromString(reactor, config["port"])
    s = internet.StreamServerEndpointService(ep, site)
    return s

