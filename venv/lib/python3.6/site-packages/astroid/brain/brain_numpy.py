# Copyright (c) 2015-2016, 2018 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2016 Ceridwen <ceridwenv@gmail.com>
# Copyright (c) 2017-2018 hippo91 <guillaume.peillex@gmail.com>

# Licensed under the LGPL: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
# For details: https://github.com/PyCQA/astroid/blob/master/COPYING.LESSER


"""Astroid hooks for numpy."""

import astroid


def numpy_random_mtrand_transform():
    return astroid.parse('''
    def beta(a, b, size=None): pass
    def binomial(n, p, size=None): pass
    def bytes(length): pass
    def chisquare(df, size=None): pass
    def choice(a, size=None, replace=True, p=None): pass
    def dirichlet(alpha, size=None): pass
    def exponential(scale=1.0, size=None): pass
    def f(dfnum, dfden, size=None): pass
    def gamma(shape, scale=1.0, size=None): pass
    def geometric(p, size=None): pass
    def get_state(): pass
    def gumbel(loc=0.0, scale=1.0, size=None): pass
    def hypergeometric(ngood, nbad, nsample, size=None): pass
    def laplace(loc=0.0, scale=1.0, size=None): pass
    def logistic(loc=0.0, scale=1.0, size=None): pass
    def lognormal(mean=0.0, sigma=1.0, size=None): pass
    def logseries(p, size=None): pass
    def multinomial(n, pvals, size=None): pass
    def multivariate_normal(mean, cov, size=None): pass
    def negative_binomial(n, p, size=None): pass
    def noncentral_chisquare(df, nonc, size=None): pass
    def noncentral_f(dfnum, dfden, nonc, size=None): pass
    def normal(loc=0.0, scale=1.0, size=None): pass
    def pareto(a, size=None): pass
    def permutation(x): pass
    def poisson(lam=1.0, size=None): pass
    def power(a, size=None): pass
    def rand(*args): pass
    def randint(low, high=None, size=None, dtype='l'): pass
    def randn(*args): pass
    def random_integers(low, high=None, size=None): pass
    def random_sample(size=None): pass
    def rayleigh(scale=1.0, size=None): pass
    def seed(seed=None): pass
    def set_state(state): pass
    def shuffle(x): pass
    def standard_cauchy(size=None): pass
    def standard_exponential(size=None): pass
    def standard_gamma(shape, size=None): pass
    def standard_normal(size=None): pass
    def standard_t(df, size=None): pass
    def triangular(left, mode, right, size=None): pass
    def uniform(low=0.0, high=1.0, size=None): pass
    def vonmises(mu, kappa, size=None): pass
    def wald(mean, scale, size=None): pass
    def weibull(a, size=None): pass
    def zipf(a, size=None): pass
    ''')


def numpy_core_umath_transform():
    ufunc_optional_keyword_arguments = ("""out=None, where=True, casting='same_kind', order='K', """
                                        """dtype=None, subok=True""")
    return astroid.parse('''
    # Constants
    e = 2.718281828459045
    euler_gamma = 0.5772156649015329

    # No arg functions
    def geterrobj(): pass

    # One arg functions
    def seterrobj(errobj): pass

    # One arg functions with optional kwargs
    def arccos(x, {opt_args:s}): pass
    def arccosh(x, {opt_args:s}): pass
    def arcsin(x, {opt_args:s}): pass
    def arcsinh(x, {opt_args:s}): pass
    def arctan(x, {opt_args:s}): pass
    def arctanh(x, {opt_args:s}): pass
    def cbrt(x, {opt_args:s}): pass
    def conj(x, {opt_args:s}): pass
    def conjugate(x, {opt_args:s}): pass
    def cosh(x, {opt_args:s}): pass
    def deg2rad(x, {opt_args:s}): pass
    def degrees(x, {opt_args:s}): pass
    def exp2(x, {opt_args:s}): pass
    def expm1(x, {opt_args:s}): pass
    def fabs(x, {opt_args:s}): pass
    def frexp(x, {opt_args:s}): pass
    def isfinite(x, {opt_args:s}): pass
    def isinf(x, {opt_args:s}): pass
    def log(x, {opt_args:s}): pass
    def log1p(x, {opt_args:s}): pass
    def log2(x, {opt_args:s}): pass
    def logical_not(x, {opt_args:s}): pass
    def modf(x, {opt_args:s}): pass
    def negative(x, {opt_args:s}): pass
    def rad2deg(x, {opt_args:s}): pass
    def radians(x, {opt_args:s}): pass
    def reciprocal(x, {opt_args:s}): pass
    def rint(x, {opt_args:s}): pass
    def sign(x, {opt_args:s}): pass
    def signbit(x, {opt_args:s}): pass
    def sinh(x, {opt_args:s}): pass
    def spacing(x, {opt_args:s}): pass
    def square(x, {opt_args:s}): pass
    def tan(x, {opt_args:s}): pass
    def tanh(x, {opt_args:s}): pass
    def trunc(x, {opt_args:s}): pass
    
    # Two args functions with optional kwargs
    def bitwise_and(x1, x2, {opt_args:s}): pass
    def bitwise_or(x1, x2, {opt_args:s}): pass
    def bitwise_xor(x1, x2, {opt_args:s}): pass
    def copysign(x1, x2, {opt_args:s}): pass
    def divide(x1, x2, {opt_args:s}): pass
    def equal(x1, x2, {opt_args:s}): pass
    def float_power(x1, x2, {opt_args:s}): pass
    def floor_divide(x1, x2, {opt_args:s}): pass
    def fmax(x1, x2, {opt_args:s}): pass
    def fmin(x1, x2, {opt_args:s}): pass
    def fmod(x1, x2, {opt_args:s}): pass
    def greater(x1, x2, {opt_args:s}): pass
    def hypot(x1, x2, {opt_args:s}): pass
    def ldexp(x1, x2, {opt_args:s}): pass
    def left_shift(x1, x2, {opt_args:s}): pass
    def less(x1, x2, {opt_args:s}): pass
    def logaddexp(x1, x2, {opt_args:s}): pass
    def logaddexp2(x1, x2, {opt_args:s}): pass
    def logical_and(x1, x2, {opt_args:s}): pass
    def logical_or(x1, x2, {opt_args:s}): pass
    def logical_xor(x1, x2, {opt_args:s}): pass
    def maximum(x1, x2, {opt_args:s}): pass
    def minimum(x1, x2, {opt_args:s}): pass
    def nextafter(x1, x2, {opt_args:s}): pass
    def not_equal(x1, x2, {opt_args:s}): pass
    def power(x1, x2, {opt_args:s}): pass
    def remainder(x1, x2, {opt_args:s}): pass
    def right_shift(x1, x2, {opt_args:s}): pass
    def subtract(x1, x2, {opt_args:s}): pass
    def true_divide(x1, x2, {opt_args:s}): pass
    '''.format(opt_args=ufunc_optional_keyword_arguments))


