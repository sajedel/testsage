"""
Ciphers
"""

#*****************************************************************************
#       Copyright (C) 2007 David Kohel <kohel@maths.usyd.edu.au>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# Ciphers should inherit from morphisms (of sets).
# Specific cipher types will implement their functions in terms of the key

from sage.structure.element import Element

class Cipher(Element):
    """
    Cipher class
    """
    def __init__(self, parent, key):
        """
        Create a cipher.

        INPUT: Parent and key

        EXAMPLES: None yet
        """
        self._parent = parent
        self._key = key

    def __eq__(self, right):
        return type(self) == type(right) and self._parent == right._parent and self._key == right._key

    def _repr_(self):
        r"""
        Return the string representation of this cipher.

        EXAMPLES::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: S(13)
            Shift cipher on Free alphabetic string monoid on A-Z
        """
        # return str(self._key)
        return "Cipher on %s" % self.parent().cipher_domain()

    def key(self):
        return self._key # was str(self._key)

    def domain(self):
        return self._parent.cipher_domain()

    def codomain(self):
        return self._parent().cipher_codomain()

    def parent(self):
        return self._parent

class SymmetricKeyCipher(Cipher):
    """
    Symmetric key cipher class
    """
    def __init__(self, parent, key):
        """
        Create a symmetric cipher

        INPUT: Parent and key

        EXAMPLES: None yet
        """
        Cipher.__init__(self, parent, key)

class PublicKeyCipher(Cipher):
    """
    Public key cipher class
    """
    def __init__(self, parent, key, public = True):
        """
        Create a public key cipher

        INPUT: Parent and key

        EXAMPLES: None yet
        """
        Cipher.__init__(self, parent, key)
        self._public = public