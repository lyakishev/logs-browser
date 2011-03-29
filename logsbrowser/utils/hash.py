import pickle
import hashlib

def hash_value(params):
    pick = pickle.dumps(params)
    hash_v = hashlib.md5(pick).hexdigest()
    return "".join(["_",hash_v])
