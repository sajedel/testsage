r"""
Functions that compute some of the sequences in Sloane's tables

EXAMPLES:
   Type sloane.[tab] to see a list of the sequences that are defined.
   sage: d = sloane.A000005; d
    The integer sequence tau(n), which is the number of divisors of n.
    sage: d(1)
    1
    sage: d(6)
    4
    sage: d(100)
    9

Type \code{d._eval??} to see how the function that computes an individual
term of the sequence is implemented.

The input must be a positive integer:
    sage: d(0)
    Traceback (most recent call last):
    ...
    ValueError: input n (=0) must be a positive integer
    sage: d(1/3)
    Traceback (most recent call last):
    ...
    TypeError: Unable to coerce rational (=1/3) to an Integer.

You can also change how a sequence prints:
    sage: d = sloane.A000005; d
    The integer sequence tau(n), which is the number of divisors of n.
    sage: d.rename('(..., tau(n), ...)')
    sage: d
    (..., tau(n), ...)
    sage: d.reset_name()
    sage: d
    The integer sequence tau(n), which is the number of divisors of n.
"""

########################################################################
#
# To add your own new sequence here, do the following:
#
# 1. Add a new class to Section II below, which you should
#    do by copying an existing class and modifying it.
#    Make sure to at least define _eval and _repr_.
#    NOTES:  (a) define the _eval method only, which you may
#                assume has as input a *positive* SAGE integer.
#            (b) define the list method if there is a faster
#                way to compute the terms of the sequence than
#                just calling _eval (which is the default definition
#                of list).
#            (c) *AVOID* using gp.method if possible!  Use pari(obj).method()
#            (d) In many cases the function that computes a given integer
#                sequence belongs elsewhere in SAGE.  Put it there and make
#                your class in this file just call it.
#            (e) _eval should always return a SAGE integer.
#
# 2. Add an instance of your class in Section III below.
#
# 3. Type "sage -br" to rebuild SAGE, then fire up the notebook and
#    try out your new sequence.  Click the text button to get a version
#    of your session that you then include as a docstring.
#    You can check your results with the entries of the OEIS:
#       sage: seq = sloane_sequence(45)
#       Searching Sloane's online database...
#       sage: print seq[1]
#       Fibonacci numbers: F(n) = F(n-1) + F(n-2), F(0) = 0, F(1) = 1, F(2) = 1, ...
#       sage: seq[2][:12]
#       [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
#
# 4. Send a patch using
#      sage: hg_sage.ci()
#      sage: hg_sage.send('patchname')
#    (Email it to sage-dev@groups.google.com or post it online.)
#
########################################################################

########################################################################
# I. Define the generic Sloane sequence class.
########################################################################

# just used for handy .load, .save, etc.
from sage.structure.sage_object import SageObject
from sage.misc.misc import srange

class SloaneSequence(SageObject):
    def _repr_(self):
        raise NotImplementedError

    def __getitem__(self, n):
        return self(n)

    def __call__(self, n):
        m = Integer(n)
        if m <= 0:
            raise ValueError, "input n (=%s) must be a positive integer"%n
        return self._eval(m)

    def _eval(self, n):
        # this is what you implement in the derived class
        # the input n is assumed to be a *SAGE* integer >= 1
        raise NotImplementedError

    def list(self, n):
        return [self._eval(i) for i in srange(Integer(1),n+1)]

########################################################################
# II. Actual implementations of Sloane sequences.
########################################################################

# You may have to import more here when defining new sequences
import sage.rings.arith as arith
from sage.rings.integer import Integer

class A000005(SloaneSequence):
    r"""
    The sequence $tau(n)$, which is the number of divisors of $n$.

    This sequence is also denoted $d(n)$ (also called $\tau(n)$ or
    $\sigma_0(n)$), the number of divisors of n.

    EXAMPLES:
        sage: d = sloane.A000005; d
        The integer sequence tau(n), which is the number of divisors of n.
        sage: d(1)
        1
        sage: d(6)
        4
        sage: d(51)
        4
        sage: d(100)
        9
        sage: d(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: d.list(10)
        [1, 2, 2, 3, 2, 4, 2, 4, 3, 4]

    AUTHOR:
        -- Jaap Spies (2006-12-10)
        -- William Stein (2007-01-08)
    """
    def _repr_(self):
        return "The integer sequence tau(n), which is the number of divisors of n."

    def _eval(self, n):
        return arith.number_of_divisors(n)

    def list(self, n):
        return [self(i) for i in range(1,n+1)]

