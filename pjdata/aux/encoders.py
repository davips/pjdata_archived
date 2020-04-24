import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from json import JSONEncoder

import numpy as np


@dataclass(frozen=True)
class UUID:
    null_digest = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    null_pretty = '0000000000000000000'

    # TIP: Dataclass checks for equality on this field!
    digest: bytes = null_digest

    isnull = digest == null_digest

    @property
    @lru_cache()
    def pretty(self):
        return digest2pretty(self.digest)

    @staticmethod
    def from_pretty(txt):
        return UUID(pretty2bytes(txt))

    def __add__(self, other):
        """Merge with another UUIDs.

         Non commutative: a + b != b + a
         Reversible: (a + b) - b = a
         """
        return UUID(encrypt(msg_bytes=self.digest, key_bytes=other.digest))

    def __sub__(self, other):
        """Unmerge from last merged UUID."""
        if self.digest == self.null_digest:
            raise Exception(f'Cannot subtract from UUID={self.null_pretty}!')
        return UUID(decrypt(encrypted_msg=self.digest, key_bytes=other.digest))

    def __str__(self):
        return self.pretty

    __repr__ = __str__  # TODO: is this needed?


# @dataclass(frozen=True)
# class UUID:
#     # TIP: Dataclass checks for equality on this field!
#     bignumber: int = 0
#     isnull = bignumber == 0
#
#     @property
#     @lru_cache()
#     def pretty(self):
#         return int2pretty(self.bignumber)
#
#     @staticmethod
#     def from_pretty(txt):
#         return UUID(pretty2int(txt))
#
#     def __add__(self, other):
#         """Merge with another UUIDs.
#
#          Non commutative: a + b != b + a
#          Reversible: (a + b) - b = a
#          """
#         return UUID(rev_hash(msg_int=other.bignumber, key_int=self.bignumber))
#
#     def __sub__(self, other):
#         """Unmerge from last merged UUID."""
#         if self.bignumber == 0:
#             raise Exception(f'Cannot subtract from UUID={self.pretty}!')
#         return UUID(rev_unhash(=other.bignumber, key_int=self.bignumber))
#
#     def __str__(self):
#         return self.pretty
#
#     __repr__ = __str__  # TODO: is this needed?

def uuid00(bytes_content):
    return UUID(md5digest(bytes_content))


def md5digest(bytes_content):
    """
    Generates a hash intended for unique identification of content
     (unique for any reasonably finite universe).
    It is preferred to generate such hash on compressed data,
    since MD5 is much slower for large data than the compression itself.
    :param bytes_content:
        encoded content; it can be a packed object, a text, JSON,...
    :return: str <32 characters>
    """
    return hashlib.md5(bytes_content).digest()


def digest2pretty(bytes_digest):
    """
    Convert MD5 representation (16 bytes) to a friendly still short one
     (19 digits in base-107).
    :param bytes_digest:
    :return: string with 19 digits, padded with '0' when needed
    """
    return int2pretty(bytes2int(bytes_digest))


def int2pretty(number):
    """Convert number to a tiny human-friendly string (19 chars)."""
    return enc(number).rjust(19, '0')


def int2bytes(x):
    return x.to_bytes(16, 'big')


def bytes2int(digest):
    """
    Convert MD5 digest (16 bytes) to int.
    :param digest:
    :return: int
    """
    return int.from_bytes(digest, 'big')


