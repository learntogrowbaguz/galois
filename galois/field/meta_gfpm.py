import numba
import numpy as np

from ..dtypes import DTYPES
from .meta import FieldMeta

CHARACTERISTIC = None  # The prime characteristic `p` of the Galois field
DEGREE = None  # The prime power `m` of the Galois field
ORDER = None  # The field's order `p^m`
IRREDUCIBLE_POLY = None  # The field's primitive polynomial in integer form
PRIMITIVE_ELEMENT = None  # The field's primitive element in integer form

INT_TO_POLY_JIT = lambda x: [0]
POLY_TO_INT_JIT = lambda vec: 0

MULTIPLY_UFUNC = lambda x, y: x * y
RECIPROCAL_UFUNC = lambda x: 1 / x


class GFpmMeta(FieldMeta):
    """
    An abstract base class for all :math:`\\mathrm{GF}(2^m)` field array classes.
    """
    # pylint: disable=no-value-for-parameter

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        cls._irreducible_poly_coeffs = np.array(cls._irreducible_poly.coeffs, dtype=cls.dtypes[-1])
        cls._prime_subfield = kwargs["prime_subfield"]

        cls.compile(kwargs["mode"], kwargs["target"])

        # Determine if the irreducible polynomial is primitive
        cls._is_primitive_poly = cls._irreducible_poly(cls.primitive_element, field=cls) == 0

    @property
    def dtypes(cls):
        max_dtype = DTYPES[-1]
        d = [dtype for dtype in DTYPES if np.iinfo(dtype).max >= cls.order - 1 and np.iinfo(max_dtype).max >= (cls.order - 1)**2]
        if len(d) == 0:
            d = [np.object_]
        return d

    def _compile_ufuncs(cls):
        super()._compile_ufuncs()

        if cls.ufunc_mode == "jit-calculate":
            global CHARACTERISTIC, DEGREE
            CHARACTERISTIC = cls.characteristic
            DEGREE = cls.degree
            cls._INT_TO_POLY_JIT = numba.jit("int64[:](int64)", nopython=True)(_int_to_poly)
            cls._POLY_TO_INT_JIT = numba.jit("int64(int64[:])", nopython=True)(_poly_to_int)

    ###############################################################################
    # Compile general-purpose calculate functions
    ###############################################################################

    def _compile_add_calculate(cls):
        global CHARACTERISTIC, INT_TO_POLY_JIT, POLY_TO_INT_JIT
        CHARACTERISTIC = cls.characteristic
        INT_TO_POLY_JIT = cls._INT_TO_POLY_JIT
        POLY_TO_INT_JIT = cls._POLY_TO_INT_JIT
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64, int64)"], **kwargs)(_add_calculate)

    def _compile_negative_calculate(cls):
        global CHARACTERISTIC, INT_TO_POLY_JIT, POLY_TO_INT_JIT
        CHARACTERISTIC = cls.characteristic
        INT_TO_POLY_JIT = cls._INT_TO_POLY_JIT
        POLY_TO_INT_JIT = cls._POLY_TO_INT_JIT
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64)"], **kwargs)(_negative_calculate)

    def _compile_subtract_calculate(cls):
        global CHARACTERISTIC, INT_TO_POLY_JIT, POLY_TO_INT_JIT
        CHARACTERISTIC = cls.characteristic
        INT_TO_POLY_JIT = cls._INT_TO_POLY_JIT
        POLY_TO_INT_JIT = cls._POLY_TO_INT_JIT
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64, int64)"], **kwargs)(_subtract_calculate)

    def _compile_multiply_calculate(cls):
        global CHARACTERISTIC, DEGREE, IRREDUCIBLE_POLY, INT_TO_POLY_JIT, POLY_TO_INT_JIT
        CHARACTERISTIC = cls.characteristic
        DEGREE = cls.degree
        IRREDUCIBLE_POLY = cls._irreducible_poly.coeffs.view(np.ndarray)
        INT_TO_POLY_JIT = cls._INT_TO_POLY_JIT
        POLY_TO_INT_JIT = cls._POLY_TO_INT_JIT
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64, int64)"], **kwargs)(_multiply_calculate)

    def _compile_reciprocal_calculate(cls):
        global ORDER, MULTIPLY_UFUNC
        ORDER = cls.order
        MULTIPLY_UFUNC = cls._ufunc_multiply()
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64)"], **kwargs)(_reciprocal_calculate)

    def _compile_divide_calculate(cls):
        global MULTIPLY_UFUNC, RECIPROCAL_UFUNC
        MULTIPLY_UFUNC = cls._ufunc_multiply()
        RECIPROCAL_UFUNC = cls._ufunc_reciprocal()
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64, int64)"], **kwargs)(_divide_calculate)

    def _compile_power_calculate(cls):
        global MULTIPLY_UFUNC, RECIPROCAL_UFUNC
        MULTIPLY_UFUNC = cls._ufunc_multiply()
        RECIPROCAL_UFUNC = cls._ufunc_reciprocal()
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64, int64)"], **kwargs)(_power_calculate)

    def _compile_log_calculate(cls):
        global ORDER, PRIMITIVE_ELEMENT, MULTIPLY_UFUNC
        ORDER = cls.order
        PRIMITIVE_ELEMENT = int(cls.primitive_element)
        MULTIPLY_UFUNC = cls._ufunc_multiply()
        kwargs = {"nopython": True, "target": cls.ufunc_target} if cls.ufunc_target != "cuda" else {"target": cls.ufunc_target}
        return numba.vectorize(["int64(int64)"], **kwargs)(_log_calculate)

    ###############################################################################
    # Ufunc routines
    ###############################################################################

    def _convert_inputs_to_vector(cls, inputs, kwargs):
        v_inputs = list(inputs)
        for i in range(len(inputs)):
            if issubclass(type(inputs[i]), cls):
                v_inputs[i] = inputs[i].vector()

        # View all output arrays as np.ndarray to avoid infinite recursion
        if "out" in kwargs:
            outputs = kwargs["out"]
            v_outputs = []
            for output in outputs:
                if issubclass(type(output), cls):
                    o = output.vector()
                else:
                    o = output
                v_outputs.append(o)
            kwargs["out"] = tuple(v_outputs)

        return v_inputs, kwargs

    def _convert_output_from_vector(cls, output, field, dtype):  # pylint: disable=no-self-use
        if output is None:
            return None
        else:
            return field.Vector(output, dtype=dtype)

    def _ufunc_routine_add(cls, ufunc, method, inputs, kwargs, meta):
        if cls.ufunc_mode == "jit-lookup" or method != "__call__":
            # Use the lookup ufunc on each array entry
            return super()._ufunc_routine_add(ufunc, method, inputs, kwargs, meta)
        else:
            # Convert entire array to polynomial/vector representation, perform array operation in GF(p), and convert back to GF(p^m)
            cls._verify_operands_in_same_field(ufunc, inputs, meta)
            inputs, kwargs = cls._convert_inputs_to_vector(inputs, kwargs)
            output = getattr(ufunc, method)(*inputs, **kwargs)
            output = cls._convert_output_from_vector(output, meta["field"], meta["dtype"])
            return output

    def _ufunc_routine_negative(cls, ufunc, method, inputs, kwargs, meta):
        if cls.ufunc_mode == "jit-lookup" or method != "__call__":
            # Use the lookup ufunc on each array entry
            return super()._ufunc_routine_negative(ufunc, method, inputs, kwargs, meta)
        else:
            # Convert entire array to polynomial/vector representation and perform array operation in GF(p)
            cls._verify_operands_in_same_field(ufunc, inputs, meta)
            inputs, kwargs = cls._convert_inputs_to_vector(inputs, kwargs)
            output = getattr(ufunc, method)(*inputs, **kwargs)
            output = cls._convert_output_from_vector(output, meta["field"], meta["dtype"])
            return output

    def _ufunc_routine_subtract(cls, ufunc, method, inputs, kwargs, meta):
        if cls.ufunc_mode == "jit-lookup" or method != "__call__":
            # Use the lookup ufunc on each array entry
            return super()._ufunc_routine_subtract(ufunc, method, inputs, kwargs, meta)
        else:
            # Convert entire array to polynomial/vector representation, perform array operation in GF(p), and convert back to GF(p^m)
            cls._verify_operands_in_same_field(ufunc, inputs, meta)
            inputs, kwargs = cls._convert_inputs_to_vector(inputs, kwargs)
            output = getattr(ufunc, method)(*inputs, **kwargs)
            output = cls._convert_output_from_vector(output, meta["field"], meta["dtype"])
            return output

    ###############################################################################
    # GF(p^m) arithmetic in pure python
    ###############################################################################

    def _int_to_poly(cls, a):
        a_vec = np.zeros(cls.degree, dtype=cls.dtypes[-1])
        for i in range(0, cls.degree):
            q = a // cls.characteristic**(cls.degree - 1 - i)
            a -= q*cls.characteristic**(cls.degree - 1 - i)
            a_vec[i] = q
        return a_vec

    def _poly_to_int(cls, a_vec):
        a = 0
        for i in range(0, cls.degree):
            a += a_vec[i]*cls.characteristic**(cls.degree - 1 - i)
        return a

    def _add_python(cls, a, b):
        a_vec = cls._int_to_poly(a)
        b_vec = cls._int_to_poly(b)
        c_vec = (a_vec + b_vec) % cls.characteristic
        return cls._poly_to_int(c_vec)

    def _negative_python(cls, a):
        a_vec = cls._int_to_poly(a)
        c_vec = (-a_vec) % cls.characteristic
        return cls._poly_to_int(c_vec)

    def _subtract_python(cls, a, b):
        a_vec = cls._int_to_poly(a)
        b_vec = cls._int_to_poly(b)
        c_vec = (a_vec - b_vec) % cls.characteristic
        return cls._poly_to_int(c_vec)

    def _multiply_python(cls, a, b):
        a_vec = cls._int_to_poly(a)
        b_vec = cls._int_to_poly(b)

        c_vec = np.zeros(cls.degree, dtype=cls.dtypes[-1])
        for _ in range(cls.degree):
            if b_vec[-1] > 0:
                c_vec = (c_vec + b_vec[-1]*a_vec) % cls.characteristic

            # Multiply a(x) by x
            q = a_vec[0]  # Don't need to divide by the leading coefficient of p(x) because it must be 1
            a_vec[:-1] = a_vec[1:]
            a_vec[-1] = 0

            # Reduce a(x) modulo the irreducible polynomial p(x)
            if q > 0:
                a_vec = (a_vec - q*cls._irreducible_poly_coeffs[1:]) % cls.characteristic

            # Divide b(x) by x
            b_vec[1:] = b_vec[:-1]
            b_vec[0] = 0

        return cls._poly_to_int(c_vec)

    def _reciprocal_python(cls, a):
        """
        TODO: Replace this with more efficient algorithm

        From Fermat's Little Theorem:
        a^(p^m - 1) = 1 (mod p^m), for a in GF(p^m)

        a * a^-1 = 1
        a * a^-1 = a^(p^m - 1)
            a^-1 = a^(p^m - 2)
        """
        if a == 0:
            raise ZeroDivisionError("Cannot compute the multiplicative inverse of 0 in a Galois field.")

        power = cls.order - 2
        result_s = a  # The "squaring" part
        result_m = 1  # The "multiplicative" part

        while power > 1:
            if power % 2 == 0:
                result_s = cls._multiply_python(result_s, result_s)
                power //= 2
            else:
                result_m = cls._multiply_python(result_m, result_s)
                power -= 1

        result = cls._multiply_python(result_m, result_s)

        return result