def numpy_core_numerictypes_transform():
    return astroid.parse('''
    # different types defined in numerictypes.py
    class generic(object):
        def __init__(self, value):
            self.T = None
            self.base = None
            self.data = None
            self.dtype = None
            self.flags = None
            self.flat = None
            self.imag = None
            self.itemsize = None
            self.nbytes = None
            self.ndim = None
            self.real = None
            self.size = None
            self.strides = None

        def all(self): pass
        def any(self): pass
        def argmax(self): pass
        def argmin(self): pass
        def argsort(self): pass
        def astype(self): pass
        def base(self): pass
        def byteswap(self): pass
        def choose(self): pass
        def clip(self): pass
        def compress(self): pass
        def conj(self): pass
        def conjugate(self): pass
        def copy(self): pass
        def cumprod(self): pass
        def cumsum(self): pass
        def data(self): pass
        def diagonal(self): pass
        def dtype(self): pass
        def dump(self): pass
        def dumps(self): pass
        def fill(self): pass
        def flags(self): pass
        def flat(self): pass
        def flatten(self): pass
        def getfield(self): pass
        def imag(self): pass
        def item(self): pass
        def itemset(self): pass
        def itemsize(self): pass
        def max(self): pass
        def mean(self): pass
        def min(self): pass
        def nbytes(self): pass
        def ndim(self): pass
        def newbyteorder(self): pass
        def nonzero(self): pass
        def prod(self): pass
        def ptp(self): pass
        def put(self): pass
        def ravel(self): pass
        def real(self): pass
        def repeat(self): pass
        def reshape(self): pass
        def resize(self): pass
        def round(self): pass
        def searchsorted(self): pass
        def setfield(self): pass
        def setflags(self): pass
        def shape(self): pass
        def size(self): pass
        def sort(self): pass
        def squeeze(self): pass
        def std(self): pass
        def strides(self): pass
        def sum(self): pass
        def swapaxes(self): pass
        def take(self): pass
        def tobytes(self): pass
        def tofile(self): pass
        def tolist(self): pass
        def tostring(self): pass
        def trace(self): pass
        def transpose(self): pass
        def var(self): pass
        def view(self): pass


    class dtype(object):
        def __init__(self, obj, align=False, copy=False):
            self.alignment = None
            self.base = None
            self.byteorder = None
            self.char = None
            self.descr = None
            self.fields = None
            self.flags = None
            self.hasobject = None
            self.isalignedstruct = None
            self.isbuiltin = None
            self.isnative = None
            self.itemsize = None
            self.kind = None
            self.metadata = None
            self.name = None
            self.names = None
            self.num = None
            self.shape = None
            self.str = None
            self.subdtype = None
            self.type = None

        def newbyteorder(self, new_order='S'): pass


    class ndarray(object):
        def __init__(self, shape, dtype=float, buffer=None, offset=0,
                     strides=None, order=None):
            self.T = None
            self.base = None
            self.ctypes = None
            self.data = None
            self.dtype = None
            self.flags = None
            self.flat = None
            self.imag = None
            self.itemsize = None
            self.nbytes = None
            self.ndim = None
            self.real = None
            self.shape = None
            self.size = None
            self.strides = None

        def all(self): pass
        def any(self): pass
        def argmax(self): pass
        def argmin(self): pass
        def argpartition(self): pass
        def argsort(self): pass
        def astype(self): pass
        def byteswap(self): pass
        def choose(self): pass
        def clip(self): pass
        def compress(self): pass
        def conj(self): pass
        def conjugate(self): pass
        def copy(self): pass
        def cumprod(self): pass
        def cumsum(self): pass
        def diagonal(self): pass
        def dot(self): pass
        def dump(self): pass
        def dumps(self): pass
        def fill(self): pass
        def flatten(self): pass
        def getfield(self): pass
        def item(self): pass
        def itemset(self): pass
        def max(self): pass
        def mean(self): pass
        def min(self): pass
        def newbyteorder(self): pass
        def nonzero(self): pass
        def partition(self): pass
        def prod(self): pass
        def ptp(self): pass
        def put(self): pass
        def ravel(self): pass
        def repeat(self): pass
        def reshape(self): pass
        def resize(self): pass
        def round(self): pass
        def searchsorted(self): pass
        def setfield(self): pass
        def setflags(self): pass
        def sort(self): pass
        def squeeze(self): pass
        def std(self): pass
        def sum(self): pass
        def swapaxes(self): pass
        def take(self): pass
        def tobytes(self): pass
        def tofile(self): pass
        def tolist(self): pass
        def tostring(self): pass
        def trace(self): pass
        def transpose(self): pass
        def var(self): pass
        def view(self): pass


    class busdaycalendar(object):
        def __init__(self, weekmask='1111100', holidays=None):
            self.holidays = None
            self.weekmask = None

    class flexible(generic): pass
    class bool_(generic): pass
    class number(generic): pass
    class datetime64(generic): pass
   

    class void(flexible):
        def __init__(self, *args, **kwargs):
            self.base = None
            self.dtype = None
            self.flags = None
        def getfield(self): pass
        def setfield(self): pass


    class character(flexible): pass


    class integer(number):
        def __init__(self, value):
           self.denominator = None
           self.numerator = None


    class inexact(number): pass


    class str_(str, character):
        def maketrans(self, x, y=None, z=None): pass

    
    class bytes_(bytes, character):
        def fromhex(self, string): pass
        def maketrans(self, frm, to): pass


    class signedinteger(integer): pass


    class unsignedinteger(integer): pass


    class complexfloating(inexact): pass


    class floating(inexact): pass


    class float64(floating, float):
        def fromhex(self, string): pass 

        
    class uint64(unsignedinteger): pass
    class complex64(complexfloating): pass
    class int16(signedinteger): pass
    class float96(floating): pass
    class int8(signedinteger): pass
    class uint32(unsignedinteger): pass
    class uint8(unsignedinteger): pass
    class _typedict(dict): pass
    class complex192(complexfloating): pass
    class timedelta64(signedinteger): pass
    class int32(signedinteger): pass
    class uint16(unsignedinteger): pass
    class float32(floating): pass
    class complex128(complexfloating, complex): pass
    class float16(floating): pass
    class int64(signedinteger): pass

    buffer_type = memoryview
    bool8 = bool_
    byte = int8
    bytes0 = bytes_
    cdouble = complex128
    cfloat = complex128
    clongdouble = complex192
    clongfloat = complex192
    complex_ = complex128
    csingle = complex64
    double = float64
    float_ = float64
    half = float16
    int0 = int32
    int_ = int32
    intc = int32
    intp = int32
    long = int32
    longcomplex = complex192
    longdouble = float96
    longfloat = float96
    longlong = int64
    object0 = object_
    object_ = object_
    short = int16
    single = float32
    singlecomplex = complex64
    str0 = str_
    string_ = bytes_
    ubyte = uint8
    uint = uint32
    uint0 = uint32
    uintc = uint32
    uintp = uint32
    ulonglong = uint64
    unicode = str_
    unicode_ = str_
    ushort = uint16
    void0 = void
    ''')


def numpy_funcs():
    return astroid.parse('''
    import builtins
    def sum(a, axis=None, dtype=None, out=None, keepdims=None):
        return builtins.sum(a)
    ''')


astroid.register_module_extender(astroid.MANAGER, 'numpy.core.umath', numpy_core_umath_transform)
astroid.register_module_extender(astroid.MANAGER, 'numpy.random.mtrand',
                                 numpy_random_mtrand_transform)
astroid.register_module_extender(astroid.MANAGER, 'numpy.core.numerictypes',
                                 numpy_core_numerictypes_transform)
astroid.register_module_extender(astroid.MANAGER, 'numpy', numpy_funcs)
