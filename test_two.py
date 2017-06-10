from __future__ import print_function
import sys, json
from binascii import hexlify, unhexlify
import requests

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

password = b"password"
base = dict(password_hex=bytes_to_hexstr(password),
            #params="1024",
            )

def call(url, **extra):
    args = base.copy()
    args.update(**extra)
    return requests.post(url, json=args).json()

def run():
    urlA = sys.argv[1]
    urlB = sys.argv[2]

    a1 = call(urlA)
    print("A1:", a1)
    b1 = call(urlB, msg_in_hex=a1["msg_out_hex"])
    print("B1:", b1)
    a2 = call(urlA, state=a1["state"], msg_in_hex=b1["msg_out_hex"])
    print("A2:", a2)
    print("A key:", b1["key_hex"])
    print("B key:", a2["key_hex"])
    print("match:", b1["key_hex"] == a2["key_hex"])

if __name__ == '__main__':
    run()