###############################################################################
# GF(p^m) arithmetic explicitly calculated without lookup tables
###############################################################################

def _int_to_poly(a):
    """
    Convert the integer representation to vector/polynomial representation
    """
    a_vec = np.zeros(DEGREE, dtype=np.int64)
    for i in range(0, DEGREE):
        q = a // CHARACTERISTIC**(DEGREE - 1 - i)
        a -= q*CHARACTERISTIC**(DEGREE - 1 - i)
        a_vec[i] = q
    return a_vec


def _poly_to_int(a_vec):
    """
    Convert the integer representation to vector/polynomial representation
    """
    a = 0
    for i in range(0, DEGREE):
        a += a_vec[i]*CHARACTERISTIC**(DEGREE - 1 - i)
    return a


def _add_calculate(a, b):  # pragma: no cover
    a_vec = INT_TO_POLY_JIT(a)
    b_vec = INT_TO_POLY_JIT(b)
    c_vec = (a_vec + b_vec) % CHARACTERISTIC
    return POLY_TO_INT_JIT(c_vec)


def _negative_calculate(a):  # pragma: no cover
    a_vec = INT_TO_POLY_JIT(a)
    a_vec = (-a_vec) % CHARACTERISTIC
    return POLY_TO_INT_JIT(a_vec)


