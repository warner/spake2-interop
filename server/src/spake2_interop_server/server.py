from attr import attrs, attrib
from attr.validators import instance_of
from twisted.python import usage, log
from twisted.application import internet
from twisted.internet import reactor, endpoints
from twisted.web import resource, static, server
#from twisted.internet.utils import getProcessOutputAndValue
import subprocess

# curl --data-binary '{"password_hex": "abac", "msg1_hex": "420a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/A
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "410a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/B
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "53fd036b02cb66af2c4283708b455f45282ef9482640f30923de2584040a929c52"}' http://localhost:8705/Symmetric

@attrs
class Dispatcher(resource.Resource, object):
    _cmd_path = attrib(validator=instance_of(type(b"")))
        
    def render_POST(self, request):
        req_data = request.content.read()

        #(out, err, rc) = yield getProcessOutputAndValue(self._cmd_path
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
    root.putChild(b"0.3", Dispatcher("ve-p03/bin/spake2_interop_python_0_3"))
    root.putChild(b"0.7", Dispatcher("ve-p07/bin/spake2_interop_python_0_7"))

    ep = endpoints.serverFromString(reactor, config["port"])
    s = internet.StreamServerEndpointService(ep, site)
    return s

