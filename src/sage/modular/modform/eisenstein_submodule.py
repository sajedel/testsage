"""
The Eisenstein Subspace
"""

from sage.structure.all import Sequence
from sage.misc.all import verbose
import sage.rings.all as rings
from sage.categories.all import Objects
from sage.matrix.all import Matrix

from sage.rings.number_field.number_field_element import NumberFieldElement as NumberFieldElement

import eis_series
import element
import submodule

class EisensteinSubmodule(submodule.ModularFormsSubmodule):
    """
    The Eisenstein submodule of an ambient space of modular forms.
    """
    def __init__(self, ambient_space):
        """
        Return the Eisenstein submodule of the given space.

        EXAMPLES::

            sage: E = ModularForms(23,4).eisenstein_subspace() ## indirect doctest
            sage: E
            Eisenstein subspace of dimension 2 of Modular Forms space of dimension 7 for Congruence Subgroup Gamma0(23) of weight 4 over Rational Field
            sage: E == loads(dumps(E))
            True
        """
        verbose('creating eisenstein submodule of %s'%ambient_space)
        d = ambient_space._dim_eisenstein()
        V = ambient_space.module()
        n = V.dimension()
        self._start_position = int(n - d)
        S = V.submodule([V.gen(i) for i in range(n-d,n)], check=False,
                        already_echelonized=True)
        submodule.ModularFormsSubmodule.__init__(self, ambient_space, S)

    def _repr_(self):
        """
        Return the string representation of self.

        EXAMPLES::

            sage: E = ModularForms(23,4).eisenstein_subspace() ## indirect doctest
            sage: E._repr_()
            'Eisenstein subspace of dimension 2 of Modular Forms space of dimension 7 for Congruence Subgroup Gamma0(23) of weight 4 over Rational Field'
        """
        return "Eisenstein subspace of dimension %s of %s"%(self.dimension(), self.ambient_module())

    def eisenstein_submodule(self):
        """
        Return the Eisenstein submodule of self.
        (Yes, this is just self.)

        EXAMPLES::

            sage: E = ModularForms(23,4).eisenstein_subspace()
            sage: E == E.eisenstein_submodule()
            True
        """
        return self

    def modular_symbols(self, sign=0):
        r"""
        Return the corresponding space of modular symbols with given sign.

        .. warning::

           If sign != 0, then the space of modular symbols will, in general,
           only correspond to a *subspace* of this space of modular forms.
           This can be the case for both sign +1 or -1.

        EXAMPLES::

            sage: E = ModularForms(11,2).eisenstein_submodule()
            sage: M = E.modular_symbols(); M
            Modular Symbols subspace of dimension 1 of Modular Symbols space
            of dimension 3 for Gamma_0(11) of weight 2 with sign 0 over Rational Field
            sage: M.sign()
            0

            sage: M = E.modular_symbols(sign=-1); M
            Modular Symbols subspace of dimension 0 of Modular Symbols space of
            dimension 1 for Gamma_0(11) of weight 2 with sign -1 over Rational Field

            sage: E = ModularForms(1,12).eisenstein_submodule()
            sage: E.modular_symbols()
            Modular Symbols subspace of dimension 1 of Modular Symbols space of
            dimension 3 for Gamma_0(1) of weight 12 with sign 0 over Rational Field

            sage: eps = DirichletGroup(13).0
            sage: E = EisensteinForms(eps^2, 2)
            sage: E.modular_symbols()
            Modular Symbols subspace of dimension 2 of Modular Symbols space of dimension 4 and level 13, weight 2, character [zeta6], sign 0, over Cyclotomic Field of order 6 and degree 2
        """
        try:
            return self.__modular_symbols[sign]
        except AttributeError:
            self.__modular_symbols = {}
        except KeyError:
            pass
        A = self.ambient_module()
        S = A.modular_symbols(sign).eisenstein_submodule()
        self.__modular_symbols[sign] = S
        return S