class A000010(SloaneSequence):
    r"""
    The integer sequence A000010 is Euler's totient function.

    Number of positive integers $i < n$ that are relative prime to $n$.
    Number of totatives of $n$.

    Euler totient function $\phi(n)$: count numbers < $n$ and prime to $n$.
    euler_phi is a standard SAGE function implemented in PARI

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000010; a
        Euler's totient function
        sage: a(1)
        1
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(11)
        10
        sage: a.list(12)
        [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: Unable to coerce rational (=1/3) to an Integer.

    AUTHOR:
        -- Jaap Spies (2007-01-12)
    """
    def _repr_(self):
        return "Euler's totient function"

    def _eval(self, n):
        return arith.euler_phi(n)

    def list(self, n):
        return [self(i) for i in range(1,n+1)]

class A000045(SloaneSequence):
    r"""
    Sequence of Fibonacci numbers, offset 0,4.

    REFERENCES: S. Plouffe, Project Gutenberg,
    The First 1001 Fibonacci Numbers,
    \url{http://ibiblio.org/pub/docs/books/gutenberg/etext01/fbncc10.txt}
    We have one more. Our first Fibonacci number is 0.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000045; a
        Fibonacci number with index n >= 0
        sage: a(1)
        1
        sage: a(0)
        0
        sage: a.list(12)
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: Unable to coerce rational (=1/3) to an Integer.

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        self._b = []

    def _repr_(self):
        return "Fibonacci number with index n >= 0"

    def __call__(self, n):
        m = Integer(n)
        if m < 0:
            raise ValueError, "input n (=%s) must be a non-negative integer"%n
        return self._eval(m)

    def _precompute(self, how_many=500):
        try:
            f = self._f
        except AttributeError:
            self._f = self.fib()
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def fib(self):
        """
        Returns a generator over all Fibanacci numbers, starting with 0.
        """
        x, y = Integer(0), Integer(1)
        yield x
        while True:
            x, y = y, x+y
            yield x

    offset = 0

    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A000203(SloaneSequence):
    r"""
    The sequence $\sigma(n)$, where $\sigma(n)$ is the sum of the
    divisors of $n$.   Also called $\sigma_1(n)$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000203; a
        sigma(n) = sum of divisors of n. Also called sigma_1(n).
        sage: a(1)
        1
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(256)
        511
        sage: a.list(12)
        [1, 3, 4, 7, 6, 12, 8, 15, 13, 18, 12, 28]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: Unable to coerce rational (=1/3) to an Integer.

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """

    def _repr_(self):
        return "sigma(n) = sum of divisors of n. Also called sigma_1(n)."

    offset = 1

    def _eval(self, n):
        return sum(arith.divisors(n))

    def list(self, n):
        return [self(i) for i in range(1,n+1)]

def is_power_of_two(n):
    r"""
    This function returns True if and only if $n$ is a power of 2

    INPUT:
        n -- integer

    OUTPUT:
        True -- if n is a power of 2
        False -- if not

    EXAMPLES:
        sage: from sage.databases.sloane_functions import is_power_of_two

        sage: is_power_of_two(1024)
        True

        sage: is_power_of_two(1)
        True

        sage: is_power_of_two(24)
        False

        sage: is_power_of_two(0)
        False

        sage: is_power_of_two(-4)
        False

    AUTHOR:
        -- Jaap Spies (2006-12-09)

    """
    # modification of is2pow(n) from the Programming Guide
    while n > 0 and n%2 == 0:
        n = n >> 1
    return n == 1

class A111774(SloaneSequence):
    r"""
    Sequence of numbers of the third kind, i.e., numbers that can be
    written as a sum of at least three consecutive positive integers.

    Odd primes can only be written as a sum of two consecutive integers.
    Powers of 2 do not have a representation as a sum of $k$ consecutive
    integers (other than the trivial $n = n$ for $k = 1$).

    See: http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A111774; a
        Numbers that can be written as a sum of at least three consecutive positive integers.
        sage: a(1)
        6
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(100)
        141
        sage: a.list(12)
        [6, 9, 10, 12, 14, 15, 18, 20, 21, 22, 24, 25]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: Unable to coerce rational (=1/3) to an Integer.

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def _repr_(self):
        return "Numbers that can be written as a sum of at least three consecutive positive integers."

    offset = 1

    def _precompute(self, how_many=150):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = []
            n = 1
            self._n = n
        self._b += [i for i in range(n, n+how_many) if self.is_number_of_the_third_kind(i)]

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)

    def is_number_of_the_third_kind(self, n):
        r"""
        This function returns True if and only if $n$ is a number of the third kind.

        A number is of the third kind if it can be written as a sum of at
        least three consecutive positive integers.  Odd primes can only be
        written as a sum of two consecutive integers.  Powers of 2 do not
        have a representation as a sum of $k$ consecutive integers (other
        than the trivial $n = n$ for $k = 1$).

        See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

        INPUT:
            n -- positive integer

        OUTPUT:
            True -- if n is not prime and not a power of 2
            False --

        EXAMPLES:
            sage: a = sloane.A111774
            sage: a.is_number_of_the_third_kind(6)
            True
            sage: a.is_number_of_the_third_kind(100)
            True
            sage: a.is_number_of_the_third_kind(16)
            False
            sage: a.is_number_of_the_third_kind(97)
            False

        AUTHOR:
            -- Jaap Spies (2006-12-09)
        """
        if (not arith.is_prime(n)) and (not is_power_of_two(n)):
            return True
        else:
            return False

