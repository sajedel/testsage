"""
PPL Backend

AUTHORS:

- Risan (2012-02): initial implementation
"""

#*****************************************************************************
#       Copyright (C) 2010 Risan <ptrrsn.1@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.numerical.mip import MIPSolverException
from sage.libs.ppl import MIP_Problem, Variable, Linear_Expression, Constraint, Generator

cdef class PPLBackend(GenericBackend):
    cdef object mip
    cdef list Matrix
    cdef list row_lower_bound
    cdef list row_upper_bound
    cdef list col_lower_bound
    cdef list col_upper_bound
    cdef list objective_function
    cdef list row_name_var
    cdef list col_name_var
    cdef int is_maximize
    cdef str name

    def __cinit__(self, maximization = True):
        """
        Constructor

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram(solver = "PPL")
        """

        self.Matrix = []
        self.row_lower_bound = []
        self.row_upper_bound = []
        self.col_lower_bound = []
        self.col_upper_bound = []
        self.objective_function   = []
        self.row_name_var = []
        self.col_name_var = []
        self.name = ''
        self.obj_constant_term = 0;

        if maximization:
            self.set_sense(+1)
        else:
            self.set_sense(-1)

    cpdef base_ring(self):
        from sage.rings.all import QQ
        return QQ

    cpdef zero(self):
        return self.base_ring()(0)

    def init_mip(self):
        """
        Converting the matrix form of the MIP Problem to PPL MIP_Problem.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.base_ring()
            Rational Field
            sage: type(p.zero())
            <type 'sage.rings.rational.Rational'>
            sage: p.init_mip()

        """

        self.mip = MIP_Problem()
        mip_obj = Linear_Expression(0)

        self.mip.add_space_dimensions_and_embed(len(self.objective_function))
        for i in range(len(self.objective_function)):
            mip_obj = mip_obj + Linear_Expression(self.objective_function[i] * Variable(i))
        self.mip.set_objective_function(mip_obj)
        for i in range(len(self.Matrix)):
            l = Linear_Expression(0)
            for j in range(len(self.Matrix[i])):
                l = l + Linear_Expression(self.Matrix[i][j] * Variable(j))
            if self.row_lower_bound[i] is not None:
                self.mip.add_constraint(l >= self.row_lower_bound[i])
            if self.row_upper_bound[i] is not None:
                self.mip.add_constraint(l <= self.row_upper_bound[i])

        for i in range(len(self.col_lower_bound)):
            if self.col_lower_bound[i] is not None:
                self.mip.add_constraint(Variable(i) >= self.col_lower_bound[i])

        for i in range(len(self.col_upper_bound)):
            if self.col_upper_bound[i] is not None:
                self.mip.add_constraint(Variable(i) <= self.col_upper_bound[i])

        if self.is_maximize == 1:
            self.mip.set_optimization_mode('maximization')
        else:
            self.mip.set_optimization_mode('minimization')

    cpdef int add_variable(self, lower_bound=0, upper_bound=None, binary=False, continuous=True, integer=False, obj=0, name=None) except -1:
        """
        Add a variable.

        This amounts to adding a new column to the matrix. By default,
        the variable is both positive and real.

        It has not been implemented for selecting the variable type yet.

        INPUT:

        - ``lower_bound`` -- the lower bound of the variable (default: 0)

        - ``upper_bound`` -- the upper bound of the variable (default: ``None``)

        - ``binary`` -- ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` -- ``True`` if the variable is binary (default: ``True``).

        - ``integer`` -- ``True`` if the variable is binary (default: ``False``).

        - ``obj`` -- (optional) coefficient of this variable in the objective function (default: 0)

        - ``name`` -- an optional name for the newly added variable (default: ``None``).

        OUTPUT: The index of the newly created variable

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variable()
            0
            sage: p.ncols()
            1
            sage: p.add_variable(lower_bound=-2)
            1
            sage: p.add_variable(name='x',obj=2/3)
            2
            sage: p.col_name(2)
            'x'
            sage: p.objective_coefficient(2)
            2/3
        """
        for i in range(len(self.Matrix)):
            self.Matrix[i].append(0)
        self.col_lower_bound.append(lower_bound)
        self.col_upper_bound.append(upper_bound)
        self.objective_function.append(obj)
        self.col_name_var.append(name)
        return len(self.objective_function) - 1

    cpdef int add_variables(self, int n, lower_bound=0, upper_bound=None, binary=False, continuous=True, integer=False, obj=0, names=None) except -1:
        """
        Add ``n`` variables.

        This amounts to adding new columns to the matrix. By default,
        the variables are both positive and real.

        It has not been implemented for selecting the variable type yet.

        INPUT:

        - ``n`` -- the number of new variables (must be > 0)

        - ``lower_bound`` -- the lower bound of the variable (default: 0)

        - ``upper_bound`` -- the upper bound of the variable (default: ``None``)

        - ``binary`` -- ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` -- ``True`` if the variable is binary (default: ``True``).

        - ``integer`` -- ``True`` if the variable is binary (default: ``False``).

        - ``obj`` -- (optional) coefficient of all variables in the objective function (default: 0)

        - ``names`` -- optional list of names (default: ``None``)

        OUTPUT: The index of the variable created last.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variables(5)
            4
            sage: p.ncols()
            5
            sage: p.add_variables(2, lower_bound=-2.0, names=['a','b'])
            6
        """
        for k in range(n):
            for i in range(len(self.Matrix)):
                self.Matrix[i].append(0)
            self.col_lower_bound.append(lower_bound)
            self.col_upper_bound.append(upper_bound)
            self.objective_function.append(obj)
            if names is not None:
                self.col_name_var.append(names[k])
            else:
                self.col_name_var.append(None)
        return len(self.objective_function) - 1;

    cpdef  set_variable_type(self, int variable, int vtype):
        """
        Set the type of a variable.

        EXAMPLE::

        sage: from sage.numerical.backends.generic_backend import get_solver
        sage: p = get_solver(solver = "PPL")
        sage: p.add_variables(5)
        4
        sage: p.set_variable_type(3, -1)
        sage: p.set_variable_type(3, -2)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        if vtype != -1:
            raise Exception('This backend does not handle integer variables ! Read the doc !')

    cpdef set_sense(self, int sense):
        """
        Set the direction (maximization/minimization).

        INPUT:

        - ``sense`` (integer) :

            * +1 => Maximization
            * -1 => Minimization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.is_maximization()
            True
            sage: p.set_sense(-1)
            sage: p.is_maximization()
            False
        """
        if sense == 1:
            self.is_maximize = 1
        else:
            self.is_maximize = 0

    cpdef objective_coefficient(self, int variable, coeff=None):
        """
        Set or get the coefficient of a variable in the objective
        function

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``coeff`` (integer) -- its coefficient

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variable()
            0
            sage: p.objective_coefficient(0)
            0
            sage: p.objective_coefficient(0,2)
            sage: p.objective_coefficient(0)
            2
        """
        if coeff is not None:
            self.objective_function[variable] = coeff;
        else:
            return self.objective_function[variable]

    cpdef  set_objective(self, list coeff, d = 0):
        """
        Set the objective function.

        INPUT:

        - ``coeff`` -- a list of real values, whose ith element is the
          coefficient of the ith variable in the objective function.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(5)
            4
            sage: p.set_objective([1, 1, 2, 1, 3])
            sage: map(lambda x :p.objective_coefficient(x), range(5))
            [1, 1, 2, 1, 3]
        """
        for i in range(len(coeff)):
            self.objective_function[i] = coeff[i];
        obj_constant_term = d;

    cpdef set_verbosity(self, int level):
        """
        Set the log (verbosity) level. Not Implemented.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.set_verbosity(0)
        """

    cpdef add_linear_constraint(self, coefficients, lower_bound, upper_bound, name=None):
        """
        Add a linear constraint.

        INPUT:

        - ``coefficients`` -- an iterable with ``(c,v)`` pairs where ``c``
          is a variable index (integer) and ``v`` is a value (real
          value).

        - ``lower_bound`` -- a lower bound, either a real value or ``None``

        - ``upper_bound`` -- an upper bound, either a real value or ``None``

        - ``name`` -- an optional name for this row (default: ``None``)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(5)
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2.0, 2.0)
            sage: p.row(0)
            ([1, 2, 3, 4], [1, 2, 3, 4])
            sage: p.row_bounds(0)
            (2.00000000000000, 2.00000000000000)
            sage: p.add_linear_constraint( zip(range(5), range(5)), 1.0, 1.0, name='foo')
            sage: p.row_name(-1)
            'foo'
        """
        last = len(self.Matrix)
        self.Matrix.append([])
        for i in range(len(self.objective_function)):
            self.Matrix[last].append(0)
        for a in coefficients:
            self.Matrix[last][a[0]] = a[1]

        self.row_lower_bound.append(lower_bound)
        self.row_upper_bound.append(upper_bound)
        self.row_name_var.append(name)

    cpdef add_col(self, list indices, list coeffs):
        """
        Add a column.

        INPUT:

        - ``indices`` (list of integers) -- this list constains the
          indices of the constraints in which the variable's
          coefficient is nonzero

        - ``coeffs`` (list of real values) -- associates a coefficient
          to the variable in each of the constraints in which it
          appears. Namely, the ith entry of ``coeffs`` corresponds to
          the coefficient of the variable in the constraint
          represented by the ith entry in ``indices``.

        .. NOTE::

            ``indices`` and ``coeffs`` are expected to be of the same
            length.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.nrows()
            0
            sage: p.add_linear_constraints(5, 0, None)
            sage: p.add_col(range(5), range(5))
            sage: p.nrows()
            5
        """
        for i in range(len(self.Matrix)):
            self.Matrix[i].append(0)
        for i in range(len(indices)):
            self.Matrix[indices[i]][len(self.Matrix[indices[i]]) - 1] = coeffs[i]

        self.col_lower_bound.append(None)
        self.col_upper_bound.append(None)
        self.objective_function.append(0)
        self.col_name_var.append(None)

    cpdef add_linear_constraints(self, int number, lower_bound, upper_bound, names=None):
        """
        Add constraints.

        INPUT:

        - ``number`` (integer) -- the number of constraints to add.

        - ``lower_bound`` -- a lower bound, either a real value or ``None``

        - ``upper_bound`` -- an upper bound, either a real value or ``None``

        - ``names`` -- an optional list of names (default: ``None``)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(5)
            4
            sage: p.add_linear_constraints(5, None, 2)
            sage: p.row(4)
            ([], [])
            sage: p.row_bounds(4)
            (None, 2)
        """
        for i in range(number):
            self.Matrix.append([])
            for j in range(len(self.objective_function)):
                self.Matrix[i].append(0)
            self.row_lower_bound.append(lower_bound)
            self.row_upper_bound.append(upper_bound)
            if names is not None:
                self.row_name_var.append(names)
            else:
                self.row_name_var.append(None)

    cpdef int solve(self) except -1:
        """
        Solve the problem.

        .. NOTE::

            This method raises ``MIPSolverException`` exceptions when
            the solution can not be computed for any reason (none
            exists, or the LP solver was not able to find it, etc...)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_linear_constraints(5, 0, None)
            sage: p.add_col(range(5), range(5))
            sage: p.solve()
            0
            sage: p.objective_coefficient(0,1)
            sage: p.solve()
            Traceback (most recent call last):
            ...
            MIPSolverException: ...
        """
        self.init_mip()

        ans = self.mip.solve()

        if ans['status'] == 'optimized':
            pass
        elif ans['status'] == 'unbounded':
            raise MIPSolverException("PPL : Solution is unbounded")
        elif ans['status'] == 'unfeasible':
            raise MIPSolverException("PPL : There is no feasible solution")

        return 0

    cpdef get_objective_value(self):
        """
        Return the exact value of the objective function.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(2)
            1
            sage: p.add_linear_constraint([(0,1), (1,2)], None, 3)
            sage: p.set_objective([2, 5])
            sage: p.solve()
            0
            sage: p.get_objective_value()
            15/2
            sage: p.get_variable_value(0)
            0
            sage: p.get_variable_value(1)
            3/2
        """
        self.init_mip()
        ans = self.mip.optimal_value()
        return ans + self.obj_constant_term

    cpdef get_variable_value(self, int variable):
        """
        Return the value of a variable given by the solver.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(2)
            1
            sage: p.add_linear_constraint([(0,1), (1, 2)], None, 3)
            sage: p.set_objective([2, 5])
            sage: p.solve()
            0
            sage: p.get_objective_value()
            15/2
            sage: p.get_variable_value(0)
            0
            sage: p.get_variable_value(1)
            3/2
        """
        self.init_mip()
        g = self.mip.optimizing_point()
        return g.coefficient(Variable(variable)) / g.divisor()

    cpdef int ncols(self):
        """
        Return the number of columns/variables.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variables(2)
            1
            sage: p.ncols()
            2
        """
        return len(self.objective_function)

    cpdef int nrows(self):
        """
        Return the number of rows/constraints.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.nrows()
            0
            sage: p.add_linear_constraints(2, 2.0, None)
            sage: p.nrows()
            2
        """
        return len(self.Matrix)

    cpdef bint is_maximization(self):
        """
        Test whether the problem is a maximization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.is_maximization()
            True
            sage: p.set_sense(-1)
            sage: p.is_maximization()
            False
        """
        if self.is_maximize == 1:
            return 1
        else:
            return 0

    cpdef problem_name(self, char * name = NULL):
        """
        Return or define the problem's name

        INPUT:

        - ``name`` (``char *``) -- the problem's name. When set to
          ``NULL`` (default), the method returns the problem's name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.problem_name("There once was a french fry")
            sage: print p.problem_name()
            There once was a french fry
        """
        if name == NULL:
            return self.name
        self.name = <str>name

    cpdef row(self, int i):
        """
        Return a row

        INPUT:

        - ``index`` (integer) -- the constraint's id.

        OUTPUT:

        A pair ``(indices, coeffs)`` where ``indices`` lists the
        entries whose coefficient is nonzero, and to which ``coeffs``
        associates their coefficient on the model of the
        ``add_linear_constraint`` method.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(5)
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2, 2)
            sage: p.row(0)
            ([1, 2, 3, 4], [1, 2, 3, 4])
            sage: p.row_bounds(0)
            (2, 2)
        """
        idx = []
        coef = []
        for j in range(len(self.Matrix[i])):
            if self.Matrix[i][j] != 0:
                idx.append(j)
                coef.append(self.Matrix[i][j])
        return (idx, coef)

    cpdef row_bounds(self, int index):
        """
        Return the bounds of a specific constraint.

        INPUT:

        - ``index`` (integer) -- the constraint's id.

        OUTPUT:

        A pair ``(lower_bound, upper_bound)``. Each of them can be set
        to ``None`` if the constraint is not bounded in the
        corresponding direction, and is a real value otherwise.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variables(5)
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2, 2)
            sage: p.row(0)
            ([1, 2, 3, 4], [1, 2, 3, 4])
            sage: p.row_bounds(0)
            (2, 2)
        """
        return (self.row_lower_bound[index], self.row_upper_bound[index])

    cpdef col_bounds(self, int index):
        """
        Return the bounds of a specific variable.

        INPUT:

        - ``index`` (integer) -- the variable's id.

        OUTPUT:

        A pair ``(lower_bound, upper_bound)``. Each of them can be set
        to ``None`` if the variable is not bounded in the
        corresponding direction, and is a real value otherwise.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variable()
            0
            sage: p.col_bounds(0)
            (0, None)
            sage: p.variable_upper_bound(0, 5)
            sage: p.col_bounds(0)
            (0, 5)
        """
        return (self.col_lower_bound[index], self.col_upper_bound[index])

    cpdef bint is_variable_binary(self, int index):
        """
        Test whether the given variable is of binary type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variable()
            0
            sage: p.is_variable_binary(0)
            False
        """
        return False

    cpdef bint is_variable_integer(self, int index):
        """
        Test whether the given variable is of integer type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variable()
            0
            sage: p.is_variable_integer(0)
            False
        """
        return False

    cpdef bint is_variable_continuous(self, int index):
        """
        Test whether the given variable is of continuous/real type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.ncols()
            0
            sage: p.add_variable()
            0
            sage: p.is_variable_continuous(0)
            True
        """
        return True

    cpdef row_name(self, int index):
        """
        Return the ``index`` th row name

        INPUT:

        - ``index`` (integer) -- the row's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_linear_constraints(1, 2, None, names="Empty constraint 1")
            sage: p.row_name(0)
            'Empty constraint 1'
        """
        if self.row_name_var[index] is not None:
            return self.row_name_var[index]
        return "constraint_" + repr(index)

    cpdef col_name(self, int index):
        """
        Return the ``index`` th col name

        INPUT:

        - ``index`` (integer) -- the col's id

        - ``name`` (``char *``) -- its name. When set to ``NULL``
          (default), the method returns the current name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variable(name="I am a variable")
            0
            sage: p.col_name(0)
            'I am a variable'
        """
        if self.col_name_var[index] is not None:
            return self.col_name_var[index]
        return "x_" + repr(index)

    cpdef variable_upper_bound(self, int index, value = False):
        """
        Return or define the upper bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not upper bound. When set to ``None``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variable()
            0
            sage: p.col_bounds(0)
            (0, None)
            sage: p.variable_upper_bound(0, 5)
            sage: p.col_bounds(0)
            (0, 5)
            sage: p.variable_upper_bound(0, None)
            sage: p.col_bounds(0)
            (0, None)
        """
        if value is not False:
            self.col_upper_bound[index] = value
        else:
            return self.col_upper_bound[index]

    cpdef variable_lower_bound(self, int index, value = False):
        """
        Return or define the lower bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not lower bound. When set to ``None``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "PPL")
            sage: p.add_variable()
            0
            sage: p.col_bounds(0)
            (0, None)
            sage: p.variable_lower_bound(0, 5)
            sage: p.col_bounds(0)
            (5, None)
            sage: p.variable_lower_bound(0, None)
            sage: p.col_bounds(0)
            (None, None)
        """
        if value is not False:
            self.col_lower_bound[index] = value
        else:
            return self.col_lower_bound[index]
