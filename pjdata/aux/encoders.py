import hashlib
from json import JSONEncoder

import numpy as np

from pjdata.aux.alphabets import alphabet1224, alphabet1224dic


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
     (20 digits in base-107).
    :param bytes_digest:
    :return: string with 20 digits, padded with '0' when needed
    """
    return int2pretty(bytes2int(bytes_digest))


def int2pretty(number):
    """Convert number to a tiny human-friendly string (20 chars)."""
    return enc(number).rjust(20, '0')


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
    # It didn't help too much to replace list by a dict. 7.8us vs 6.2us
    base = len(alphabet)
    for i, d in enumerate(digest):
        res += alphabet.index(d) * pow(base, last - i)
    return res


def enc(big_number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                             'abcdefghijklmnopqrstuvwxyz'
                             'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """
    Encode an integer to base-n. n = len(alphabet).
    The default is base107 since it is enough to represent MD5 as 18-19 chars.
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
    57 22 # possible to type with an US keyboard
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

    typeable and double-clickable (63)
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz

    :param alphabet: string with allowed digits
    :param big_number: an integer, usually a big MD5-like one
    :return: string representing a base-107 number (or any other base,
    depending on the given alphabet length)"""
    l = len(alphabet)
    res = []
    while True:
        big_number, rem = divmod(big_number, l)
        res.append(alphabet[rem])
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
    """Convert tiny string (20 chars) to bytes."""
    return dec(digest).to_bytes(16, 'big')


def pretty2int(digest, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                'abcdefghijklmnopqrstuvwxyz'
                                'ÁÂÄÅÆÉÊËÍÎÏÐÑÓÔÖÚÛÜÝÞßáâäåæçéêëíîïðñóôöøúûüýþ'):
    """Convert tiny string (20 chars) to bytes."""
    return dec(digest, alphabet)


def prettydigest(bytes_content):
    return digest2pretty(md5digest(bytes_content))


def intlist2bytes(lst):
    """Each int becomes 4 bytes. max=4294967294"""
    return b''.join([n.to_bytes(4, byteorder='big') for n in lst])


def bytes2intlist(bytes_content):
    """Each 4 bytes become an int."""
    n = len(bytes_content)
    return [bytes2int(bytes_content[i:i + 4]) for i in range(0, n, 4)]


def pmatrix2pretty(m, alphabet=alphabet1224):
    """Convert a permutation matrix to a string using the given alphabet.

    The alphabet should have at least |m|² - 1 letters.
    When compared to the straight math conversion, this implementation will
    provide a shorter text (20 vs 18) through a faster conversion (44us vs 5us)
    at the expense of size in bytes (increasing from 20 to ~34 in RAM and from
    20 to 36 in a fixed length CHAR field in a database; latin1 vs utf8).
    In a 1MiB/s network, this would lead to extra 18us,
    still far from ~40us savings.
    """
    # TODO: Create an alphabet for 58x58 (3363 letters).
    side = len(m)
    lst = [alphabet[m[i + 1] + side * m[i]] for i in range(0, side - 1, 2)]
    if side % 2 == 1:
        lst.append(alphabet[m[side - 1]])
    return ''.join(lst)


def pretty2pmatrix(text, side=35, alphabet_dict=alphabet1224dic):
    """See pmatrix2pretty."""
    m = [x for d in text[:-1] for x in divmod(alphabet_dict[d], side)]
    if side % 2 == 1:
        m.append(alphabet_dict[text[-1]])
    return m


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if obj is not None:
            from pjdata.aux.uuid import UUID
            if isinstance(obj, np.ndarray):
                return str(obj)
            elif isinstance(obj, UUID):
                return obj.id
            elif not isinstance(
                    obj, (list, set, str, int, float, bytearray, bool)):
                return obj.jsonable

        return JSONEncoder.default(self, obj)