def _subtract_calculate(a, b):  # pragma: no cover
    a_vec = INT_TO_POLY_JIT(a)
    b_vec = INT_TO_POLY_JIT(b)
    c_vec = (a_vec - b_vec) % CHARACTERISTIC
    return POLY_TO_INT_JIT(c_vec)


def _multiply_calculate(a, b):  # pragma: no cover
    a_vec = INT_TO_POLY_JIT(a)
    b_vec = INT_TO_POLY_JIT(b)

    c_vec = np.zeros(DEGREE, dtype=np.int64)
    for _ in range(DEGREE):
        if b_vec[-1] > 0:
            c_vec = (c_vec + b_vec[-1]*a_vec) % CHARACTERISTIC

        # Multiply a(x) by x
        q = a_vec[0]
        a_vec[:-1] = a_vec[1:]
        a_vec[-1] = 0

        # Reduce a(x) modulo the irreducible polynomial
        if q > 0:
            a_vec = (a_vec - q*IRREDUCIBLE_POLY[1:]) % CHARACTERISTIC

        # Divide b(x) by x
        b_vec[1:] = b_vec[:-1]
        b_vec[0] = 0

    return POLY_TO_INT_JIT(c_vec)


def _reciprocal_calculate(a):  # pragma: no cover
    """
    TODO: Replace this with a more efficient algorithm

    From Fermat's Little Theorem:
    a^(p^m - 1) = 1, for a in GF(p^m)

    a * a^-1 = 1
    a * a^-1 = a^(p^m - 1)
        a^-1 = a^(p^m - 2)
    """
    if a == 0:
        raise ZeroDivisionError("Cannot compute the multiplicative inverse of 0 in a Galois field.")

    power = ORDER - 2
    result_s = a  # The "squaring" part
    result_m = 1  # The "multiplicative" part

    while power > 1:
        if power % 2 == 0:
            result_s = MULTIPLY_UFUNC(result_s, result_s)
            power //= 2
        else:
            result_m = MULTIPLY_UFUNC(result_m, result_s)
            power -= 1

    result = MULTIPLY_UFUNC(result_m, result_s)

    return result