class EisensteinSubmodule_params(EisensteinSubmodule):
    def parameters(self):
        r"""
        Return a list of parameters for each Eisenstein series
        spanning self. That is, for each such series, return a triple
        of the form (`\psi`, `\chi`, level), where `\psi` and `\chi`
        are the characters defining the Eisenstein series, and level
        is the smallest level at which this series occurs.

        EXAMPLES::

            sage: ModularForms(24,2).eisenstein_submodule().parameters()
            [([1, 1, 1], [1, 1, 1], 2),
            ([1, 1, 1], [1, 1, 1], 3),
            ([1, 1, 1], [1, 1, 1], 4),
            ([1, 1, 1], [1, 1, 1], 6),
            ([1, 1, 1], [1, 1, 1], 8),
            ([1, 1, 1], [1, 1, 1], 12),
            ([1, 1, 1], [1, 1, 1], 24)]
            sage: EisensteinForms(12,6).parameters()
            [([1, 1], [1, 1], 1),
            ([1, 1], [1, 1], 2),
            ([1, 1], [1, 1], 3),
            ([1, 1], [1, 1], 4),
            ([1, 1], [1, 1], 6),
            ([1, 1], [1, 1], 12)]
            sage: ModularForms(DirichletGroup(24).0,3).eisenstein_submodule().parameters()
            [([1, 1, 1], [-1, 1, 1], 1),
            ([1, 1, 1], [-1, 1, 1], 2),
            ([1, 1, 1], [-1, 1, 1], 3),
            ([1, 1, 1], [-1, 1, 1], 6),
            ([-1, 1, 1], [1, 1, 1], 1),
            ([-1, 1, 1], [1, 1, 1], 2),
            ([-1, 1, 1], [1, 1, 1], 3),
            ([-1, 1, 1], [1, 1, 1], 6)]
        """
        try:
            return self.__parameters
        except AttributeError:
            char = self._parameters_character()
            if char is None:
                P = eis_series.compute_eisenstein_params(self.level(), self.weight())
            else:
                P = eis_series.compute_eisenstein_params(char, self.weight())
            self.__parameters = P
            return P

    def _parameters_character(self):
        """
        Return the character defining self.

        EXAMPLES::

            sage: EisensteinForms(DirichletGroup(33).1,5)._parameters_character()
            [1, zeta10]
        """
        return self.character()

    def change_ring(self, base_ring):
        """
        Return self as a module over base_ring.

        EXAMPLES::

            sage: E = EisensteinForms(12,2) ; E
            Eisenstein subspace of dimension 5 of Modular Forms space of dimension 5 for Congruence Subgroup Gamma0(12) of weight 2 over Rational Field
            sage: E.basis()
            [
            1 + O(q^6),
            q + 6*q^5 + O(q^6),
            q^2 + O(q^6),
            q^3 + O(q^6),
            q^4 + O(q^6)
            ]
            sage: E.change_ring(GF(5))
            Eisenstein subspace of dimension 5 of Modular Forms space of dimension 5 for Congruence Subgroup Gamma0(12) of weight 2 over Finite Field of size 5
            sage: E.change_ring(GF(5)).basis()
            [
            1 + O(q^6),
            q + q^5 + O(q^6),
            q^2 + O(q^6),
            q^3 + O(q^6),
            q^4 + O(q^6)
            ]
        """
        if base_ring == self.base_ring():
            return self
        A = self.ambient_module()
        B = A.change_ring(base_ring)
        return B.eisenstein_submodule()

    def eisenstein_series(self):
        """
        Return the Eisenstein series that span this space (over the
        algebraic closure).

        EXAMPLES::

            sage: EisensteinForms(11,2).eisenstein_series()
            [
            5/12 + q + 3*q^2 + 4*q^3 + 7*q^4 + 6*q^5 + O(q^6)
            ]
            sage: EisensteinForms(1,4).eisenstein_series()
            [
            1/240 + q + 9*q^2 + 28*q^3 + 73*q^4 + 126*q^5 + O(q^6)
            ]
            sage: EisensteinForms(1,24).eisenstein_series()
            [
            236364091/131040 + q + 8388609*q^2 + 94143178828*q^3 + 70368752566273*q^4 + 11920928955078126*q^5 + O(q^6)
            ]
            sage: EisensteinForms(5,4).eisenstein_series()
            [
            1/240 + q + 9*q^2 + 28*q^3 + 73*q^4 + 126*q^5 + O(q^6),
            1/240 + q^5 + O(q^6)
            ]
            sage: EisensteinForms(13,2).eisenstein_series()
            [
            1/2 + q + 3*q^2 + 4*q^3 + 7*q^4 + 6*q^5 + O(q^6)
            ]

            sage: E = EisensteinForms(Gamma1(7),2)
            sage: E.set_precision(4)
            sage: E.eisenstein_series()
            [
            1/4 + q + 3*q^2 + 4*q^3 + O(q^4),
            1/7*zeta6 - 3/7 + q + (-2*zeta6 + 1)*q^2 + (3*zeta6 - 2)*q^3 + O(q^4),
            q + (-zeta6 + 2)*q^2 + (zeta6 + 2)*q^3 + O(q^4),
            -1/7*zeta6 - 2/7 + q + (2*zeta6 - 1)*q^2 + (-3*zeta6 + 1)*q^3 + O(q^4),
            q + (zeta6 + 1)*q^2 + (-zeta6 + 3)*q^3 + O(q^4)
            ]

            sage: eps = DirichletGroup(13).0^2
            sage: ModularForms(eps,2).eisenstein_series()
            [
            -7/13*zeta6 - 11/13 + q + (2*zeta6 + 1)*q^2 + (-3*zeta6 + 1)*q^3 + (6*zeta6 - 3)*q^4 - 4*q^5 + O(q^6),
            q + (zeta6 + 2)*q^2 + (-zeta6 + 3)*q^3 + (3*zeta6 + 3)*q^4 + 4*q^5 + O(q^6)
            ]

            sage: M = ModularForms(19,3).eisenstein_subspace()
            sage: M.eisenstein_series()
            [
            ]
        """
        try:
            return self.__eisenstein_series
        except AttributeError:
            P = self.parameters()
            E = Sequence([element.EisensteinSeries(self.change_ring(chi.base_ring()),
                                                      None, t, chi, psi) for \
                                              chi, psi, t in P], immutable=True,
                         cr = True, universe=Objects())
            assert len(E) == self.dimension(), "bug in enumeration of Eisenstein series."
            self.__eisenstein_series = E
            return E

    def _compute_q_expansion_basis(self, prec=None):
        """
        Compute a q-expansion basis for self to precision prec.

        EXAMPLES::

            sage: EisensteinForms(22,4)._compute_q_expansion_basis(6)
            [1 + O(q^6),
            q + 28*q^3 - 8*q^4 + 126*q^5 + O(q^6),
            q^2 + 9*q^4 + O(q^6),
            O(q^6)]
            sage: EisensteinForms(22,4)._compute_q_expansion_basis(15)
            [1 + O(q^15),
            q + 28*q^3 - 8*q^4 + 126*q^5 + 344*q^7 - 72*q^8 + 757*q^9 - 224*q^12 + 2198*q^13 + O(q^15),
            q^2 + 9*q^4 + 28*q^6 + 73*q^8 + 126*q^10 + 252*q^12 + 344*q^14 + O(q^15),
            q^11 + O(q^15)]
        """
        if prec == None:
            prec = self.prec()
        else:
            prec = rings.Integer(prec)

        E = self.eisenstein_series()
        K = self.base_ring()
        V = K**prec
        G = []
        for e in E:
            f = e.q_expansion(prec)
            w = f.padded_list(prec)
            L = f.base_ring()
            if K.has_coerce_map_from(L):
                G.append(V(w))
            else:
                # restrict scalars from L to K
                r,d = cyclotomic_restriction(L,K)
                s = [r(x) for x in w]
                for i in range(d):
                    G.append(V([x[i] for x in s]))

        W = V.submodule(G, check=False)
        R = self._q_expansion_ring()
        X = [R(f.list(), prec) for f in W.basis()]
        return X + [R(0,prec)]*(self.dimension() - len(X))

    def _q_expansion(self, element, prec):
        """
        Compute a q-expansion for a given element of self, expressed
        as a vector of coefficients for the basis vectors of self,
        viewing self as a subspace of the corresponding space of
        modular forms.

        EXAMPLES::

            sage: E = EisensteinForms(17,4)
            sage: (11*E.0 + 3*E.1).q_expansion(20)
            11 + 3*q + 27*q^2 + 84*q^3 + 219*q^4 + 378*q^5 + 756*q^6 + 1032*q^7 + 1755*q^8 + 2271*q^9 + 3402*q^10 + 3996*q^11 + 6132*q^12 + 6594*q^13 + 9288*q^14 + 10584*q^15 + 14043*q^16 + 17379*q^17 + 20439*q^18 + 20580*q^19 + O(q^20)
            sage: E._q_expansion([0,0,0,0,11,3],20)
            11 + 3*q + 27*q^2 + 84*q^3 + 219*q^4 + 378*q^5 + 756*q^6 + 1032*q^7 + 1755*q^8 + 2271*q^9 + 3402*q^10 + 3996*q^11 + 6132*q^12 + 6594*q^13 + 9288*q^14 + 10584*q^15 + 14043*q^16 + 17379*q^17 + 20439*q^18 + 20580*q^19 + O(q^20)
        """
        B = self.q_expansion_basis(prec)
        f = self._q_expansion_zero()
        for i in range(self._start_position, len(element)):
            if element[i] != 0:
                f += element[i] * B[i - self._start_position]
        return f