class A111775(SloaneSequence):
    r"""
    Number of ways $n$ can be written as a sum of at least three consecutive integers.

    Powers of 2 and (odd) primes can not be written as a sum of at least
    three consecutive integers. $a(n)$ strongly depends on the number
    of odd divisors of $n$ (A001227):
    Suppose $n$ is to be written as sum of $k$ consecutive integers
    starting with $m$, then $2n = k(2m + k - 1)$.
    Only one of the factors is odd. For each odd divisor of $n$
    there is a unique corresponding $k$, $k=1$ and $k=2$ must be excluded.

    See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A111775; a
        Number of ways n can be written as a sum of at least three consecutive integers.

        sage: a(1)
        0
        sage: a(0)
        0

    We have a(15)=2 because 15 = 4+5+6 and 15 = 1+2+3+4+5. The number of odd divisors of 15 is 4.
        sage: a(15)
        2

        sage: a(100)
        2
        sage: a(256)
        0
        sage: a(29)
        0
        sage: a.list(20)
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 2, 0, 0, 2, 0]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: Unable to coerce rational (=1/3) to an Integer.

    AUTHOR:
        -- Jaap Spies (2006-12-09)
    """
    def _repr_(self):
        return "Number of ways n can be written as a sum of at least three consecutive integers."

    offset = 0

    def __call__(self, n):
        m = Integer(n)
        if m < 0:
            raise ValueError, "input n (=%s) must be a non negative integer"%n
        return self._eval(m)

    def _eval(self, n):
        if n == 1 or n == 0:
            return 0
        k = sum(i%2 for i in arith.divisors(n)) # A001227, the number of odd divisors
        if n % 2 ==0:
            return k-1
        else:
            return k-2

    def list(self, n):
       return [self(i) for i in range(0,n)]

class A111776(SloaneSequence):
    r"""
    The $n$th term of the sequence $a(n)$ is the largest $k$ such that
    $n$ can be written as sum of $k$ consecutive integers.

    $n$ is the sum of at most $a(n)$ consecutive positive integers.
    Suppose $n$ is to be written as sum of $k$ consecutive integers starting
    with $m$, then $2n = k(2m + k - 1)$. Only one of the factors is odd.
    For each odd divisor $d$ of $n$ there is a unique corresponding
    $k = min(d,2n/d)$. $a(n)$ is the largest among those $k$
.
    See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def _repr_(self):
        return "a(n) is the largest k such that n can be written as sum of k consecutive integers."

    offset = 0

    def __call__(self, n):
        m = Integer(n)
        if m < 0:
            raise ValueError, "input n (=%s) must be a non negative integer"%n
        return self._eval(m)

    def _eval(self, n):
        if n == 1 or n == 0:
            return 1
        m = 0
        for d in [i for i in arith.divisors(n) if i%2]: # d is odd divisor
            k = min(d, 2*n/d)
            if k > m:
                m = k
        return m

    def list(self, n):
       return [self(i) for i in range(0,n)]

#############################################################
# III. Create the Sloane object, off which all the sequence
#      objects are members.
#############################################################

class Sloane(SageObject):
    pass
sloane = Sloane()

sloane.A000005 = A000005()
sloane.A000010 = A000010()
sloane.A000045 = A000045()
sloane.A000203 = A000203()
sloane.A111774 = A111774()
sloane.A111775 = A111775()
sloane.A111776 = A111776()
