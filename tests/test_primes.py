"""
A pytest module to test the functions relating to primes.
"""
import random

import pytest
import numpy as np

import galois


def test_primes_exceptions():
    with pytest.raises(TypeError):
        galois.primes(20.0)


def test_primes():
    assert galois.primes(-10) == []
    assert galois.primes(1) == []
    assert galois.primes(2) == [2]
    assert galois.primes(3) == [2, 3]
    assert galois.primes(19) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert galois.primes(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert galois.primes(100) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def test_kth_prime_exceptions():
    with pytest.raises(TypeError):
        galois.kth_prime(20.0)
    with pytest.raises(ValueError):
        galois.kth_prime(0)
    with pytest.raises(ValueError):
        galois.kth_prime(galois._prime.MAX_K + 1)


def test_kth_prime():
    ks = [7236, 6146, 6978, 8416, 4761, 8488, 7095, 741, 5538, 3462, 487, 4121, 94, 735, 9864, 7873, 7294, 8952, 3722, 3390]
    ns = [73243, 61001, 70429, 86539, 45989, 87433, 71671, 5641, 54421, 32297, 3469, 39139, 491, 5569, 103099, 80429, 73897, 92681, 34871, 31511]
    for k, n in zip(ks, ns):
        assert galois.kth_prime(k) == n


def test_prev_prime_exceptions():
    with pytest.raises(TypeError):
        galois.prev_prime(20.0)


def test_prev_prime():
    """
    Sage:
        n = randint(1e20, 1e40)
        p = previous_prime(n)
        print(n, p)
    """
    assert galois.prev_prime(-10) is None
    assert galois.prev_prime(1) is None
    assert galois.prev_prime(2) == 2
    assert galois.prev_prime(8) == 7
    assert galois.prev_prime(11) == 11

    assert galois.prev_prime(6298891201241929548477199440981228280038) == 6298891201241929548477199440981228279991
    assert galois.prev_prime(2245986882959070275565383172237929066361) == 2245986882959070275565383172237929066273
    assert galois.prev_prime(9259519322042859167754950040306622329138) == 9259519322042859167754950040306622328867
    assert galois.prev_prime(8385429707258740720790261449080131360283) == 8385429707258740720790261449080131360143


def test_next_prime_exceptions():
    with pytest.raises(TypeError):
        galois.next_prime(20.0)


def test_next_prime():
    """
    Sage:
        n = randint(1e20, 1e40)
        p = next_prime(n)
        print(n, p)
    """
    assert galois.next_prime(-10) == 2
    assert galois.next_prime(1) == 2
    assert galois.next_prime(2) == 3
    assert galois.next_prime(8) == 11
    assert galois.next_prime(11) == 13

    assert galois.next_prime(6852976918500265458318414454675831645298) == 6852976918500265458318414454675831645343
    assert galois.next_prime(3572414920255490866338499919876578953336) == 3572414920255490866338499919876578953521
    assert galois.next_prime(2586430993484535570784866034349245707842) == 2586430993484535570784866034349245708081
    assert galois.next_prime(5854185879525630749384072249732042426759) == 5854185879525630749384072249732042426801


def test_random_prime_exceptions():
    with pytest.raises(TypeError):
        galois.random_prime(10.0)
    with pytest.raises(ValueError):
        galois.random_prime(0)
    with pytest.raises(ValueError):
        galois.random_prime(-10)


def test_random_prime():
    for _ in range(5):
        bits = random.randint(1, 10)
        n = galois.random_prime(bits)
        assert galois.is_prime(n) == True


def test_mersenne_exponents_exceptions():
    with pytest.raises(TypeError):
        galois.mersenne_exponents(10.0)
    with pytest.raises(ValueError):
        galois.mersenne_exponents(0)
    with pytest.raises(ValueError):
        galois.mersenne_exponents(-10)


def test_mersenne_exponents():
    # https://oeis.org/A000043
    exponents = [2,3,5,7,13,17,19,31,61,89,107,127]  # Up to 128 bits
    assert galois.mersenne_exponents(128) == exponents

    exponents = [2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423,9689,9941,11213,19937,21701,23209,44497,86243,110503,132049,216091,756839,859433,1257787,1398269,2976221,3021377,6972593,13466917,20996011,24036583,25964951,30402457,32582657,37156667,42643801,43112609]
    assert galois.mersenne_exponents() == exponents



def test_mersenne_primes_exceptions():
    with pytest.raises(TypeError):
        galois.mersenne_primes(10.0)
    with pytest.raises(ValueError):
        galois.mersenne_primes(0)
    with pytest.raises(ValueError):
        galois.mersenne_primes(-10)


def test_mersenne_primes():
    # https://oeis.org/A000668
    primes = [3,7,31,127,8191,131071,524287,2147483647,2305843009213693951,618970019642690137449562111,162259276829213363391578010288127,170141183460469231731687303715884105727]  # Up to 128 bits
    assert galois.mersenne_primes(128) == primes


def test_is_prime_exceptions():
    with pytest.raises(TypeError):
        galois.is_prime(13.0)
    with pytest.raises(ValueError):
        galois.is_prime(0)
    with pytest.raises(ValueError):
        galois.is_prime(-13)


def test_is_prime():
    # https://oeis.org/A000040
    primes = np.array([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271])
    n = np.arange(1, primes[-1] + 1)
    is_prime = np.zeros(n.size, dtype=bool)
    is_prime[primes - 1] = True  # -1 for 1-indexed
    assert [galois.is_prime(ni) for ni in n] == is_prime.tolist()


def test_is_composite_exceptions():
    with pytest.raises(TypeError):
        galois.is_composite(13.0)
    with pytest.raises(ValueError):
        galois.is_composite(0)
    with pytest.raises(ValueError):
        galois.is_composite(-13)


def test_is_composite():
    # https://oeis.org/A002808
    composites = np.array([4,6,8,9,10,12,14,15,16,18,20,21,22,24,25,26,27,28,30,32,33,34,35,36,38,39,40,42,44,45,46,48,49,50,51,52,54,55,56,57,58,60,62,63,64,65,66,68,69,70,72,74,75,76,77,78,80,81,82,84,85,86,87,88])
    n = np.arange(1, composites[-1] + 1)
    is_composite = np.zeros(n.size, dtype=bool)
    is_composite[composites - 1] = True  # -1 for 1-indexed
    assert [galois.is_composite(ni) for ni in n] == is_composite.tolist()


def test_fermat_primality_test_exceptions():
    with pytest.raises(TypeError):
        galois.fermat_primality_test(13.0)
    with pytest.raises(TypeError):
        galois.fermat_primality_test(13, a=2.0)
    with pytest.raises(TypeError):
        galois.fermat_primality_test(13, rounds=1.0)

    with pytest.raises(ValueError):
        galois.fermat_primality_test(4)
    with pytest.raises(ValueError):
        galois.fermat_primality_test(1)
    with pytest.raises(ValueError):
        galois.fermat_primality_test(13, a=12)
    with pytest.raises(ValueError):
        galois.fermat_primality_test(13, rounds=0)


def test_fermat_primality_test():
    primes = random.choices(galois.primes(10_000_000), k=10)
    assert [galois.fermat_primality_test(p) for p in primes] == [True,]*len(primes)

    # https://oeis.org/A001567
    pseudoprimes = [341,561,645,1105,1387,1729,1905,2047,2465,2701,2821,3277,4033,4369,4371,4681,5461,6601,7957,8321,8481,8911,10261,10585,11305,12801,13741,13747,13981,14491,15709,15841,16705,18705,18721,19951,23001,23377,25761,29341]
    pseudoprimes = [p for p in pseudoprimes if p % 2 == 1]  # Only test odds
    assert [galois.fermat_primality_test(p, a=2) for p in pseudoprimes] == [True,]*len(pseudoprimes)

    # https://oeis.org/A005935
    pseudoprimes = [91,121,286,671,703,949,1105,1541,1729,1891,2465,2665,2701,2821,3281,3367,3751,4961,5551,6601,7381,8401,8911,10585,11011,12403,14383,15203,15457,15841,16471,16531,18721,19345,23521,24046,24661,24727,28009,29161]
    pseudoprimes = [p for p in pseudoprimes if p % 2 == 1]  # Only test odds
    assert [galois.fermat_primality_test(p, a=3) for p in pseudoprimes] == [True,]*len(pseudoprimes)

    # https://oeis.org/A005936
    pseudoprimes = [4,124,217,561,781,1541,1729,1891,2821,4123,5461,5611,5662,5731,6601,7449,7813,8029,8911,9881,11041,11476,12801,13021,13333,13981,14981,15751,15841,16297,17767,21361,22791,23653,24211,25327,25351,29341,29539]
    pseudoprimes = [p for p in pseudoprimes if p % 2 == 1]  # Only test odds
    assert [galois.fermat_primality_test(p, a=5) for p in pseudoprimes] == [True,]*len(pseudoprimes)


def test_miller_rabin_primality_test_exceptions():
    with pytest.raises(TypeError):
        galois.miller_rabin_primality_test(13.0)
    with pytest.raises(TypeError):
        galois.miller_rabin_primality_test(13, a=2.0)
    with pytest.raises(TypeError):
        galois.miller_rabin_primality_test(13, rounds=1.0)

    with pytest.raises(ValueError):
        galois.miller_rabin_primality_test(4)
    with pytest.raises(ValueError):
        galois.miller_rabin_primality_test(1)
    with pytest.raises(ValueError):
        galois.miller_rabin_primality_test(13, a=12)
    with pytest.raises(ValueError):
        galois.miller_rabin_primality_test(13, rounds=0)


def test_miller_rabin_primality_test():
    primes = random.choices(galois.primes(10_000_000), k=10)
    assert [galois.miller_rabin_primality_test(p) for p in primes] == [True,]*len(primes)

    strong_liars = [9,10,12,16,17,22,29,38,53,62,69,74,75,79,81,82]
    witnesses = [a for a in range(2, 90) if a not in strong_liars]
    assert [galois.miller_rabin_primality_test(91, a=a) for a in strong_liars] == [True,]*len(strong_liars)
    assert [galois.miller_rabin_primality_test(91, a=a) for a in witnesses] == [False,]*len(witnesses)

    # 105 has no strong liars
    witnesses = [a for a in range(2, 104)]
    assert [galois.miller_rabin_primality_test(105, a=a) for a in witnesses] == [False,]*len(witnesses)

    # https://oeis.org/A001262
    pseudoprimes = [2047,3277,4033,4681,8321,15841,29341,42799,49141,52633,65281,74665,80581,85489,88357,90751,104653,130561,196093,220729,233017,252601,253241,256999,271951,280601,314821,357761,390937,458989,476971,486737]
    assert [galois.miller_rabin_primality_test(p, a=2) for p in pseudoprimes] == [True,]*len(pseudoprimes)
    assert [galois.miller_rabin_primality_test(p, a=3) for p in pseudoprimes] == [False,]*len(pseudoprimes)