class EisensteinSubmodule_g0_Q(EisensteinSubmodule_params):
    r"""
    Space of Eisenstein forms for `\Gamma_0(N)`.
    """

class EisensteinSubmodule_g1_Q(EisensteinSubmodule_params):
    r"""
    Space of Eisenstein forms for `\Gamma_1(N)`.
    """
    def _parameters_character(self):
        """
        Return the character defining self. Since self is
        a space of Eisenstein forms on Gamma1(N), the character
        is the trivial one, which we represent by the level.

        EXAMPLES::

            sage: EisensteinForms(Gamma1(7),4)._parameters_character()
            7
        """
        return self.level()

    def _compute_hecke_matrix(self, n, bound=None):
        r"""
        Calculate the matrix of the Hecke operator `T_n` acting on this
        space, via modular symbols.

        INPUT:

        - n: a positive integer

        - bound: an integer such that any element of this space with
          coefficients a_1, ..., a_b all zero must be the zero
          element. If this turns out not to be true, the code will
          increase the bound and try again. Setting bound = None is
          equivalent to setting bound = self.dimension().

        OUTPUT:

        - a matrix (over `\QQ`)

        ALGORITHM:

            This uses the usual pairing between modular symbols and
            modular forms, but in a slightly non-standard way. As for
            cusp forms, we can find a basis for this space made up of
            forms with q-expansions `c_m(f) = a_{i,j}(T_m)`, where
            `T_m` denotes the matrix of the Hecke operator on the
            corresponding modular symbols space. Then `c_m(T_n f) =
            a_{i,j}(T_n* T_m)`. But we can't find the constant terms
            by this method, so an extra step is required.

        EXAMPLE::

            sage: EisensteinForms(Gamma1(6), 3).hecke_matrix(3) # indirect doctest
            [ 1  0 72  0]
            [ 0  0 36 -9]
            [ 0  0  9  0]
            [ 0  1 -4 10]
        """
        # crucial to take sign 0 here
        symbs = self.modular_symbols(sign=0)
        T = symbs.hecke_matrix(n)
        d = symbs.rank()

        if bound is None:
            bound = self.dimension()
        r = bound + 1
        A = self.base_ring()
        X = A**r
        Y = X.zero_submodule()
        basis = []
        basis_images = []

        # we repeatedly use these matrices below, so we store them
        # once as lists to save time.
        hecke_matrix_ls = [ symbs.hecke_matrix(m).list() for m in range(1,r+1) ]
        hecke_image_ls = [ (T*symbs.hecke_matrix(m)).list() for m in range(1,r+1) ]

        # compute the q-expansions of some cusp forms and their
        # images under T_n
        for i in xrange(d**2):
            v = X([ hecke_matrix_ls[m][i] for m in xrange(r) ])
            Ynew = Y.span(Y.basis() + [v])
            if Ynew.rank() > Y.rank():
                basis.append(v)
                basis_images.append(X([ hecke_image_ls[m][i] for m in xrange(r) ]))
                Y = Ynew
                if len(basis) == d:
                    break
        else:
            # if we didn't find a sufficient number of modular forms
            # this way, we simply increase the bound and try again.
            return self._compute_hecke_matrix(n, bound + 5)

        # now we compute the matrix for T_n
        bigmat = Matrix(basis).augment(Matrix(basis_images))
        bigmat.echelonize()
        pivs = bigmat.pivots()
        wrong_mat = bigmat.matrix_from_rows_and_columns(range(d), [ r+x for x in pivs ])

        # this is the matrix in a basis such that projections onto
        # q-expansion coefficients 1...r are echelon, but we want
        # coeffs 0..r echelon (modular symbols don't see the constant
        # term)
        change_mat = Matrix(A, d, [self.basis()[i][j+1] for i in xrange(d) for j in pivs])
        return change_mat * wrong_mat * ~change_mat

