r"""
Base class for parent objects with generators

Many parent objects in SAGE are equipped with generators, which are
special elements of the object.  For example, the polynomial ring
$\Z[x,y,z]$ is generated by $x$, $y$, and $z$.  In SAGE the $i$th
generator of an object \code{X} is obtained using the notation
\code{X.gen(i)}.  From the SAGE interactive prompt, the shorthand
notation \code{X.i} is also allowed.

REQUIRED: A class that derives from ParentWithGens \emph{must} define
the ngens() and gen(i) methods.

OPTIONAL: It is also good if they define gens() to return all gens,
but this is not necessary.

The \code{gens} function returns a tuple of all generators, the
\code{ngens} function returns the number of generators, and the
\code{_assign_names}, \code{name} and \code{names} functions allow one
to change or obtain the way generators are printed. (They \emph{only}
affect printing!)

The following examples illustrate these functions in the context of
multivariate polynomial rings and free modules.

EXAMPLES:
    sage: R = MPolynomialRing(IntegerRing(), 3)
    sage: R.ngens()
    3
    sage: R.gen(0)
    x0
    sage: R.gens()
    (x0, x1, x2)
    sage: R.variable_names()
    ('x0', 'x1', 'x2')

This example illustrates generators for a free module over $\Z$.

    sage: M = FreeModule(IntegerRing(), 4)
    sage: M
    Ambient free module of rank 4 over the principal ideal domain Integer Ring
    sage: M.ngens()
    4
    sage: M.gen(0)
    (1, 0, 0, 0)
    sage: M.gens()
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

The names of the generators of a free module aren't really used anywhere,
but they are still defined:

    sage: M.variable_names()
    ('x0', 'x1', 'x2', 'x3')
"""

###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2005, 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

import sage.misc.defaults
import sage.misc.latex
import gens_py

include '../ext/stdsage.pxi'

def is_ParentWithGens(x):
    """
    Return True if x is a parent object with generators, i.e., derives
    from sage.structure.parent.ParentWithGens and False otherwise.

    EXAMPLES:
        sage: is_ParentWithGens(QQ['x'])
        True
        sage: is_ParentWithGens(CC)
        True
        sage: is_ParentWithGens(Primes())
        False
    """
    return bool(PY_TYPE_CHECK(x, ParentWithGens))

def is_ParentWithAdditiveAbelianGens(x):
    """
    Return True if x is a parent object with additive abelian
    generators, i.e., derives from
    sage.structure.parent.ParentWithAdditiveAbelianGens and False
    otherwise.

    EXAMPLES:
        sage: is_ParentWithAdditiveAbelianGens(QQ)
        False
        sage: is_ParentWithAdditiveAbelianGens(QQ^3)
        True
    """
    return bool(PY_TYPE_CHECK(x, ParentWithAdditiveAbelianGens))

def is_ParentWithMultiplicativeAbelianGens(x):
    """
    Return True if x is a parent object with additive abelian
    generators, i.e., derives from
    sage.structure.parent.ParentWithMultiplicativeAbelianGens and False
    otherwise.

    EXAMPLES:
        sage: is_ParentWithMultiplicativeAbelianGens(QQ)
        False
        sage: is_ParentWithMultiplicativeAbelianGens(DirichletGroup(11))
        True
    """
    return bool(PY_TYPE_CHECK(x, ParentWithMultiplicativeAbelianGens))

def _certify_names(names):
    v = []
    for N in names:
        if not isinstance(N, str):
            raise TypeError, "variable name must be a string but %s isn't"%N
        N = N.strip()
        if len(N) == 0:
            raise ValueError, "variable name must be nonempty"
        if not N.isalnum():
            raise ValueError, "variable names must be alphanumeric, but one is '%s' which is not."%N
        if not N[0].isalpha():
            raise ValueError, "first letter of variable name must be a letter"
        v.append(N)
    return tuple(v)

def normalize_names(int ngens, names=None):
    if names is None: return None
    if isinstance(names, str) and names.find(',') != -1:
        names = names.split(',')
    if isinstance(names, str) and ngens > 1 and len(names) == ngens:
        names = tuple(names)
    if isinstance(names, str):
        name = names
        names = sage.misc.defaults.variable_names(ngens, name)
        names = _certify_names(names)
    else:
        names = _certify_names(names)
        if not isinstance(names, (list, tuple)):
            raise TypeError, "names must be a list or tuple of strings"
        for x in names:
            if not isinstance(x,str):
                raise TypeError, "names must consist of strings"
        if len(names) != ngens:
            raise IndexError, "the number of names must equal the number of generators"
    return names