def dec(digest, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                         'abcdefghijklmnopqrstuvwxyz'
                         'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """
    Decode digest from base-len(alphabet).
    See enc() for more info.
    :param digest:
    :param alphabet:
    :return:
    """
    res = 0
    last = len(digest) - 1
    base = len(alphabet)
    for i, d in enumerate(digest):
        res += alphabet.index(d) * pow(base, last - i)
    return res


def enc(big_number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                             'abcdefghijklmnopqrstuvwxyz'
                             'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """
    Encode an integer to base-n. n = len(alphabet).
    The default is base107 since it is enough to represent MD5 as 19 chars.
    The selected default alphabet contains only numbers and letters. Similar
    letters were arbitrarily removed.
    This alphabet is intended to be printable and to be free of
    disruptive characters, i.e. any combination of adjacent characters will be
    understood as a single word by most linux terminals and editors.
    This can be seen as the subset of 'double-click-friendly chars'.

    The following list shows how the alphabet size relates to the number of
    necessary digits to represent the biggest MD5 number (2^128).
    The hexdigest alredy uses 32 digits, so we want less than that.
    According to the list below, good choices for the alphabet size would be in
    the range 85-185, since values higher than 256 are outside latin1 range.

    alphabet-size   number-of-digits   comments
    2 128 # crude md5 as binary string
    16 32 # hexdigest as string
    24 28
    41 24 # reducing from 32 to 24 is kind of a improvement
    48 23
    57 22
    69 21
    85 20 # base64 library provides base85, but it is not double_click_friendly
    107 19 # super friendly (our default choice)
    139 18 # not terminator/intellij friendly
    185 17 # not double_click_friendly
    256 16 # would include lots of unprintable characters
    371 15 # 371 and beyond is outside a single byte and latin1
    566 14 # idem
    16-bit 4 # idem
    32-bit 2 # UTF-8?

    147 is the size of the largest subset of latin1 that is
    double_click_friendly. Latin1 is compatible with UTF-8 and extends ASCII.

    Example alphabets are given below:

    gnome-terminal friendly (147)  [\\ <- escaped slash]
#%&+,-./0123456789=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_abcdefghijklmnopqrstuvwxyz
~ª²³µ·¹º¼½¾ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij friendly (125)
#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij[ctrl+w] friendly (124)
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz
ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ

    gnome-terminal/terminator/intellij without _ and some twin chars (107)
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ

    :param alphabet: string with allowed digits
    :param big_number: an integer, usually a big MD5-like one
    :return: string representing a base-107 number (or any other base,
    depending on the given alphabet length)"""
    l = len(alphabet)
    res = []
    while True:
        res.append(alphabet[big_number % l])
        big_number = big_number // l
        if big_number == 0:
            break
    return ''.join(res)[::-1]


def encrypt(msg_bytes, key_bytes):
    """AES 16 bytes encryption."""
    from Crypto.Cipher import AES
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    return cipher.encrypt(msg_bytes)


def decrypt(encrypted_msg, key_bytes):
    """AES 16 bytes decryption."""
    from Crypto.Cipher import AES
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    return cipher.decrypt(encrypted_msg)


# def checksum(number):
#     return number %


# def rshift(msg_int):
#     return (msg_int >> 1) | ((msg_int & 1) << 127)
#
#
# def lshift(msg_int):
#     return ((msg_int & mask_127ones) << 1) | (msg_int >> 127)
#

# def rev_hash(msg_int, key_int):
#     """A *reversible* hash, the nightmare of cryptologists."""
#     result = lshift(msg_int) ^ key_int
#     return pepper(result)
#
#
# def rev_unhash(encrypted_msg_int, key_int):
#     xor = pepper(encrypted_msg_int) ^ key_int
#     return rshift(xor)

# def pepper(msg, index):
#     print(bin(msg))
#     pos = (msg >> index) & 127
#     print(bin(pos))
#     peppered = msg ^ (2 ** pos)
#     print(bin(peppered))
#     pos2 = (peppered >> index) & 127
#     print(bin(pos2))
#     correction = 255 ((pos ^ pos2) << index)
#     print(bin(correction))
#     print(bin(msg & correction))
#     exit()
#
#
# def rev_hash(msg_int, key_int):
#     """A *reversible* hash, the nightmare of cryptologists."""
#     xor = msg_int ^ key_int
#     lshift = (((xor & mask_127ones) << 1) | (xor >> 127))
#     for i in range(6):
#         lshift = pepper(lshift, i)
#     return lshift ^ key_int
#
#
# def rev_unhash(encrypted_msg_int, key_int):
#     xor = encrypted_msg_int ^ key_int
#     for i in reversed(range(6)):
#         xor = pepper(xor, i)
#     rshift = (xor >> 1) | ((xor & 1) << 127)
#     return rshift ^ key_int


def pretty2bytes(digest):
    """Convert tiny string (19 chars) to bytes."""
    return dec(digest).to_bytes(16, 'big')


def pretty2int(digest):
    """Convert tiny string (19 chars) to bytes."""
    return dec(digest)


def prettydigest(bytes_content):
    return digest2pretty(md5digest(bytes_content))


def intlist2bytes(lst):
    """Each int becomes 4 bytes. max=4294967294"""
    return b''.join([n.to_bytes(4, byteorder='big') for n in lst])


def bytes2intlist(bytes_content):
    """Each 4 bytes become an int."""
    n = len(bytes_content)
    return [bytes2int(bytes_content[i:i + 4]) for i in range(0, n, 4)]


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj is not None:
            if isinstance(obj, np.ndarray):
                return str(obj)
            elif isinstance(obj, UUID):
                return obj.pretty
            elif not isinstance(
                    obj, (list, set, str, int, float, bytearray, bool)):
                return obj.jsonable

        return JSONEncoder.default(self, obj)