def _divide_calculate(a, b):  # pragma: no cover
    if b == 0:
        raise ZeroDivisionError("Cannot compute the multiplicative inverse of 0 in a Galois field.")

    if a == 0:
        return 0
    else:
        b_inv = RECIPROCAL_UFUNC(b)
        return MULTIPLY_UFUNC(a, b_inv)


def _power_calculate(a, power):  # pragma: no cover
    """
    Square and Multiply Algorithm

    a^13 = (1) * (a)^13
         = (a) * (a)^12
         = (a) * (a^2)^6
         = (a) * (a^4)^3
         = (a * a^4) * (a^4)^2
         = (a * a^4) * (a^8)
         = result_m * result_s
    """
    if a == 0 and power < 0:
        raise ZeroDivisionError("Cannot compute the multiplicative inverse of 0 in a Galois field.")

    if power == 0:
        return 1
    elif power < 0:
        a = RECIPROCAL_UFUNC(a)
        power = abs(power)

    result_s = a  # The "squaring" part
    result_m = 1  # The "multiplicative" part

    while power > 1:
        if power % 2 == 0:
            result_s = MULTIPLY_UFUNC(result_s, result_s)
            power //= 2
        else:
            result_m = MULTIPLY_UFUNC(result_m, result_s)
            power -= 1

    result = MULTIPLY_UFUNC(result_m, result_s)

    return result


def _log_calculate(beta):  # pragma: no cover
    """
    TODO: Replace this with more efficient algorithm

    alpha in GF(p^m) and generates field
    beta in GF(p^m)

    gamma = log_primitive_element(beta), such that: alpha^gamma = beta
    """
    if beta == 0:
        raise ArithmeticError("Cannot compute the discrete logarithm of 0 in a Galois field.")

    # Naive algorithm
    result = 1
    for i in range(0, ORDER - 1):
        if result == beta:
            break
        result = MULTIPLY_UFUNC(result, PRIMITIVE_ELEMENT)

    return i