class EisensteinSubmodule_eps(EisensteinSubmodule_params):
    """
    Space of Eisenstein forms with given Dirichlet character.

    EXAMPLES::

        sage: e = DirichletGroup(27,CyclotomicField(3)).0**2
        sage: M = ModularForms(e,2,prec=10).eisenstein_subspace()
        sage: M.dimension()
        6

        sage: M.eisenstein_series()
        [
        -1/3*zeta6 - 1/3 + q + (2*zeta6 - 1)*q^2 + q^3 + (-2*zeta6 - 1)*q^4 + (-5*zeta6 + 1)*q^5 + O(q^6),
        -1/3*zeta6 - 1/3 + q^3 + O(q^6),
        q + (-2*zeta6 + 1)*q^2 + (-2*zeta6 - 1)*q^4 + (5*zeta6 - 1)*q^5 + O(q^6),
        q + (zeta6 + 1)*q^2 + 3*q^3 + (zeta6 + 2)*q^4 + (-zeta6 + 5)*q^5 + O(q^6),
        q^3 + O(q^6),
        q + (-zeta6 - 1)*q^2 + (zeta6 + 2)*q^4 + (zeta6 - 5)*q^5 + O(q^6)
        ]
        sage: M.eisenstein_subspace().T(2).matrix().fcp()
        (x + zeta3 + 2) * (x + 2*zeta3 + 1) * (x - 2*zeta3 - 1)^2 * (x - zeta3 - 2)^2
        sage: ModularSymbols(e,2).eisenstein_subspace().T(2).matrix().fcp()
        (x + zeta3 + 2) * (x + 2*zeta3 + 1) * (x - 2*zeta3 - 1)^2 * (x - zeta3 - 2)^2

        sage: M.basis()
        [
        1 - 3*zeta3*q^6 + (-2*zeta3 + 2)*q^9 + O(q^10),
        q + (5*zeta3 + 5)*q^7 + O(q^10),
        q^2 - 2*zeta3*q^8 + O(q^10),
        q^3 + (zeta3 + 2)*q^6 + 3*q^9 + O(q^10),
        q^4 - 2*zeta3*q^7 + O(q^10),
        q^5 + (zeta3 + 1)*q^8 + O(q^10)
        ]

    """
    # TODO
    #def _compute_q_expansion_basis(self, prec):
        #B = EisensteinSubmodule_params._compute_q_expansion_basis(self, prec)
        #raise NotImplementedError, "must restrict scalars down correctly."