# Classes that derive from ParentWithGens must define gen(i) and
# ngens() functions.  It is also good if they define gens() to return
# all gens, but this is not necessary.

cdef class ParentWithGens(parent.Parent):
    def __init__(self, base, names=None, normalize=True):
        self._base = base
        self._assign_names(names=names, normalize=normalize)
        self._has_coerce_map_from = {}

    def base_ring(self):
        return self._base

    # Derived class *must* define ngens method.
    def ngens(self):
        raise NotImplementedError, "Number of generators not known."

    # Derived class *must* define gen method.
    def gen(self, i=0):
        raise NotImplementedError, "i-th generator not known."

    def __getitem__(self, n):
        return self.list()[n]

    def __getslice__(self,  Py_ssize_t n,  Py_ssize_t m):
        return self.list()[int(n):int(m)]

    def __len__(self):
        return len(self.list())

    def list(self):
        """
        Return a list of all elements in this object, if possible (the
        object must define an iterator).
        """
        if self._list != None:
            return self._list
        else:
            self._list = list(self.__iter__())
        return self._list

    def objgens(self):
        """
        Return self and the generators of self as a tuple.

        INPUT:
            names -- tuple or string

        OUTPUT:
            self  -- this object
            tuple -- self.gens()

        EXAMPLES:
            sage: R, x = MPolynomialRing(QQ,3).objgens()
            sage: R
            Polynomial Ring in x0, x1, x2 over Rational Field
            sage: x
            (x0, x1, x2)
        """
        return self, self.gens()

    def objgen(self):
        """
        Return self and the generator of self.

        INPUT:
            names -- tuple or string

        OUTPUT:
            self  -- this object
            an object -- self.gen()

        EXAMPLES:
            sage: R, x = PolynomialRing(QQ).objgen()
            sage: R
            Univariate Polynomial Ring in x over Rational Field
            sage: x
            x
        """
        return self, self.gen()

    def gens(self):
       """
       Return a tuple whose entries are the generators for this
       object, in order.
       """
       cdef int i, n
       if self._gens != None:
           return self._gens
       else:
           v = []
           n = self.ngens()
           for i from 0 <= i < n:
               v.append(self.gen(i))
           self._gens = tuple(v)
           return self._gens

    def gens_dict(self):
        r"""
        Return a dictionary whose entries are \code{{var_name:variable,...}}.
        """
        if self._gens_dict != None:
            return self._gens_dict
        else:
            v = {}
            for x in self.gens():
                v[str(x)] = x
            self._gens_dict = v
            return v

    def _assign_names(self, names=None, normalize=True):
        """
        Set the names of the generator of this object.

        This can only be done once because objects with generators
        are immutable, and is typically done during creation of the object.

        EXAMPLES:
        When we create this polynomial ring, self._assign_names is called by the constructor:

            sage: R = QQ['x,y,abc']; R
            Polynomial Ring in x, y, abc over Rational Field
            sage: R.2
            abc

        We can't rename the variables:
            sage: R._assign_names(['a','b','c'])
            Traceback (most recent call last):
            ...
            ValueError: variable names cannot be changed after object creation.
        """
        if names is None: return
        if normalize:
            names = normalize_names(self.ngens(), names)
        if not (self._names is None) and names != self._names:
            raise ValueError, 'variable names cannot be changed after object creation.'
        self._names = names

    def inject_variables(self, scope=None, verbose=True):
        """
        Inject the generators of self with their names into the
        namespace of the Python code from which this function is
        called.  Thus, e.g., if the generators of self are labeled
        'a', 'b', and 'c', then after calling this method the
        variables a, b, and c in the current scope will be set
        equal to the generators of self.

        NOTE: If Foo is a constructor for a SAGE object with
        generators, and Foo is defined in Pyrex, then it would
        typically call inject_variables() on the object it
        creates.  E.g., PolyomialRing(QQ, 'y') does this so that the
        variable y is the generator of the polynomial ring.
        """
        v = self.variable_names()
        g = self.gens()
        if scope is None:
            scope = globals()
        if verbose:
            print "Defining %s"%(', '.join(v))
        cdef int i
        for i from 0 <= i < len(v):
            scope[v[i]] = g[i]

    def injvar(self, scope=None, verbose=True):
        """
        This is a synonym for self.inject_variables(...)
        <<<sage.structure.parent_gens.ParentWithGens.inject_variables>>>
        """
        return self.inject_variables(scope=scope, verbose=verbose)

    def __temporarily_change_names(self, names, latex_names):
        """
        This is used by the variable names context manager.
        """
        old = self._names, self._latex_names
        (self._names, self._latex_names) = names, latex_names
        return old

    def variable_names(self):
        if self._names != None:
            return self._names
        raise ValueError, "variable names have not yet been set using self._assign_names(...)"

    def latex_variable_names(self):
        if self._latex_names != None:
            return self._latex_names
        # Compute the latex versions of the variable names.
        self._latex_names = []
        for x in self.variable_names():
            self._latex.append(sage.misc.latex.latex_variable_name(x))
        return self._latex_names

    def variable_name(self):
        return self.variable_names()[0]

    def latex_name(self):
        return self.variable_name()

    #################################################################################
    # Coercion support functionality
    #################################################################################
    def _coerce_(self, x):            # Call this from Python (do not override!)
        return self._coerce_c(x)

    cdef _coerce_c(self, x):          # DO NOT OVERRIDE THIS (call it)
        try:
            P = x.parent()
            if P is self:
                return x
            elif P == self:
                return self(x)
        except AttributeError, msg:
            pass
        if HAS_DICTIONARY(self):
            return self._coerce_impl(x)
        else:
            return self._coerce_c_impl(x)

    cdef _coerce_c_impl(self, x):     # OVERRIDE THIS FOR SAGEX CLASES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        raise TypeError

    def _coerce_impl(self, x):        # OVERRIDE THIS FOR PYTHON CLASSES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        return self._coerce_c_impl(x)

    def _coerce_try(self, x, v):
        """
        Given a list v of rings, try to coerce x canonically into each
        one in turn.  Return the __call__ coercion of the result into
        self of the first canonical coercion that succeeds.  Raise a
        TypeError if none of them succeed.

        INPUT:
             x -- Python object
             v -- parent object or list (iterator) of parent objects
        """
        if not isinstance(v, list):
            v = [v]
        for R in v:
            try:
                y = R._coerce_(x)
                return self(y)
            except TypeError, msg:
                pass
        raise TypeError, "no canonical coercion of element into self"

    def _coerce_self(self, x):
        return self._coerce_self_c(x)

    cdef _coerce_self_c(self, x):
        """
        Try to canonically coerce x into self.
        Return result on success or raise TypeError on failure.
        """
        # todo -- optimize?
        try:
            P = x.parent()
            if P is self:
                return x
            elif P == self:
                return self(x)
        except AttributeError:
            pass
        raise TypeError, "no canonical coercion to self defined"

    def has_coerce_map_from(self, S):
        return self.has_coerce_map_from_c(S)

    cdef has_coerce_map_from_c(self, S):
        """
        Return True if there is a natural map from S to self.
        Otherwise, return False.
        """
        try:
            return self._has_coerce_map_from[S]
        except KeyError:
            pass
        except TypeError:
            self._has_coerce_map_from = {}
        try:
            self._coerce_c(S(0))
        except TypeError:
            self._has_coerce_map_from[S] = False
            return False
        self._has_coerce_map_from[S] = True
        return True

    #################################################################################
    # Give all objects with generators a dictionary, so that attribute setting
    # works.   It would be nice if this functionality were standard in Pyrex,
    # i.e., just define __dict__ as an attribute and all this code gets generated.
    #################################################################################
    def __getstate__(self):
        d = []
        try:
            d = list(self.__dict__.copy().iteritems()) # so we can add elements
        except AttributeError:
            pass
        d = dict(d)
        d['_base'] = self._base
        d['_gens'] = self._gens
        d['_gens_dict'] = self._gens_dict
        d['_list'] = self._list
        d['_names'] = self._names
        d['_latex_names'] = self._latex_names
        try:
            d['_generator_orders'] = self._generator_orders
        except AttributeError:
            pass

        return d

    def __setstate__(self,d):
        try:
            self.__dict__ = d
            self._generator_orders = d['_generator_orders']
        except (AttributeError,KeyError):
            pass
        self._base = d['_base']
        self._gens = d['_gens']
        self._gens_dict = d['_gens_dict']
        self._list = d['_list']
        self._names = d['_names']
        self._latex_names = d['_latex_names']

    #################################################################################
    # Morphisms of objects with generators
    #################################################################################

    def _is_valid_homomorphism_(self, codomain, im_gens):
        r"""
        Return True if \code{im_gens} defines a valid homomorphism
        from self to codomain; otherwise return False.

        If determining whether or not a homomorphism is valid has not
        been implemented for this ring, then a NotImplementedError exception
        is raised.
        """
        raise NotImplementedError, "Verification of correctness of homomorphisms from %s not yet implmented."%self

    def hom(self, im_gens, codomain=None, check=True):
        r"""
        Return the unique homomorphism from self to codomain that
        sends \code{self.gens()} to the entries of \code{im_gens}.
        Raises a TypeError if there is no such homomorphism.

        INPUT:
            im_gens -- the images in the codomain of the generators of
                       this object under the homomorphism
            codomain -- the codomain of the homomorphism
            check -- whether to verify that the images of generators extend
                     to define a map (using only canonical coercisions).

        OUTPUT:
            a homomorphism self --> codomain

        \note{As a shortcut, one can also give an object X instead of
        \code{im_gens}, in which case return the (if it exists)
        natural map to X.}

        EXAMPLE: Polynomial Ring
        We first illustrate construction of a few homomorphisms
        involving a polynomial ring.

            sage: R, x = PolynomialRing(ZZ).objgen()
            sage: f = R.hom([5], QQ)
            sage: f(x^2 - 19)
            6

            sage: R, x = PolynomialRing(QQ).objgen()
            sage: f = R.hom([5], GF(7))
            Traceback (most recent call last):
            ...
            TypeError: images do not define a valid homomorphism

            sage: R, x = PolynomialRing(GF(7)).objgen()
            sage: f = R.hom([3], GF(49,'a'))
            sage: f
            Ring morphism:
              From: Univariate Polynomial Ring in x over Finite Field of size 7
              To:   Finite Field in a of size 7^2
              Defn: x |--> 3
            sage: f(x+6)
            2
            sage: f(x^2+1)
            3

        EXAMPLE: Natural morphism
            sage: f = ZZ.hom(GF(5))
            sage: f(7)
            2
            sage: f
            Coercion morphism:
              From: Integer Ring
              To:   Finite Field of size 5

        There might not be a natural morphism, in which case a TypeError exception is raised.
            sage: QQ.hom(ZZ)
            Traceback (most recent call last):
            ...
            TypeError: Natural coercion morphism from Rational Field to Integer Ring not defined.
        """
        if not isinstance(im_gens, (tuple, list)):
            return self.Hom(im_gens).natural_map()
        if codomain is None:
            from sage.structure.all import Sequence
            im_gens = Sequence(im_gens)
            codomain = im_gens.universe()
        return self.Hom(codomain)(im_gens, check=check)

