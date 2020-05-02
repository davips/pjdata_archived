import hashlib
from dataclasses import dataclass
from functools import lru_cache, partial
from json import JSONEncoder
from operator import itemgetter

import fastrand
import numpy as np
from numpy.random.mtrand import random
from sortedcontainers import SortedSet, SortedDict


class UUID:
    null_matrix = list(range(35))
    null_pretty = '0000000000000000000'
    _id = None

    def __init__(self, matrix_or_number_or_pretty):
        if isinstance(matrix_or_number_or_pretty, list):
            if len(matrix_or_number_or_pretty) != 35:
                raise Exception('Permutation matrix should be 35x35! Not',
                                len(matrix_or_number_or_pretty))
            self.matrix = matrix_or_number_or_pretty
        elif isinstance(matrix_or_number_or_pretty, int):
            if matrix_or_number_or_pretty > 2 ** 128 - 1:
                raise Exception('Number should be 128-bit! Not 2**',
                                log2(matrix_or_number_or_pretty))
            self.matrix = int2pmatrix(matrix_or_number_or_pretty)
        elif isinstance(matrix_or_number_or_pretty, str):
            if len(matrix_or_number_or_pretty) not in [18, 19]:
                raise Exception('Pretty str should be 18-19 chars long! Not',
                                len(matrix_or_number_or_pretty))
            self._id = matrix_or_number_or_pretty
            self.matrix = int2pmatrix(pretty2int(matrix_or_number_or_pretty))
        else:
            raise Exception('Wrong argument type for UUID:',
                            type(matrix_or_number_or_pretty))
        self.isnull = self.matrix == self.null_matrix

    # @property
    # @lru_cache()
    def inv(self):
        """Pretty printing version, proper for use in databases also."""
        return UUID(transpose(self.matrix))

    # @property
    def id(self):
        """Pretty printing version, proper for use in databases also."""
        if self._id is None:
            self._id = int2pretty(pmatrix2int(self.matrix))
        return self._id

    def __mul__(self, other):
        """Flexible merge/unmerge with another UUID.

         Non commutative: a * b != b * a
         Invertible: (a * b) * b.inv = a
                     a.inv * (a * b) = b
         Associative: (a * b) * c = a * (b * c)
         """
        return UUID(pmatmult(self.matrix, other.matrix))

    def __add__(self, other):
        """Alias meaning a bounded merge with another UUID.

         Non commutative: a + b != b + a
         Invertible: (a + b) - b = a
         Associative: (a + b) + c = a + (b + c)
         """
        return UUID(pmatmult(self.matrix, other.matrix))

    def __sub__(self, other):
        """Bounded unmerge from last merged UUID."""
        if self.matrix == self.null_matrix:
            raise Exception(f'Cannot subtract from UUID={self.null_pretty}!')
        return UUID(pmatmult(self.matrix, other.inv.matrix))

    def __str__(self):
        return self.id()

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
                return obj.id
            elif not isinstance(
                    obj, (list, set, str, int, float, bytearray, bool)):
                return obj.jsonable

        return JSONEncoder.default(self, obj)




def pmatmult(a, b):
    """Multiply two permutation matrices 35x35.
     a,b: lists of positive integers and zero."""
    return [b[-row - 1] for row in a]


def transpose(m):
    """Transpose a permutation matrix 35x35.
     m: list of positive integers and zero.

     https://codereview.stackexchange.com/questions/241511/how-to-efficiently-fast-calculate-the-transpose-of-a-permutation-matrix-in-p/241524?noredirect=1#comment473994_241524
     """
    n = len(m)
    tr_ls = [0] * n

    for l in m:
        tr_ls[n - 1 - m[l]] = n - 1 - l

    return tr_ls


def print_binmatrix(m):
    """Print a permutation matrix 35x35.
     m: list of positive integers and zero."""

    for row in m:
        print(' '.join(format(2 ** row, '035b')), row)


def pmatrix2int(m):
    """Convert permutation matrix 35x35 to number."""
    return fac2int(pmatrix2fac(m))


def int2pmatrix(big_number):
    """Convert number to permutation matrix."""
    return fac2pmatrix((int2fac(big_number)))


def pmatrix2fac(matrix):
    """Convert permutation matrix to factoradic number."""
    available = list(range(len(matrix)))
    digits = []
    for row in matrix:
        idx = available.index(row)
        del available[idx]
        digits.append(idx)
    return list(reversed(digits))


def fac2pmatrix(digits):
    """Convert factoradic number to permutation matrix."""
    available = list(range(len(digits)))
    mat = []
    for digit in reversed(digits):
        # print(digit, available)
        mat.append(available.pop(digit))
    return mat


def int2fac(number):
    """Convert decimal into factorial numeric system. Left-most is LSB."""
    i = 2
    res = [0]
    while number > 0:
        number, r = divmod(number, i)
        res.append(r)
        i += 1
    return res


def fac2int(digits):
    """Convert factorial numeric system into decimal. Left-most is LSB."""
    radix = 1
    i = 1
    res = 0
    for digit in digits[1:]:
        res += digit * i
        i *= radix
        radix += 1
    return res


from functools import partial
from timeit import timeit
from math import factorial, log10, log2

#
# a = int2pmatrix(factorial(35) // 76672341)
b = int2pmatrix(factorial(35) // 348765)
print_binmatrix(b)
print()
print_binmatrix(transpose(b))
print()
print_binmatrix(transpose(transpose(b)))
print()

#
# print(timeit(partial(permmult, a, b), number=10000) / 10, 'ms')
# print(timeit(partial(transpose, b), number=10000) / 10, 'ms')
# print(timeit(partial(pmatrix2int, a), number=10000) / 10, 'ms')
# print(timeit(partial(
#     int2pmatrix, 89928374983467987
# ), number=10000) / 10, 'ms')


a = UUID(int2pmatrix(2 ** 128 - 1))
b = UUID('1234567890123456789')
c = UUID(0)
print(a, b, c)
print()
print((a * b))
print((a * b) * b)
print((a * b) * b.inv())
print((a * b) * c)


fac = int2fac(2 ** 128 + 3214134)

# s = set()
# r = set()
# aa = bb = 0
# for i in range(1000000):
#     while aa in r:
#         aa = round(random() * 2 ** 128)
#     while bb in r:
#         bb = round(random() * 2 ** 128)
#     r.add(aa)
#     r.add(bb)
#     a = int2pmatrix(0*aa)
#     b = int2pmatrix(bb)
#     n = pmatrix2int(pmatmult(a, b))
#     s.add(n)
#     if i > len(s) - 1:
#         print(i, a, b, n)
#         break

# def f():
#     return pmatrix2int(int2pmatrix(2 ** 128 + 234324234))
#
#
# print(timeit(f, number=1000000), 'us')

def f():
    a = UUID(int2pmatrix(2 ** 128 - 1))
    b = UUID('1234567890123456789')
    (a * b) * b.inv()

# print(pmatrix2int(int2pmatrix(1212000002222235554)))

print(timeit(f, number=10000) * 100, 'us')
