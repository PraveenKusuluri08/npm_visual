import string


class NSAliasGenerator:
    """A simple generator for unique aliases (a, b, c, ..., aa, ab, ac, ...)."""

    predefined = {
        "str": "_str",
        "int": "_int",
        "float": "_float",
        "bool": "_bool",
        "list[]": "_[]",
        "list[str]": "list[str]",
        "list[dict]": "_list[dict]",
        "dict[str,dict]{}": "_{}",
        "list[dict[str,dict]{(name,str),(email,str)}]": "[_Contact]",
        "dict[str,dict]{(keyid,str),(sig,str)}": "_Signature",
        "dict[str,dict]{(integrity,str),(shasum,str),(tarball,str),(fileCount,int),(unpackedSize,int),(signatures,list[dict[str,dict]{(keyid,_str),(sig,_str)}])}": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
    }

    def __init__(self):
        # Start from 'a'
        self.counter = 0
        self.alphabet = string.ascii_lowercase  # 'a' to 'z'

    def generate_alias(self, structure_full: str) -> str:
        """Generate the next unique alias in the sequence (a, b, c, ..., aa, ab, ac, ...)."""
        if structure_full in self.predefined:
            return self.predefined[structure_full]
        alias = "_" + self._int_to_base26(self.counter)
        self.counter += 1
        return alias

    def _int_to_base26(self, num: int) -> str:
        """Convert an integer to a base-26 string (like Excel column numbering)."""
        result = []
        while num >= 0:
            result.append(self.alphabet[num % 26])
            num = num // 26 - 1
            if num < 0:
                break
        return "".join(reversed(result))
