import sys, json
from binascii import hexlify, unhexlify
import spake2
from spake2.params import (ParamsEd25519, Params1024, Params2048, Params3072)

# one version per server

def bytes_to_hexstr(b):
    assert isinstance(b, type(b""))
    hexstr = hexlify(b).decode("ascii")
    assert isinstance(hexstr, type(u""))
    return hexstr
def hexstr_to_bytes(hexstr):
    assert isinstance(hexstr, type(u""))
    b = unhexlify(hexstr.encode("ascii"))
    assert isinstance(b, type(b""))
    return b

# curl --data-binary '{"password_hex": "abac", "msg1_hex": "420a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/A
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "410a30f44d57f0e775b1905895106d482b473d78cf917c3f051b03325a66e54170"}' http://localhost:8705/B
# curl --data-binary '{"password_hex": "abac", "msg1_hex": "53fd036b02cb66af2c4283708b455f45282ef9482640f30923de2584040a929c52"}' http://localhost:8705/Symmetric

def run():
    # accept a JSON dictionary on stdin, write the results as a JSON
    # dictionary on stdout
    req = json.load(sys.stdin)
    resp = process(req)
    json.dump(resp, sys.stdout)
    sys.exit(0)

# msg1: create instance, run both, return (msg2, key)
# nothing: create instance, run start, return (msg2, state)
# msg1, state: rebuild instance, run finish, return (key)

def process(req):
    password = hexstr_to_bytes(req["password_hex"])
    assert isinstance(password, type(b"")), type(password)
    msg_in = hexstr_to_bytes(req["msg_in_hex"]) if "msg_in_hex" in req else None
    state = req["state"] if "state" in req else None
    if state is not None:
        assert msg_in is not None, (msg_in, state)
    if msg_in is not None:
        assert isinstance(msg_in, type(b"")), type(msg_in)
    assert req["which"] in ("A", "B", "Symmetric")

    params = {"Ed25519": ParamsEd25519,
              "1024": Params1024,
              "2048": Params2048,
              "3072": Params3072,
              }[req.get("params", "Ed25519")]

    rc = {}
    if req["which"] in ("A", "B"):
        idA = hexstr_to_bytes(req["idA_hex"]) if "idA_hex" in req else b""
        assert isinstance(idA, type(b"")), type(idA)
        idB = hexstr_to_bytes(req["idB_hex"]) if "idB_hex" in req else b""
        assert isinstance(idB, type(b"")), type(idB)
        M = hexstr_to_bytes(req["M_hex"]) if "M_hex" in req else None
        N = hexstr_to_bytes(req["N_hex"]) if "N_hex" in req else None
        assert M is None # can't actually override this yet
        assert N is None
        klass = {"A": spake2.SPAKE2_A,
                 "B": spake2.SPAKE2_B}[req["which"]]
        if state is None:
            s = klass(password, idA=idA, idB=idB, params=params)
            if msg_in is None:
                rc["msg_out_hex"] = bytes_to_hexstr(s.start())
                #"secret_scalar"
                rc["state"] = s.serialize()
            else:
                rc["msg_out_hex"] = bytes_to_hexstr(s.start())
                rc["key_hex"] = bytes_to_hexstr(s.finish(msg_in))
        else:
            s = klass.from_serialized(state, params=params)
            rc["key_hex"] = bytes_to_hexstr(s.finish(msg_in))
        rc["M_hex"] = bytes_to_hexstr(s.params.M.to_bytes())
        rc["N_hex"] = bytes_to_hexstr(s.params.N.to_bytes())
        rc["my_blinding_hex"] = bytes_to_hexstr(s.my_blinding().to_bytes())
        rc["my_unblinding_hex"] = bytes_to_hexstr(s.my_unblinding().to_bytes())
    elif req["which"] == "Symmetric":
        idS = hexstr_to_bytes(req["idS_hex"]) if "idS_hex" in req else b""
        S = hexstr_to_bytes(req["S_hex"]) if "S_hex" in req else None
        assert S is None

        if state is None:
            s = spake2.SPAKE2_Symmetric(password, idSymmetric=idS,
                                        params=params)
            if msg_in is None:
                rc["msg_out_hex"] = bytes_to_hexstr(s.start())
                rc["state"] = s.serialize()
            else:
                rc["msg_out_hex"] = bytes_to_hexstr(s.start())
                rc["key_hex"] = bytes_to_hexstr(s.finish(msg_in))
        else:
            s = spake2.SPAKE2_Symmetric.from_serialized(state, params=params)
            rc["key_hex"] = bytes_to_hexstr(s.finish(msg_in))
        rc["S_hex"] = bytes_to_hexstr(s.params.S.to_bytes())

    rc["pw_scalar_dec"] = "{:d}".format(s.pw_scalar)
    rc["secret_scalar_dec"] = "{:d}".format(s.xy_scalar)
    rc["secret_element_hex"] = bytes_to_hexstr(s.xy_elem.to_bytes())
    return rc