from sage.rings.all import CyclotomicField, lcm, euler_phi

def cyclotomic_restriction(L,K):
    r"""
    Given two cyclotomic fields L and K, compute the compositum
    M of K and L, and return a function and the index [M:K]. The
    function is a map that acts as follows (here `M = Q(\zeta_m)`):

    INPUT:

    element alpha in L

    OUTPUT:

    a polynomial `f(x)` in `K[x]` such that `f(\zeta_m) = \alpha`,
    where we view alpha as living in `M`. (Note that `\zeta_m`
    generates `M`, not `L`.)

    EXAMPLES::

        sage: L = CyclotomicField(12) ; N = CyclotomicField(33) ; M = CyclotomicField(132)
        sage: z, n = sage.modular.modform.eisenstein_submodule.cyclotomic_restriction(L,N)
        sage: n
        2

        sage: z(L.0)
        -zeta33^19*x
        sage: z(L.0)(M.0)
        zeta132^11

        sage: z(L.0^3-L.0+1)
        (zeta33^19 + zeta33^8)*x + 1
        sage: z(L.0^3-L.0+1)(M.0)
        zeta132^33 - zeta132^11 + 1
        sage: z(L.0^3-L.0+1)(M.0) - M(L.0^3-L.0+1)
        0
    """
    if not L.has_coerce_map_from(K):
        M = CyclotomicField(lcm(L.zeta_order(), K.zeta_order()))
        f = cyclotomic_restriction_tower(M,K)
        def g(x):
            """
            Function returned by cyclotomic restriction.

            INPUT:

            element alpha in L

            OUTPUT:

            a polynomial `f(x)` in `K[x]` such that `f(\zeta_m) = \alpha`,
            where we view alpha as living in `M`. (Note that `\zeta_m`
            generates `M`, not `L`.)

            EXAMPLES::

                sage: L = CyclotomicField(12)
                sage: N = CyclotomicField(33)
                sage: g, n = sage.modular.modform.eisenstein_submodule.cyclotomic_restriction(L,N)
                sage: g(L.0)
                -zeta33^19*x
            """
            return f(M(x))
        return g, euler_phi(M.zeta_order())//euler_phi(K.zeta_order())
    else:
        return cyclotomic_restriction_tower(L,K), \
               euler_phi(L.zeta_order())//euler_phi(K.zeta_order())

