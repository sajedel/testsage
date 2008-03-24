"""
Ambient Jacobian Abelian Variety

TESTS:
    sage: loads(dumps(J0(37))) == J0(37)
    True
    sage: loads(dumps(J1(13))) == J1(13)
    True
"""

import weakref

from abvar             import ModularAbelianVariety_modsym_abstract, ModularAbelianVariety
from sage.rings.all    import QQ
from sage.modular.dims import dimension_cusp_forms

from sage.modular.modsym.modsym import ModularSymbols
import morphism

_cache = {}

def ModAbVar_ambient_jacobian(group):
    """
    Return the ambient Jacobian attached to a given congruence
    subgroup.

    The result is cached using a weakref.  This function is called
    internally by modular abelian variety constructors.

    INPUT:
        group -- a congruence subgroup.

    OUTPUT:
        a modular abelian variety attached

    EXAMPLES:
        sage: import sage.modular.abvar.abvar_ambient_jacobian as abvar_ambient_jacobian
        sage: A = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A
        Abelian variety J0(11) of dimension 1
        sage: B = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A is B
        True

    You can get access to and/or clear the cache as follows:
        sage: abvar_ambient_jacobian._cache = {}
        sage: B = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A is B
        False
    """
    try:
        X = _cache[group]()
        if not X is None:
            return X
    except KeyError:
        pass
    X = ModAbVar_ambient_jacobian_class(group)
    _cache[group] = weakref.ref(X)
    return X

class ModAbVar_ambient_jacobian_class(ModularAbelianVariety_modsym_abstract):
    """
    An ambient Jacobian modular abelian variety attached to a
    congruence subgroup.
    """
    def __init__(self, group):
        """
        Create an ambient Jacobian modular abelian variety.

        EXAMPLES:
            sage: A = J0(37); A
            Abelian variety J0(37) of dimension 2
            sage: type(A)
            <class 'sage.modular.abvar.abvar_ambient_jacobian.ModAbVar_ambient_jacobian_class'>
            sage: A.group()
            Congruence Subgroup Gamma0(37)
        """
        ModularAbelianVariety_modsym_abstract.__init__(self, (group,), QQ)
        self.__group = group
        self._is_hecke_stable = True

    def _modular_symbols(self):
        """
        Return the modular symbols space associated to this ambient Jacobian.

        OUTPUT:
            modular symbols space

        EXAMPLES:
            sage: M = J0(33)._modular_symbols(); M
            Modular Symbols subspace of dimension 6 of Modular Symbols space of dimension 9 for Gamma_0(33) of weight 2 with sign 0 over Rational Field
            sage: J0(33)._modular_symbols() is M
            True
        """
        try:
            return self.__modsym
        except AttributeError:
            self.__modsym = ModularSymbols(self.__group, weight=2).cuspidal_submodule()
            return self.__modsym

    def _repr_(self):
        """
        Return string representation of this Jacobian modular abelian
        variety.

        EXAMPLES:
            sage: A = J0(11); A
            Abelian variety J0(11) of dimension 1
            sage: A._repr_()
            'Abelian variety J0(11) of dimension 1'
            sage: A.rename("J_0(11)")
            sage: A
            J_0(11)

        We now clear the cache to get rid of our renamed $J_0(11)$.
            sage: import sage.modular.abvar.abvar_ambient_jacobian as abvar_ambient_jacobian
            sage: abvar_ambient_jacobian._cache = {}
        """
        return 'Abelian variety %s of dimension %s%s'%(self._ambient_repr(), self.dimension(),
                                    '' if self.base_field() == QQ else ' over %s'%self.base_field())

    def _latex_(self):
        """
        Return Latex representation of self.

        EXAMPLES:
            sage: latex(J0(37))
            J_0(37)
            sage: J1(13)._latex_()
            'J_1(13)'
            sage: latex(JH(389,[2]))
            J_H(389,[2])
        """
        return self._ambient_latex_repr()

    def ambient_variety(self):
        """
        Return the ambient modular abelian variety that contains self.
        Since self is a Jacobian modular abelian variety, this is just
        self.

        OUTPUT:
            abelian variety

        EXAMPLES:
            sage: A = J0(11)
            sage: A.ambient_variety()
            Abelian variety J0(11) of dimension 1
            sage: A is A.ambient_variety()
            True
        """
        return self

    def group(self):
        """
        Return the group that this Jacobian modular abelian variety
        is attached to.

        EXAMPLES:
            sage: J1(37).group()
            Congruence Subgroup Gamma1(37)
            sage: J0(5077).group()
            Congruence Subgroup Gamma0(5077)
            sage: J = GammaH(11,[3]).modular_abelian_variety(); J
            Abelian variety JH(11,[3]) of dimension 1
            sage: J.group()
            Congruence Subgroup Gamma_H(11) with H generated by [3]
        """
        return self.__group

    def groups(self):
        """
        Return the tuple of congruence subgroups attached to this
        ambient Jacobian.  This is always a tuple of length 1.

        OUTPUT:
            tuple

        EXAMPLES:
            sage: J0(37).groups()
            (Congruence Subgroup Gamma0(37),)
        """
        return (self.__group,)

    def degeneracy_map(self, level, t=1, check=True):
        """
        Return the t-th degeneracy map from self to J(level).  Here t
        must be a divisor of either level/self.level() or
        self.level()/level.

        INPUT:
            level -- integer (multiple or divisor of level of self)
            t -- divisor of quotient of level of self and level
            check -- bool (default: True); if True do some checks on the input

        OUTPUT:
            a morphism

        EXAMPLES:
            sage: J0(11).degeneracy_map(33)
            Abelian variety morphism:
              From: Abelian variety J0(11) of dimension 1
              To:   Abelian variety J0(33) of dimension 3
            sage: J0(11).degeneracy_map(33).matrix()
            [ 0 -3  2  1 -2  0]
            [ 1 -2  0  1  0 -1]
            sage: J0(11).degeneracy_map(33,3).matrix()
            [-1  0  0  0  1 -2]
            [-1 -1  1 -1  1  0]
            sage: J0(33).degeneracy_map(11,1).matrix()
            [ 0  1]
            [ 0 -1]
            [ 1 -1]
            [ 0  1]
            [-1  1]
            [ 0  0]
            sage: J0(11).degeneracy_map(33,1).matrix() * J0(33).degeneracy_map(11,1).matrix()
            [4 0]
            [0 4]
        """
        if check:
            if (level % self.level()) and (self.level() % level):
                raise ValueError, "level must be divisible by level of self"
            if (max(level,self.level()) // min(self.level(),level)) % t:
                raise ValueError, "t must divide the quotient of the two levels"

        Mself = self.modular_symbols()
        #Jdest = Mself.ambient_module().modular_symbols_of_level(level).cuspidal_subspace().abelian_variety()
        Jdest = (type(Mself.group()))(level).modular_abelian_variety()
        Mdest = Jdest.modular_symbols()

        symbol_map = Mself.degeneracy_map(level, t).restrict_codomain(Mdest)
        H = self.Hom(Jdest)

        return H(morphism.Morphism(H,symbol_map.matrix()))

    def dimension(self):
        """
        Return the dimension of this modular abelian variety.

        EXAMPLES:
            sage: J0(2007).dimension()
            221
            sage: J1(13).dimension()
            2
            sage: J1(997).dimension()
            40920
            sage: J0(389).dimension()
            32
            sage: JH(389,[4]).dimension()
            64
            sage: J1(389).dimension()
            6112
        """
        try:
            return self._dimension
        except AttributeError:
            d = dimension_cusp_forms(self.group(), k=2)
            self._dimension = d
            return d
