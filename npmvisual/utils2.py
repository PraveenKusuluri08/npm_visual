import hashlib


def ns_hash(name: str, length=40) -> str:
    hash: str = hashlib.sha1(name.encode("UTF-8")).hexdigest()
    return hash[:length]
