import sys, json
from binascii import hexlify, unhexlify
import spake2

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
    password = hexstr_to_bytes(req["password_hex"])
    assert isinstance(password, type(b"")), type(password)
    msg1 = hexstr_to_bytes(req["msg1_hex"])
    assert isinstance(msg1, type(b"")), type(msg1)
    if req["which"] in ("A", "B"):
        idA = hexstr_to_bytes(req["idA_hex"]) if "idA_hex" in req else b""
        assert isinstance(idA, type(b"")), type(idA)
        idB = hexstr_to_bytes(req["idB_hex"]) if "idB_hex" in req else b""
        assert isinstance(idB, type(b"")), type(idB)
        M = hexstr_to_bytes(req["M_hex"]) if "M_hex" in req else None
        N = hexstr_to_bytes(req["N_hex"]) if "N_hex" in req else None
        assert M is None # can't actually override this yet
        assert N is None
    elif req["which"] == "Symmetric":
        idS = hexstr_to_bytes(req["idS_hex"]) if "idS_hex" in req else b""
        S = hexstr_to_bytes(req["S_hex"]) if "S_hex" in req else None
        assert S is None
    if req["which"] == "A":
        s = spake2.SPAKE2_A(password, idA=idA, idB=idB)
        msg2 = s.start()
        key = s.finish(msg1)
    elif req["which"] == "B":
        s = spake2.SPAKE2_B(password, idA=idA, idB=idB)
        msg2 = s.start()
        key = s.finish(msg1)
    elif req["which"] == "Symmetric":
        s = spake2.SPAKE2_Symmetric(password, idSymmetric=idS)
        msg2 = s.start()
        key = s.finish(msg1)

    r = {"msg2_hex": bytes_to_hexstr(msg2),
         "key_hex": bytes_to_hexstr(key),
         }
    json.dump(r, sys.stdout)
    sys.exit(0)