def cyclotomic_restriction_tower(L,K):
    """
    Suppose L/K is an extension of cyclotomic fields and L=Q(zeta_m).
    This function computes a map with the following property:

    INPUT:

    an element alpha in L

    OUTPUT:

    a polynomial `f(x)` in `K[x]` such that `f(zeta_m) = alpha`.

    EXAMPLES::

        sage: L = CyclotomicField(12) ; K = CyclotomicField(6)
        sage: z = sage.modular.modform.eisenstein_submodule.cyclotomic_restriction_tower(L,K)
        sage: z(L.0)
        x
        sage: z(L.0^2+L.0)
        x + zeta6
    """
    if not L.has_coerce_map_from(K):
        raise ValueError, "K must be contained in L"
    f = L.defining_polynomial()
    R = K['x']
    x = R.gen()
    g = R(f)
    h_ls = [ t[0] for t in g.factor() if t[0](L.gen(0)) == 0 ]
    if len(h_ls) == 0:
        raise ValueError, "K (= Q(\zeta_%s)) is not contained in L (= Q(\zeta_%s))"%(K._n(), L._n())
    h = h_ls[0]
    def z(a):
        """
        Function returned by cyclotomic_restriction_tower.

        INPUT:

        an element alpha in L

        OUTPUT:

        a polynomial `f(x)` in `K[x]` such that `f(zeta_m) = alpha`.

        EXAMPLES::

            sage: L = CyclotomicField(121) ; K = CyclotomicField(11)
            sage: z = sage.modular.modform.eisenstein_submodule.cyclotomic_restriction_tower(L,K)
            sage: z(L.0)
            x
            sage: z(L.0^11)
            zeta11
        """
        return R(a.polynomial()) % h
    return z
