include "../../libs/ntl/decl.pxi"

from sage.rings.padics.padic_ZZ_pX_element cimport pAdicZZpXElement
from sage.structure.element cimport RingElement, ModuleElement

cdef class pAdicZZpXFMElement(pAdicZZpXElement):
    cdef ZZ_pX_c value
    cdef pAdicZZpXFMElement _new_c(self)
    cdef pAdicZZpXFMElement _lshift_c(self, long n, bint top_zeros)
    cdef pAdicZZpXFMElement _rshift_c(self, long n, bint top_zeros)
    cdef pAdicZZpXFMElement _unit_part_c(self, bint top_zeros)
    cdef RingElement _invert_c_impl(self)