cdef class ParentWithMultiplicativeAbelianGens(ParentWithGens):
    def generator_orders(self):
        if self._generator_orders != None:
            return self._generator_orders
        else:
            g = []
            for x in self.gens():
                g.append(x.multiplicative_order())
            self._generator_orders = g
            return g

    def __iter__(self):
        """
        Return an iterator over the elements in this object.
        """
        return gens_py.multiplicative_iterator(self)

cdef class ParentWithAdditiveAbelianGens(ParentWithGens):
    def generator_orders(self):
        if self._generator_orders != None:
            return self._generator_orders
        else:
            g = []
            for x in self.gens():
                g.append(x.additive_order())
            self._generator_orders = g
            return g

    def __iter__(self):
        """
        Return an iterator over the elements in this object.
        """
        return gens_py.abelian_iterator(self)

class localvars:
    r"""
    Context manager for safely temporarily changing the variables
    names of an object with generators.

    Objects with named generators are globally unique in SAGE.
    Sometimes, though, it is very useful to be able to temporarily
    display the generators differently.   The new Python "with"
    statement and the localvars context manager make this easy and
    safe (and fun!)

    Suppose X is any object with generators.  Write
    \begin{verbatim}
        with localvars(X, names[, latex_names] [,normalize=False]):
             some code
             ...
    \end{verbatim}
    and the indented code will be run as if the names in X are changed
    to the new names.  If you give normalize=True, then the names are
    assumed to be a tuple of the correct number of strings.

    If you're writing Python library code, you currently have
    to put \code{from __future__ import with_statement} in your file
    in order to use the \code{with} statement.  This restriction will
    disappear in Python 2.6.

    EXAMPLES:
        sage: R.<x,y> = PolynomialRing(QQ,2)
        sage: with localvars(R, 'z,w'):
        ...       print x^3 + y^3 - x*y
        ...
        w^3 - z*w + z^3

    NOTES: I wrote this because it was needed to print elements of the
    quotient of a ring R by an ideal I using the print function for
    elemnts of R.  See the code in \code{quotient_ring_element.pyx}.

    AUTHOR: William Stein (2006-10-31)
    """
    def __init__(self, obj, names, latex_names=None, normalize=True):
        self._obj = obj
        if normalize:
            self._names = normalize_names(obj.ngens(), names)
            self._latex_names = latex_names
        else:
            self._names = normalize_names(obj.ngens(), names)
            self._latex_names = latex_names

    def __enter__(self):
        self._orig = self._obj.__temporarily_change_names(self._names, self._latex_names)

    def __exit__(self, type, value, traceback):
        self._obj.__temporarily_change_names(self._orig[0], self._orig[1])
