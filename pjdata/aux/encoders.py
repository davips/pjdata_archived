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

    @property
    @lru_cache()
    def pretty(self):
        return prettydigest(self.digest)

    def __add__(self, other):
        """Merge with another UUIDs.

         Non commutative: a + b != b + a
         Reversible: (a + b) - b = a
         """
        return UUID(push(new=other.digest, stack=self.digest))

    def __sub__(self, other):
        """Unmerge from last merged UUID."""
        if other.digest == self.null_digest:
            raise Exception(f'Cannot subtract from UUID={self.null_pretty}!')
        return UUID(pop(last=other.digest, stack=self.digest))

    def __str__(self):
        return self.pretty

    __repr__ = __str__  # TODO: is this needed?


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


def prettydigest(bytes_digest):
    """
    Convert MD5 representation (16 bytes) to a friendly still short one
     (19 digits in base-107).
    :param bytes_digest:
    :return: string with 19 digits, padded with 'Ø' when needed
    """
    return int2pretty(bytes2int(bytes_digest))


def int2pretty(number):
    """Convert number to a tiny human-friendly string (19 chars)."""
    return enc(number).rjust(19, '0')


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


def push(new, stack):
    """Noncommutative combination of two sequences of bytes.

    Results in a new one representing the chain transformation of both.
    It is reversible by unmerge:
    new_stack = push(new, stack)
    stack = pop(new, new_stack)
    """
    return encrypt(msg_bytes=stack, key_bytes=new)


def pop(last, stack):
    """Undo noncommutative combination of two sequences of bytes."""
    return decrypt(encrypted_msg=stack, key_bytes=last)


# def hex2int(hexdigest):
#     """
#     Convert hex MD5 representation (32 digits in base-16) to int.
#     :param hexdigest:
#     :return: int
#     """
#     return int(hexdigest, 16)

def pretty2bytes(digest):
    """Convert tiny string (19 chars) to bytes."""
    return dec(digest).to_bytes(19, 'big')


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj is not None:
            from pjdata.step.transformation import Transformation
            if isinstance(obj, Transformation):
                # This eval is here instead of at transformation.py, to defer
                # such heavy calculation to the printing time, i.e. when needed.
                jsonable = json.loads(obj.jsonable)
                jsonable['step'] = obj.step
                return jsonable
            elif isinstance(obj, np.ndarray):
                return str(obj)
            elif not isinstance(
                    obj, (list, set, str, int, float, bytearray, bool)):
                return obj.jsonable

        return JSONEncoder.default(self, obj)
