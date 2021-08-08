"""
A pytest module to test determination of valid BCH codes.

References
----------
* S. Lin and D. Costello. Error Control Coding. Appendix C, pp. 1231.
* https://link.springer.com/content/pdf/bbm%3A978-1-4899-2174-1%2F1.pdf
"""
import pytest
import numpy as np

import galois


def test_bch_valid_codes_exceptions():
    with pytest.raises(TypeError):
        galois.bch_valid_codes(15.0)
    with pytest.raises(TypeError):
        galois.bch_valid_codes(15, t_min=1.0)

    with pytest.raises(ValueError):
        galois.bch_valid_codes(15, t_min=0)


def test_bch_valid_codes_7():
    codes = [
        (7, 4, 1),
        (7, 1, 3),
    ]
    assert galois.bch_valid_codes(7) == codes


def test_bch_valid_codes_15():
    codes = [
        (15, 11, 1),
        (15, 7, 2),
        (15, 5, 3),
        (15, 1, 7),
    ]
    assert galois.bch_valid_codes(15) == codes


def test_bch_valid_codes_31():
    codes = [
        (31, 26, 1),
        (31, 21, 2),
        (31, 16, 3),
        (31, 11, 5),
        (31, 6, 7),
        (31, 1, 15),
    ]
    assert galois.bch_valid_codes(31) == codes


def test_bch_valid_codes_63():
    codes = [
        (63, 57, 1),
        (63, 51, 2),
        (63, 45, 3),
        (63, 39, 4),
        (63, 36, 5),
        (63, 30, 6),
        (63, 24, 7),
        (63, 18, 10),
        (63, 16, 11),
        (63, 10, 13),
        (63, 7, 15),
        (63, 1, 31),
    ]
    assert galois.bch_valid_codes(63) == codes


def test_bch_valid_codes_127():
    codes = [
        (127, 120, 1),
        (127, 113, 2),
        (127, 106, 3),
        (127, 99, 4),
        (127, 92, 5),
        (127, 85, 6),
        (127, 78, 7),
        (127, 71, 9),
        (127, 64, 10),
        (127, 57, 11),
        (127, 50, 13),
        (127, 43, 14),
        (127, 36, 15),
        (127, 29, 21),
        (127, 22, 23),
        (127, 15, 27),
        (127, 8, 31),
        (127, 1, 63),
    ]
    assert galois.bch_valid_codes(127) == codes


def test_bch_valid_codes_255():
    codes = [
        (255, 247, 1),
        (255, 239, 2),
        (255, 231, 3),
        (255, 223, 4),
        (255, 215, 5),
        (255, 207, 6),
        (255, 199, 7),
        (255, 191, 8),
        (255, 187, 9),
        (255, 179, 10),
        (255, 171, 11),
        (255, 163, 12),
        (255, 155, 13),
        (255, 147, 14),
        (255, 139, 15),
        (255, 131, 18),
        (255, 123, 19),
        (255, 115, 21),
        (255, 107, 22),
        (255, 99, 23),
        (255, 91, 25),
        (255, 87, 26),
        (255, 79, 27),
        (255, 71, 29),
        (255, 63, 30),
        (255, 55, 31),
        (255, 47, 42),
        (255, 45, 43),
        (255, 37, 45),
        (255, 29, 47),
        (255, 21, 55),
        (255, 13, 59),
        (255, 9, 63),
        (255, 1, 127),
    ]
    assert galois.bch_valid_codes(255) == codes


def test_bch_valid_codes_511():
    codes = [
        (511, 502, 1),
        (511, 493, 2),
        (511, 484, 3),
        (511, 475, 4),
        (511, 466, 5),
        (511, 457, 6),
        (511, 448, 7),
        (511, 439, 8),
        (511, 430, 9),
        (511, 421, 10),
        (511, 412, 11),
        (511, 403, 12),
        (511, 394, 13),
        (511, 385, 14),
        (511, 376, 15),
        (511, 367, 17),
        (511, 358, 18),
        (511, 349, 19),
        (511, 340, 20),
        (511, 331, 21),
        (511, 322, 22),
        (511, 313, 23),
        (511, 304, 25),
        (511, 295, 26),
        (511, 286, 27),
        (511, 277, 28),
        (511, 268, 29),
        (511, 259, 30),
        (511, 250, 31),
        (511, 241, 36),
        (511, 238, 37),
        (511, 229, 38),
        (511, 220, 39),
        (511, 211, 41),
        (511, 202, 42),
        (511, 193, 43),
        (511, 184, 45),
        (511, 175, 46),
        (511, 166, 47),
        (511, 157, 51),
        (511, 148, 53),
        (511, 139, 54),
        (511, 130, 55),
        (511, 121, 58),
        (511, 112, 59),
        (511, 103, 61),
        (511, 94, 62),
        (511, 85, 63),
        (511, 76, 85),
        (511, 67, 87),
        (511, 58, 91),
        (511, 49, 93),
        (511, 40, 95),
        (511, 31, 109),
        (511, 28, 111),
        (511, 19, 119),
        (511, 10, 127),
        (511, 1, 255),
    ]
    assert galois.bch_valid_codes(511) == codes
