r"""
Ideals

Sage provides functionality for computing with ideals. One can
create an ideal in any commutative ring `R` by giving a
list of generators, using the notation
``R.ideal([a,b,...])``.
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from types import GeneratorType

import sage.misc.latex as latex
import sage.rings.ring
import sage.rings.principal_ideal_domain
import commutative_ring
from sage.structure.sage_object import SageObject
from sage.structure.element import MonoidElement
from sage.interfaces.singular import singular as singular_default, is_SingularElement
import sage.rings.infinity
from sage.structure.sequence import Sequence

def Ideal(*args, **kwds):
    r"""
    Create the ideal in ring with given generators.

    There are some shorthand notations for creating an ideal, in
    addition to using the Ideal function::

                --  R.ideal(gens, coerce=True)
                --  gens*R
                --  R*gens

    INPUT:

    -  ``R (optional)`` - a ring (if not given, will try to
       infer it from gens)

    -  ``gens`` - list of elements generating the ideal

    -  ``coerce (optional)`` - bool (default: True);
       whether gens need to be coerced into ring.

    OUTPUT: The ideal of ring generated by gens.

    EXAMPLES::

        sage: R, x = PolynomialRing(ZZ, 'x').objgen()
        sage: I = R.ideal([4 + 3*x + x^2, 1 + x^2])
        sage: I
        Ideal (x^2 + 3*x + 4, x^2 + 1) of Univariate Polynomial Ring in x over Integer Ring
        sage: Ideal(R, [4 + 3*x + x^2, 1 + x^2])
        Ideal (x^2 + 3*x + 4, x^2 + 1) of Univariate Polynomial Ring in x over Integer Ring
        sage: Ideal((4 + 3*x + x^2, 1 + x^2))
        Ideal (x^2 + 3*x + 4, x^2 + 1) of Univariate Polynomial Ring in x over Integer Ring

    ::

        sage: ideal(x^2-2*x+1, x^2-1)
        Ideal (x^2 - 2*x + 1, x^2 - 1) of Univariate Polynomial Ring in x over Integer Ring
        sage: ideal([x^2-2*x+1, x^2-1])
        Ideal (x^2 - 2*x + 1, x^2 - 1) of Univariate Polynomial Ring in x over Integer Ring
        sage: l = [x^2-2*x+1, x^2-1]
        sage: ideal(f^2 for f in l)
        Ideal (x^4 - 4*x^3 + 6*x^2 - 4*x + 1, x^4 - 2*x^2 + 1) of
        Univariate Polynomial Ring in x over Integer Ring

    This example illustrates how Sage finds a common ambient ring for
    the ideal, even though 1 is in the integers (in this case).

    ::

        sage: R.<t> = ZZ['t']
        sage: i = ideal(1,t,t^2)
        sage: i
        Ideal (1, t, t^2) of Univariate Polynomial Ring in t over Integer Ring
        sage: ideal(1/2,t,t^2)
        Principal ideal (1) of Univariate Polynomial Ring in t over Rational Field

    This shows that the issues at trac #1104 are resolved::

        sage: Ideal(3, 5)
        Principal ideal (1) of Integer Ring
        sage: Ideal(ZZ, 3, 5)
        Principal ideal (1) of Integer Ring
        sage: Ideal(2, 4, 6)
        Principal ideal (2) of Integer Ring

    TESTS::

        sage: R, x = PolynomialRing(ZZ, 'x').objgen()
        sage: I = R.ideal([4 + 3*x + x^2, 1 + x^2])
        sage: I == loads(dumps(I))
        True

    ::

        sage: I = Ideal(R, [4 + 3*x + x^2, 1 + x^2])
        sage: I == loads(dumps(I))
        True

    ::

        sage: I = Ideal((4 + 3*x + x^2, 1 + x^2))
        sage: I == loads(dumps(I))
        True
    """
    if len(args) == 0:
        raise ValueError, "need at least one argument"

    if kwds.has_key('coerce'):
        coerce = kwds['coerce']
    else:
        coerce = True

    first = args[0]

    if not isinstance(first, sage.rings.ring.Ring):
        if isinstance(first, Ideal_generic):
            R = first.ring()
            gens = first.gens()
        else:
            gens = args
            if isinstance(first, (list, tuple, GeneratorType)):
                gens = first
            gens = Sequence(gens)
            R = gens.universe()
            if not isinstance(R, sage.rings.ring.Ring):
                raise TypeError, "unable to find common ring into which all ideal generators map"
            return R.ideal(gens)
    else:
        R = first
        gens = args[1:]
        if isinstance(gens[0], Ideal_generic):
            gens = gens[0].gens()
        elif isinstance(gens[0], (list, tuple)):
            gens = gens[0]

    if not commutative_ring.is_CommutativeRing(R):
        raise TypeError, "R must be a commutative ring"

    if len(gens) == 0:
        gens = [R(0)]
        coerce = False

    if coerce:
        gens = [R(g) for g in gens]

    if isinstance(R, sage.rings.principal_ideal_domain.PrincipalIdealDomain):
        # Use GCD algorithm to obtain a principal ideal
        g = gens[0]
        for h in gens[1:]:
            g = R.gcd(g, h)
        return Ideal_pid(R, g)

    if len(gens) == 1:
        return Ideal_principal(R, gens[0])

    return Ideal_generic(R, gens, coerce=False)

def is_Ideal(x):
    r"""
    Returns True if object is an ideal of a ring.

    EXAMPLES: A simple example involving the ring of integers. Note
    that Sage does not interpret rings objects themselves as ideals.
    However, one can still explicitly construct these ideals::

        sage: from sage.rings.ideal import is_Ideal
        sage: R = ZZ
        sage: is_Ideal(R)
        False
        sage: 1*R; is_Ideal(1*R)
        Principal ideal (1) of Integer Ring
        True
        sage: 0*R; is_Ideal(0*R)
        Principal ideal (0) of Integer Ring
        True

    Sage recognizes ideals of polynomial rings as well::

        sage: R = PolynomialRing(QQ, 'x'); x = R.gen()
        sage: I = R.ideal(x^2 + 1); I
        Principal ideal (x^2 + 1) of Univariate Polynomial Ring in x over Rational Field
        sage: is_Ideal(I)
        True
        sage: is_Ideal((x^2 + 1)*R)
        True
    """
    return isinstance(x, Ideal_generic)

class Ideal_generic(MonoidElement):
    """
    An ideal.
    """
    def __init__(self, ring, gens, coerce=True):
        self.__ring = ring
        if not isinstance(gens, (list, tuple)):
            gens = [gens]
        if coerce:
            gens = [ring(x) for x in gens]

        gens = tuple(gens)
        if len(gens)==0: gens=(ring.zero_element(),)
        self.__gens = gens
        MonoidElement.__init__(self, ring.ideal_monoid())

    def _repr_short(self):
        return '(%s)'%(', '.join([str(x) for x in self.gens()]))

    def __repr__(self):
        return "Ideal %s of %s"%(self._repr_short(), self.ring())

    def __cmp__(self, other):
        S = set(self.gens())
        T = set(other.gens())
        if S == T:
            return 0
        return cmp(self.gens(), other.gens())

    def __contains__(self, x):
        try:
            return self._contains_(self.__ring(x))
        except TypeError:
            return False

    def _contains_(self, x):
        # check if x, which is assumed to be in the ambient ring, is actually in this ideal.
        raise NotImplementedError

    def __nonzero__(self):
        r"""Return True if this ideal is not (0).
        TESTS::

            sage: I = ZZ.ideal(5)
            sage: bool(I)
            True

        ::

            sage: I = ZZ['x'].ideal(0)
            sage: bool(I)
            False

        ::

            sage: I = ZZ['x'].ideal(ZZ['x'].gen()^2)
            sage: bool(I)
            True

        ::

            sage: I = QQ['x', 'y'].ideal(0)
            sage: bool(I)
            False
        """
        for g in self.gens():
            if not g.is_zero():
                return True
        return False

    def base_ring(self):
        r"""
        Returns the base ring of this ideal.

        EXAMPLES::

            sage: R = ZZ
            sage: I = 3*R; I
            Principal ideal (3) of Integer Ring
            sage: J = 2*I; J
            Principal ideal (6) of Integer Ring
            sage: I.base_ring(); J.base_ring()
            Integer Ring
            Integer Ring

        We construct an example of an ideal of a quotient ring::

            sage: R = PolynomialRing(QQ, 'x'); x = R.gen()
            sage: I = R.ideal(x^2 - 2)
            sage: I.base_ring()
            Rational Field

        And p-adic numbers::

            sage: R = Zp(7, prec=10); R
            7-adic Ring with capped relative precision 10
            sage: I = 7*R; I
            Principal ideal (7 + O(7^11)) of 7-adic Ring with capped relative precision 10
            sage: I.base_ring()
            7-adic Ring with capped relative precision 10
        """
        return self.ring().base_ring()

    def _latex_(self):
        return '\\left(%s\\right)%s'%(", ".join([latex.latex(g) for g in \
                                                 self.gens()]),
                                      latex.latex(self.ring()))

    def ring(self):
        """
        Returns the ring containing this ideal.

        EXAMPLES::

            sage: R = ZZ
            sage: I = 3*R; I
            Principal ideal (3) of Integer Ring
            sage: J = 2*I; J
            Principal ideal (6) of Integer Ring
            sage: I.ring(); J.ring()
            Integer Ring
            Integer Ring

        Note that ``self.ring()`` is different from
        ``self.ring()``

        ::

            sage: R = PolynomialRing(QQ, 'x'); x = R.gen()
            sage: I = R.ideal(x^2 - 2)
            sage: I.base_ring()
            Rational Field
            sage: I.ring()
            Univariate Polynomial Ring in x over Rational Field

        Another example using polynomial rings::

            sage: R = PolynomialRing(QQ, 'x'); x = R.gen()
            sage: I = R.ideal(x^2 - 3)
            sage: I.ring()
            Univariate Polynomial Ring in x over Rational Field
            sage: Rbar = R.quotient(I, names='a')
            sage: S = PolynomialRing(Rbar, 'y'); y = Rbar.gen(); S
            Univariate Polynomial Ring in y over Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^2 - 3
            sage: J = S.ideal(y^2 + 1)
            sage: J.ring()
            Univariate Polynomial Ring in y over Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^2 - 3
        """
        return self.__ring

    def reduce(self, f):
        r"""
        Return the reduction the element of `f` modulo the ideal
        `I` (=self). This is an element of `R` that is
        equivalent modulo `I` to `f`.

        EXAMPLES::

            sage: ZZ.ideal(5).reduce(17)
            2
            sage: parent(ZZ.ideal(5).reduce(17))
            Integer Ring
        """
        return f       # default

    def gens(self):
        """
        Return a set of generators / a basis of self. This is usually the
        set of generators provided during object creation.

        EXAMPLE::

            sage: P.<x,y> = PolynomialRing(QQ,2)
            sage: I = Ideal([x,y+1]); I
            Ideal (x, y + 1) of Multivariate Polynomial Ring in x, y over Rational Field
            sage: I.gens()
            (x, y + 1)

        ::

            sage: ZZ.ideal(5,10).gens()
            (5,)
        """
        return self.__gens

    def gens_reduced(self):
        r"""
        Same as gens() for this ideal, since there is currently no special
        gens_reduced algorithm implemented for this ring.

        This method is provided so that ideals in ZZ have the method
        gens_reduced(), just like ideals of number fields.

        EXAMPLES::

            sage: ZZ.ideal(5).gens_reduced()
            (5,)
        """
        return self.gens()

    def is_maximal(self):
        r"""
        Returns True if the ideal is maximal in the ring containing the
        ideal.

        TODO: Make self.is_maximal() work! Write this code!

        EXAMPLES::

            sage: R = ZZ
            sage: I = R.ideal(7)
            sage: I.is_maximal()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def is_prime(self):
        r"""
        Returns True if the ideal is prime in the ring containing the
        ideal.

        TODO: Make self.is_prime() work! Write this code!

        EXAMPLES::

            sage: R = ZZ[x]
            sage: I = R.ideal(7)
            sage: I.is_prime()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def is_principal(self):
        r"""
        Returns True if the ideal is principal in the ring containing the
        ideal.

        TODO: Code is naive. Only keeps track of ideal generators as set
        during intiialization of the ideal. (Can the base ring change? See
        example below.)

        EXAMPLES::

            sage: R = ZZ[x]
            sage: I = R.ideal(2,x)
            sage: I.is_principal()
            Traceback (most recent call last):
            ...
            NotImplementedError
            sage: J = R.base_extend(QQ).ideal(2,x)
            sage: J.is_principal()
            True
        """
        if len(self.gens()) <= 1:
            return True
        raise NotImplementedError

    def is_trivial(self):
        r"""Return True if this ideal is (0) or (1).
        TESTS::

            sage: I = ZZ.ideal(5)
            sage: I.is_trivial()
            False

        ::

            sage: I = ZZ['x'].ideal(-1)
            sage: I.is_trivial()
            True

        ::

            sage: I = ZZ['x'].ideal(ZZ['x'].gen()^2)
            sage: I.is_trivial()
            False

        ::

            sage: I = QQ['x', 'y'].ideal(-5)
            sage: I.is_trivial()
            True

        ::

            sage: I = CC['x'].ideal(0)
            sage: I.is_trivial()
            True
        """
        if self.is_zero():
            return True
        # If self is principal, can give a complete answer
        if self.is_principal():
            return self.gens()[0].is_unit()
        # If self is not principal, can only give an affirmative answer
        for g in self.gens():
            if g.is_unit():
                return True
        raise NotImplementedError

    def category(self):
        """
        Return the category of this ideal.

        EXAMPLES: Note that category is dependent on the ring of the
        ideal.

        ::

            sage: I = ZZ.ideal(7)
            sage: J = ZZ[x].ideal(7,x)
            sage: K = ZZ[x].ideal(7)
            sage: I.category()
            Category of ring ideals in Integer Ring
            sage: J.category()
            Category of ring ideals in Univariate Polynomial Ring in x
            over Integer Ring
            sage: K.category()
            Category of ring ideals in Univariate Polynomial Ring in x
            over Integer Ring
        """
        import sage.categories.all
        return sage.categories.all.Ideals(self.__ring)

    def __add__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)
        return self.ring().ideal(self.gens() + other.gens())

    def __radd__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)
        return self.ring().ideal(self.gens() + other.gens())

    def __mul__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)
        return self.ring().ideal([x*y for x in self.gens() for y in other.gens()])

    def __rmul__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)
        return self.ring().ideal([y*x for x in self.gens() for y in other.gens()])

class Ideal_principal(Ideal_generic):
    """
    A principal ideal.
    """
    def __init__(self, ring, gen):
        Ideal_generic.__init__(self, ring, [gen])

    def __repr__(self):
        return "Principal ideal (%s) of %s"%(self.gen(), self.ring())

    def is_principal(self):
        r"""
        Returns True if the ideal is principal in the ring containing the
        ideal. When the ideal construction is explicitly principal (i.e.
        when we define an ideal with one element) this is always the case.

        EXAMPLES: Note that Sage automatically coerces ideals into
        principals ideals during initialization::

            sage: R = ZZ[x]
            sage: I = R.ideal(x)
            sage: J = R.ideal(2,x)
            sage: K = R.base_extend(QQ).ideal(2,x)
            sage: I
            Principal ideal (x) of Univariate Polynomial Ring in x
            over Integer Ring
            sage: J
            Ideal (2, x) of Univariate Polynomial Ring in x over Integer Ring
            sage: K
            Principal ideal (1) of Univariate Polynomial Ring in x
            over Rational Field
            sage: I.is_principal()
            True
            sage: K.is_principal()
            True
        """
        return True

    def gen(self):
        r"""
        Returns the generator of the principal ideal. The generators are
        elements of the ring containing the ideal.

        EXAMPLES: A simple example in the integers::

            sage: R = ZZ
            sage: I = R.ideal(7)
            sage: J = R.ideal(7, 14)
            sage: I.gen(); J.gen()
            7
            7

        Note that the generator belongs to the ring from which the ideal
        was initialized::

            sage: R = ZZ[x]
            sage: I = R.ideal(x)
            sage: J = R.base_extend(QQ).ideal(2,x)
            sage: a = I.gen(); a
            x
            sage: b = J.gen(); b
            1
            sage: a.base_ring()
            Integer Ring
            sage: b.base_ring()
            Rational Field
        """
        return self.gens()[0]

    def __contains__(self, x):
        """
        Returns True if x is in the ideal self.

        EXAMPLES::

            sage: P.<x> = PolynomialRing(ZZ)
            sage: I = P.ideal(x^2-2)
            sage: x^2 in I
            False
            sage: x^2-2 in I
            True
            sage: x^2-3 in I
            False
        """
        if self.gen().is_zero():
            return x.is_zero()
        return self.gen().divides(x)

    def __cmp__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)

        if not other.is_principal():
            return -1

        if self.is_zero():
            if not other.is_zero():
                return -1
            return 0

        # is other.gen() / self.gen() a unit in the base ring?
        g0 = other.gen()
        g1 = self.gen()
        if g0.divides(g1) and g1.divides(g0):
            return 0
        return 1

    def divides(self, other):
        """
        Returns True if self divides other.

        EXAMPLES::

            sage: P.<x> = PolynomialRing(QQ)
            sage: I = P.ideal(x)
            sage: J = P.ideal(x^2)
            sage: I.divides(J)
            True
            sage: J.divides(I)
            False
        """
        if isinstance(other, Ideal_principal):
            return self.gen().divides(other.gen())
        raise NotImplementedError

class Ideal_pid(Ideal_principal):
    """
    An ideal of a principal ideal domain.
    """
    def __init__(self, ring, gen):
        Ideal_principal.__init__(self, ring, gen)

    def __add__(self, other):
        if not isinstance(other, Ideal_generic):
            other = self.ring().ideal(other)
        return self.ring().ideal(self.gcd(other))

    def reduce(self, f):
        """
        Return the reduction of f modulo self.

        EXAMPLES::

            sage: I = 8*ZZ
            sage: I.reduce(10)
            2
            sage: n = 10; n.mod(I)
            2
        """
        f = self.ring()(f)
        if self.gen() == 0:
            return f
        q, r = f.quo_rem(self.gen())
        return r

    def gcd(self, other):
        r"""
        Returns the greatest common divisor of the principal ideal with the
        ideal ``other``; that is, the largest principal ideal
        contained in both the ideal and ``other``

        TODO: This is not implemented in the case when
        ``other`` is neither principal nor when the generator
        of ``self`` is contained in ``other``.
        Also, it seems that this class is used only in PIDs--is this
        redundant? Note: second example is broken.

        EXAMPLES: An example in the principal ideal domain ZZ::

            sage: R = ZZ
            sage: I = R.ideal(42)
            sage: J = R.ideal(70)
            sage: I.gcd(J)
            Principal ideal (14) of Integer Ring
            sage: J.gcd(I)
            Principal ideal (14) of Integer Ring

        TESTS: We cannot take the gcd of a principal ideal with a
        non-principal ideal as well: ( gcd(I,J) should be (7) )

        ::

            sage: I = ZZ.ideal(7)
            sage: J = ZZ[x].ideal(7,x)
            sage: I.gcd(J)
            Traceback (most recent call last):
            ...
            NotImplementedError
            sage: J.gcd(I)
            Traceback (most recent call last):
            ...
            AttributeError: 'Ideal_generic' object has no attribute 'gcd'

        Note::

            sage: type(I)
            <class 'sage.rings.ideal.Ideal_pid'>
            sage: type(J)
            <class 'sage.rings.ideal.Ideal_generic'>
        """
        if isinstance(other, Ideal_principal):
            return self.ring().ideal(self.gen().gcd(other.gen()))
        elif self.gen() in other:
            return other
        else:
            raise NotImplementedError

    def is_prime(self):
        """
        Returns True if the ideal is prime. This relies on the ring
        elements having a method is_irreducible() implemented, since an
        ideal (a) is prime iff a is irreducible (or 0)

        EXAMPLES::

            sage: ZZ.ideal(2).is_prime()
            True
            sage: ZZ.ideal(-2).is_prime()
            True
            sage: ZZ.ideal(4).is_prime()
            False
            sage: ZZ.ideal(0).is_prime()
            True
            sage: R.<x>=QQ[]
            sage: P=R.ideal(x^2+1); P
            Principal ideal (x^2 + 1) of Univariate Polynomial Ring in x over Rational Field
            sage: P.is_prime()
            True
        """
        if self.is_zero(): # PIDs are integral domains by definition
            return True
        g = self.gen()
        if hasattr(g, 'is_irreducible'):
            return g.is_irreducible()

        raise NotImplementedError

    def residue_field(self):
        """
        Return the residue class field of this ideal, which must be prime.

        TODO: Implement this for more general rings. Currently only defined
        for ZZ and for number field orders.

        EXAMPLES::

            sage: P = ZZ.ideal(61); P
            Principal ideal (61) of Integer Ring
            sage: F = P.residue_field(); F
            Residue field of Integers modulo 61
            sage: pi = F.reduction_map(); pi
            Partially defined reduction map from Rational Field to Residue field of Integers modulo 61
            sage: pi(123/234)
            6
            sage: pi(1/61)
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Cannot reduce rational 1/61 modulo 61: it has negative valuation
            sage: lift = F.lift_map(); lift
            Lifting map from Residue field of Integers modulo 61 to Rational Field
            sage: lift(F(12345/67890))
            33
            sage: (12345/67890) % 61
            33

        TESTS::

            sage: ZZ.ideal(96).residue_field()
            Traceback (most recent call last):
            ...
            ValueError: The ideal (Principal ideal (96) of Integer Ring) is not prime

        ::

            sage: R.<x>=QQ[]
            sage: I=R.ideal(x^2+1)
            sage: I.is_prime()
            True
            sage: I.residue_field()
            Traceback (most recent call last):
            NotImplementedError: residue_field() is only implemented for ZZ and rings of integers of number fields.
        """
        if not self.is_prime():
            raise ValueError, "The ideal (%s) is not prime"%self
        from sage.rings.integer_ring import ZZ
        if self.ring() is ZZ:
            return ZZ.residue_field(self, check = False)
        raise NotImplementedError, "residue_field() is only implemented for ZZ and rings of integers of number fields."

class Ideal_fractional(Ideal_generic):
    def __repr__(self):
        return "Fractional ideal %s of %s"%(self._repr_short(), self.ring())

# constructors for standard (benchmark) ideals, written uppercase as
# these are constructors

def Cyclic(R, n=None, homog=False, singular=singular_default):
    """
    Ideal of cyclic n-roots from 1-st n variables of R if R is
    coercable to Singular. If n==None n is set to R.ngens()

    INPUT:

    -  ``R`` - base ring to construct ideal for

    -  ``n`` - number of cyclic roots (default: None)

    -  ``homog`` - if True a homogenous ideal is returned
       using the last variable in the ideal (default: False)

    -  ``singular`` - singular instance to use

    .. note::

       R will be set as the active ring in Singular

    EXAMPLES: An example from a multivariate polynomial ring over the
    rationals::

        sage: P.<x,y,z> = PolynomialRing(QQ,3,order='lex')
        sage: I = sage.rings.ideal.Cyclic(P)
        sage: I
        Ideal (x + y + z, x*y + x*z + y*z, x*y*z - 1) of Multivariate Polynomial
        Ring in x, y, z over Rational Field
        sage: I.groebner_basis()
        [x + y + z, y^2 + y*z + z^2, z^3 - 1]

    We compute a Groebner basis for cyclic 6, which is a standard
    benchmark and test ideal::

        sage: R.<x,y,z,t,u,v> = QQ['x,y,z,t,u,v']
        sage: I = sage.rings.ideal.Cyclic(R,6)
        sage: B = I.groebner_basis()
        sage: len(B)
        45
    """
    from rational_field import RationalField

    if n:
        if n > R.ngens():
            raise ArithmeticError, "n must be <= R.ngens()"
    else:
        n = R.ngens()

    singular.lib("poly")
    R2 = R.change_ring(RationalField())
    R2._singular_().set_ring()

    if not homog:
        I = singular.cyclic(n)
    else:
        I = singular.cyclic(n).homog(R2.gen(n-1))
    return R2.ideal(I).change_ring(R)

def Katsura(R, n=None, homog=False, singular=singular_default):
    """
    n-th katsura ideal of R if R is coercable to Singular. If n==None n
    is set to R.ngens()

    INPUT:

    -  ``R`` - base ring to construct ideal for

    -  ``n`` - which katsura ideal of R

    -  ``homog`` - if True a homogenous ideal is returned
       using the last variable in the ideal (default: False)

    -  ``singular`` - singular instance to use

    EXAMPLES::

        sage: P.<x,y,z> = PolynomialRing(QQ,3)
        sage: I = sage.rings.ideal.Katsura(P,3); I
        Ideal (x + 2*y + 2*z - 1, x^2 + 2*y^2 + 2*z^2 - x, 2*x*y + 2*y*z - y)
        of Multivariate Polynomial Ring in x, y, z over Rational Field

    ::

        sage: Q.<x> = PolynomialRing(QQ,1)
        sage: J = sage.rings.ideal.Katsura(Q,1); J
        Ideal (x - 1) of Multivariate Polynomial Ring in x over Rational Field
    """
    from rational_field import RationalField
    if n:
        if n > R.ngens():
            raise ArithmeticError, "n must be <= R.ngens()."
    else:
        n = R.ngens()
    singular.lib("poly")
    R2 = R.change_ring(RationalField())
    R2._singular_().set_ring()

    if not homog:
        I = singular.katsura(n)
    else:
        I = singular.katsura(n).homog(R2.gen(n-1))
    return R2.ideal(I).change_ring(R)

def FieldIdeal(R):
    """
    Let q = R.base_ring().order() and (x0,...,x_n) = R.gens() then if
    q is finite this constructor returns

    `< x_0^q - x_0, ... , x_n^q - x_n >.`

    We call this ideal the field ideal and the generators the field
    equations.

    EXAMPLES: The Field Ideal generated from the polynomial ring over
    two variables in the finite field of size 2::

        sage: P.<x,y> = PolynomialRing(GF(2),2)
        sage: I = sage.rings.ideal.FieldIdeal(P); I
        Ideal (x^2 + x, y^2 + y) of Multivariate Polynomial Ring in x, y over
        Finite Field of size 2

    Antoher, similar example::

        sage: Q.<x1,x2,x3,x4> = PolynomialRing(GF(2^4,name='alpha'), 4)
        sage: J = sage.rings.ideal.FieldIdeal(Q); J
        Ideal (x1^16 + x1, x2^16 + x2, x3^16 + x3, x4^16 + x4) of
        Multivariate Polynomial Ring in x1, x2, x3, x4 over Finite
        Field in alpha of size 2^4
    """

    q = R.base_ring().order()

    if q is sage.rings.infinity.infinity:
        raise TypeError, "Cannot construct field ideal for R.base_ring().order()==infinity"

    return R.ideal([x**q - x for x in R.gens() ])
