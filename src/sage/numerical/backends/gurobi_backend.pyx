"""
Gurobi Backend

AUTHORS:

- Nathann Cohen (2011-10): initial implementation
"""

##############################################################################
#       Copyright (C) 2010 Nathann Cohen <nathann.cohen@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

from sage.numerical.mip import MIPSolverException

cdef class GurobiBackend(GenericBackend):
    def __cinit__(self, maximization = True):
        """
        Constructor

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram(solver="Gurobi")            # optional - GUROBI
        """
        cdef int error

        cdef GRBenv ** env
        env = <GRBenv **> sage_malloc(sizeof(GRBenv *))

        error = GRBloadenv(env, NULL)

        if error or (env[0] == NULL):
            raise Exception("Could not initialize Gurobi environment")

        self.model = <GRBmodel **> sage_malloc(sizeof(GRBmodel *))
        error = GRBnewmodel(env[0], self.model, NULL, 0, NULL, NULL, NULL, NULL, NULL)

        self.env = GRBgetenv (self.model[0])

        if error:
            raise Exception("Could not initialize Gurobi model")

        if maximization:
            error = GRBsetintattr(self.model[0], "ModelSense", -1)
        else:
            error = GRBsetintattr(self.model[0], "ModelSense", +1)

        check(self.env, error)

        self.set_sense(1 if maximization else -1)

        self.set_verbosity(0)

    cpdef int add_variable(self, lower_bound=0.0, upper_bound=None, binary=False, continuous=False, integer=False, obj=0.0, name=None) except -1:
        """
        Add a variable.

        This amounts to adding a new column to the matrix. By default,
        the variable is both positive, real and the coefficient in the
        objective function is 0.0.

        INPUT:

        - ``lower_bound`` - the lower bound of the variable (default: 0)

        - ``upper_bound`` - the upper bound of the variable (default: ``None``)

        - ``binary`` - ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` - ``True`` if the variable is binary (default: ``True``).

        - ``integer`` - ``True`` if the variable is binary (default: ``False``).

        - ``obj`` - (optional) coefficient of this variable in the objective function (default: 0.0)

        - ``name`` - an optional name for the newly added variable (default: ``None``).

        OUTPUT: The index of the newly created variable

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                              # optional - GUROBI
            sage: p.ncols()                                                      # optional - GUROBI
            0
            sage: p.add_variable()                                               # optional - GUROBI
            0
            sage: p.ncols()                                                      # optional - GUROBI
            1
            sage: p.add_variable(binary=True)                                    # optional - GUROBI
            1
            sage: p.add_variable(lower_bound=-2.0, integer=True)                 # optional - GUROBI
            2
            sage: p.add_variable(continuous=True, integer=True)                  # optional - GUROBI
            Traceback (most recent call last):
            ...
            ValueError: ...
            sage: p.add_variable(name='x',obj=1.0)                               # optional - GUROBI
            3
            sage: p.col_name(3)                                                  # optional - GUROBI
            'x'
            sage: p.objective_coefficient(3)                                     # optional - GUROBI
            1.0
        """
        # Checking the input
        cdef char vtype = int(bool(binary)) + int(bool(continuous)) + int(bool(integer))
        if  vtype == 0:
            continuous = True
        elif vtype != 1:
            raise ValueError("Exactly one parameter of 'binary', 'integer' and 'continuous' must be 'True'.")

        cdef int error

        if binary:
            vtype = GRB_BINARY
        elif continuous:
            vtype = GRB_CONTINUOUS
        elif integer:
            vtype = GRB_INTEGER

        cdef char * c_name = ""

        if name is None:
            name = "x_"+str(self.ncols())

        c_name = name

        if upper_bound is None:
            upper_bound = GRB_INFINITY
        if lower_bound is None:
            lower_bound = -GRB_INFINITY

        error = GRBaddvar(self.model[0], 0, NULL, NULL, obj, <double> lower_bound, <double> upper_bound, vtype, c_name)

        check(self.env,error)

        check(self.env,GRBupdatemodel(self.model[0]))

        return self.ncols()-1

    cpdef int add_variables(self, int number, lower_bound=0.0, upper_bound=None, binary=False, continuous=False, integer=False, obj=0.0, names=None) except -1:
        """
        Add ``number`` new variables.

        This amounts to adding new columns to the matrix. By default,
        the variables are both positive, real and theor coefficient in
        the objective function is 0.0.

        INPUT:

        - ``n`` - the number of new variables (must be > 0)

        - ``lower_bound`` - the lower bound of the variable (default: 0)

        - ``upper_bound`` - the upper bound of the variable (default: ``None``)

        - ``binary`` - ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` - ``True`` if the variable is binary (default: ``True``).

        - ``integer`` - ``True`` if the variable is binary (default: ``False``).

        - ``obj`` - (optional) coefficient of all variables in the objective function (default: 0.0)

        - ``names`` - optional list of names (default: ``None``)

        OUTPUT: The index of the variable created last.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver           # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                        # optional - GUROBI
            sage: p.ncols()                                                                # optional - GUROBI
            0
            sage: p.add_variables(5)                                                       # optional - GUROBI
            4
            sage: p.ncols()                                                                # optional - GUROBI
            5
            sage: p.add_variables(2, lower_bound=-2.0, integer=True, names=['a','b'])      # optional - GUROBI
            6
        """
        cdef int i
        cdef int value
        for i in range(number):
            value = self.add_variable(lower_bound = lower_bound,
                              upper_bound = upper_bound,
                              binary = binary,
                              continuous = continuous,
                              integer = integer,
                              obj = obj,
                              name = None if names is None else names[i])
        return value
#        cdef double * p_obj = NULL
#        cdef double * p_lb = NULL
#        cdef double * p_ub = NULL
#        cdef char ** p_names = NULL
#        cdef char * p_types = NULL
#        cdef int i
#        cdef int error
#
#        cdef int NAME_MAX_LEN = 50
#
#        # Objective coefficients
#        if obj:
#            p_obj = <double*> sage_malloc(number*sizeof(double))
#            for i in range(number):
#                p_obj[i] = obj
#
#        # Lower bounds
#        if lower_bound != 0:
#            p_lb = <double*> sage_malloc(number*sizeof(double))
#            for i in range(number):
#                p_lb[i] = -GRB_INFINITY if lower_bound is None else lower_bound
#
#        # Upper bounds
#        if not upper_bound is None:
#            p_ub = <double*> sage_malloc(number*sizeof(double))
#            for i in range(number):
#                p_ub[i] = upper_bound
#
#        # Type
#        if not continuous:
#            p_types = <char *> sage_malloc(number*sizeof(char))
#            if binary:
#                p_types[0] = GRB_BINARY
#            else:
#                p_types[0] = GRB_INTEGER
#
#            for i in range(2, number):
#                p_types[i] = p_types[i-1]
#
#        # Names
#        if not names is None:
#            p_names = <char **> sage_malloc((number+1)*sizeof(char *))
#            p_names[0] = <char *> sage_malloc(number*NAME_MAX_LEN*sizeof(char))
#            for i, name in enumerate(names):
#                p_names[i+1] = p_names[i] + NAME_MAX_LEN
#                p_names[i][0] = str(name)
#
#        error = GRBaddvars (self.model[0], number, 0, NULL, NULL, NULL, p_obj, p_lb, p_ub, p_types, p_names)
#
#        # Freeing the memory
#        if p_obj != NULL:
#            sage_free(p_obj)
#        if p_lb != NULL:
#            sage_free(p_lb)
#        if p_ub != NULL:
#            sage_free(p_ub)
#        if p_names != NULL:
#            for i in range(number+1):
#                sage_free(p_names[i])
#            sage_free(p_names)
#        if p_types != NULL:
#            sage_free(p_types)
#
#        check(self.env, error)

    cpdef set_variable_type(self, int variable, int vtype):
        """
        Set the type of a variable

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``vtype`` (integer) :

            *  1  Integer
            *  0  Binary
            * -1 Real

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.ncols()                                                       # optional - GUROBI
            0
            sage: p.add_variable()                                                # optional - GUROBI
            0
            sage: p.set_variable_type(0,1)                                        # optional - GUROBI
            sage: p.is_variable_integer(0)                                        # optional - GUROBI
            True
        """
        cdef int error

        if vtype == 1:
            error = GRBsetcharattrelement(self.model[0], "VType", variable, 'I')
        elif vtype == 0:
            error = GRBsetcharattrelement(self.model[0], "VType", variable, 'B')
        else:
            error = GRBsetcharattrelement(self.model[0], "VType", variable, 'C')
        check(self.env, error)

        check(self.env,GRBupdatemodel(self.model[0]))

    cpdef set_sense(self, int sense):
        """
        Set the direction (maximization/minimization).

        INPUT:

        - ``sense`` (integer) :

            * +1 => Maximization
            * -1 => Minimization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.is_maximization()                                              # optional - GUROBI
            True
            sage: p.set_sense(-1)                                                  # optional - GUROBI
            sage: p.is_maximization()                                              # optional - GUROBI
            False
        """
        cdef int error

        if sense == 1:
            error = GRBsetintattr(self.model[0], "ModelSense", -1)
        else:
            error = GRBsetintattr(self.model[0], "ModelSense", +1)

        check(self.env, error)
        check(self.env,GRBupdatemodel(self.model[0]))

    cpdef objective_coefficient(self, int variable, coeff=None):
        """
        Set or get the coefficient of a variable in the objective function

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``coeff`` (double) -- its coefficient or ``None`` for
          reading (default: ``None``)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.add_variable()                                                 # optional - GUROBI
            0
            sage: p.objective_coefficient(0) == 0                                  # optional - GUROBI
            True
            sage: p.objective_coefficient(0,2)                                     # optional - GUROBI
            sage: p.objective_coefficient(0)                                       # optional - GUROBI
            2.0
        """
        cdef int error
        cdef double value[1]

        if coeff:
            error = GRBsetdblattrelement(self.model[0], "Obj", variable, coeff)
            check(self.env, error)
            check(self.env,GRBupdatemodel(self.model[0]))
        else:
            error = GRBgetdblattrelement(self.model[0], "Obj", variable, value)
            check(self.env, error)
            return value[0]

    cpdef problem_name(self, char * name = NULL):
        """
        Return or define the problem's name

        INPUT:

        - ``name`` (``char *``) -- the problem's name. When set to
          ``NULL`` (default), the method returns the problem's name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver      # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                   # optional - GUROBI
            sage: p.problem_name("There once was a french fry")                       # optional - GUROBI
            sage: print p.problem_name()                                              # optional - GUROBI
            There once was a french fry

        TESTS::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: print p.problem_name()                                            # optional - GUROBI
        """
        cdef int error
        cdef char * pp_name[1]

        if name:
            error = GRBsetstrattr(self.model[0], "ModelName", name)
            check(self.env, error)
            check(self.env,GRBupdatemodel(self.model[0]))

        else:
            check(self.env,GRBgetstrattr(self.model[0], "ModelName", <char **> pp_name))
            if pp_name[0] == NULL:
                value = ""
            else:
                value = str(pp_name[0])

            return value

    cpdef set_objective(self, list coeff):
        """
        Set the objective function.

        INPUT:

        - ``coeff`` - a list of real values, whose ith element is the
          coefficient of the ith variable in the objective function.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver     # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                  # optional - GUROBI
            sage: p.add_variables(5)                                                 # optional - GUROBI
            4
            sage: p.set_objective([1, 1, 2, 1, 3])                                   # optional - GUROBI
            sage: map(lambda x :p.objective_coefficient(x), range(5))                # optional - GUROBI
            [1.0, 1.0, 2.0, 1.0, 3.0]
        """
        cdef int i = 0
        cdef double value
        cdef int error

        for value in coeff:
            error = GRBsetdblattrelement (self.model[0], "Obj", i, value)
            check(self.env,error)
            i += 1

        check(self.env,GRBupdatemodel(self.model[0]))

    cpdef set_verbosity(self, int level):
        """
        Set the verbosity level

        INPUT:

        - ``level`` (integer) -- From 0 (no verbosity) to 3.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.set_verbosity(2)                                               # optional - GUROBI

        """
        cdef int error
        if level:
            error = GRBsetintparam(self.env, "OutputFlag", 1)
        else:
            error = GRBsetintparam(self.env, "OutputFlag", 0)

        check(self.env, error)

    cpdef add_linear_constraint(self, coefficients, lower_bound, upper_bound, name=None):
        """
        Add a linear constraint.

        INPUT:

        - ``coefficients`` an iterable with ``(c,v)`` pairs where ``c``
          is a variable index (integer) and ``v`` is a value (real
          value).

        - ``lower_bound`` - a lower bound, either a real value or ``None``

        - ``upper_bound`` - an upper bound, either a real value or ``None``

        - ``name`` - an optional name for this row (default: ``None``)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver          # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                       # optional - GUROBI
            sage: p.add_variables(5)                                                      # optional - GUROBI
            4
            sage: p.add_linear_constraint( zip(range(5), range(5)), 2.0, 2.0)             # optional - GUROBI
            sage: p.row(0)                                                                # optional - GUROBI
            ([0, 1, 2, 3, 4], [0.0, 1.0, 2.0, 3.0, 4.0])
            sage: p.row_bounds(0)                                                         # optional - GUROBI
            (2.0, 2.0)
            sage: p.add_linear_constraint( zip(range(5), range(5)), 1.0, 1.0, name='foo') # optional - GUROBI
            sage: p.row_name(1)                                                           # optional - GUROBI
            'foo'
        """

        if lower_bound is None and upper_bound is None:
            raise ValueError("At least one of 'upper_bound' or 'lower_bound' must be set.")

        cdef int * row_i
        cdef double * row_values

        row_i = <int *> sage_malloc((len(coefficients)) * sizeof(int))
        row_values = <double *> sage_malloc((len(coefficients)) * sizeof(double))

        for i,(c,v) in enumerate(coefficients):
            row_i[i] = c
            row_values[i] = v

        if name is None:
            name = ""

        if upper_bound is not None and lower_bound is None:
            error = GRBaddconstr(self.model[0], len(coefficients), row_i, row_values, GRB_LESS_EQUAL, <double> upper_bound, name)

        elif lower_bound is not None and upper_bound is None:
            error = GRBaddconstr(self.model[0], len(coefficients), row_i, row_values, GRB_GREATER_EQUAL, <double> lower_bound, name)

        elif upper_bound is not None and lower_bound is not None:
            if lower_bound == upper_bound:
                error = GRBaddconstr(self.model[0], len(coefficients), row_i, row_values, GRB_EQUAL, <double> lower_bound, name)

            else:
                error = GRBaddrangeconstr(self.model[0], len(coefficients), row_i, row_values, <double> lower_bound, <double> upper_bound, name)

        check(self.env,error)

        error = GRBupdatemodel(self.model[0])

        check(self.env,error)

        sage_free(row_i)
        sage_free(row_values)

    cpdef row(self, int index):
        r"""
        Return a row

        INPUT:

        - ``index`` (integer) -- the constraint's id.

        OUTPUT:

        A pair ``(indices, coeffs)`` where ``indices`` lists the
        entries whose coefficient is nonzero, and to which ``coeffs``
        associates their coefficient on the model of the
        ``add_linear_constraint`` method.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.add_variables(5)                                               # optional - GUROBI
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2, 2)           # optional - GUROBI
            sage: p.row(0)                                                         # optional - GUROBI
            ([0, 1, 2, 3, 4], [0.0, 1.0, 2.0, 3.0, 4.0])
            sage: p.row_bounds(0)                                                  # optional - GUROBI
            (2.0, 2.0)
        """
        cdef int error
        cdef int fake[1]

        cdef int length[1]
        error =  GRBgetconstrs(self.model[0], length, NULL, NULL, NULL, index, 1 )
        check(self.env,error)

        cdef int * p_indices = <int *> sage_malloc(length[0] * sizeof(int))
        cdef double * p_values = <double *> sage_malloc(length[0] * sizeof(double))

        error =  GRBgetconstrs(self.model[0], length, <int *> fake, p_indices, p_values, index, 1 )
        check(self.env,error)

        cdef list indices = []
        cdef list values = []

        cdef int i
        for i in range(length[0]):
            indices.append(p_indices[i])
            values.append(p_values[i])

        sage_free(p_indices)
        sage_free(p_values)

        return indices, values

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

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variables(5)                                                # optional - GUROBI
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2, 2)            # optional - GUROBI
            sage: p.row(0)                                                          # optional - GUROBI
            ([0, 1, 2, 3, 4], [0.0, 1.0, 2.0, 3.0, 4.0])
            sage: p.row_bounds(0)                                                   # optional - GUROBI
            (2.0, 2.0)
        """
        cdef double d[1]
        cdef char sense[1]
        cdef int error

        error = GRBgetcharattrelement(self.model[0], "Sense", index, <char *> sense)
        check(self.env, error)

        error = GRBgetdblattrelement(self.model[0], "RHS", index, <double *> d)
        check(self.env, error)

        if sense[0] == '>':
            return (d[0], None)
        elif sense[0] == '<':
            return (None, d[0])
        else:
            return (d[0],d[0])

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

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variable()                                                  # optional - GUROBI
            0
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (0.0, None)
            sage: p.variable_upper_bound(0, 5)                                      # optional - GUROBI
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (0.0, 5.0)
        """

        cdef double lb[1], ub[1]

        error = GRBgetdblattrelement(self.model[0], "LB", index, <double *> lb)
        check(self.env, error)

        error = GRBgetdblattrelement(self.model[0], "UB", index, <double *> ub)
        check(self.env, error)

        return (None if lb[0] <= -2147483647 else lb[0],
                None if  (<int> ub[0]) >= 2147483647 else ub[0])

    cpdef int solve(self) except -1:
        """
        Solve the problem.

        .. NOTE::

            This method raises ``MIPSolverException`` exceptions when
            the solution can not be computed for any reason (none
            exists, or the LP solver was not able to find it, etc...)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.add_variables(5)                                              # optional - GUROBI
            4
            sage: p.add_linear_constraint([(0,1), (1, 1)], 1.2, 1.7)              # optional - GUROBI
            sage: p.set_variable_type(0, 1)                                       # optional - GUROBI
            sage: p.set_variable_type(1, 1)                                       # optional - GUROBI
            sage: p.solve()                                                       # optional - GUROBI
            Traceback (most recent call last):
            ...
            MIPSolverException: 'Gurobi: The problem is infeasible'
        """
        cdef int error
        global mip_status

        check(self.env, GRBoptimize(self.model[0]))

        cdef int status[1]
        check(self.env, GRBgetintattr(self.model[0], "Status", <int *> status))

        # Has there been a problem ?
        if status[0] != GRB_OPTIMAL:
            raise MIPSolverException("Gurobi: "+mip_status.get(status[0], "unknown error during call to GRBoptimize : "+str(status[0])))

    cpdef double get_objective_value(self):
        """
        Returns the value of the objective function.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.add_variables(2)                                              # optional - GUROBI
            1
            sage: p.add_linear_constraint([[0, 1], [1, 2]], None, 3)              # optional - GUROBI
            sage: p.set_objective([2, 5])                                         # optional - GUROBI
            sage: p.solve()                                                       # optional - GUROBI
            0
            sage: p.get_objective_value()                                         # optional - GUROBI
            7.5
            sage: p.get_variable_value(0)                                         # optional - GUROBI
            0.0
            sage: p.get_variable_value(1)                                         # optional - GUROBI
            1.5
        """
        cdef double p_value[1]

        check(self.env,GRBgetdblattr(self.model[0], "ObjVal", <double* >p_value))

        return p_value[0]

    cpdef double get_variable_value(self, int variable):
        """
        Returns the value of a variable given by the solver.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.add_variables(2)                                               # optional - GUROBI
            1
            sage: p.add_linear_constraint([[0, 1], [1, 2]], None, 3)               # optional - GUROBI
            sage: p.set_objective([2, 5])                                          # optional - GUROBI
            sage: p.solve()                                                        # optional - GUROBI
            0
            sage: p.get_objective_value()                                          # optional - GUROBI
            7.5
            sage: p.get_variable_value(0)                                          # optional - GUROBI
            0.0
            sage: p.get_variable_value(1)                                          # optional - GUROBI
            1.5
        """

        cdef double value[1]
        check(self.env,GRBgetdblattrelement(self.model[0], "X", variable, value))
        return round(value[0]) if self.is_variable_binary(variable) else value[0]

    cpdef int ncols(self):
        """
        Return the number of columns/variables.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.ncols()                                                       # optional - GUROBI
            0
            sage: p.add_variables(2)                                              # optional - GUROBI
            1
            sage: p.ncols()                                                       # optional - GUROBI
            2
        """
        cdef int i[1]
        check(self.env,GRBgetintattr(self.model[0], "NumVars", i))
        return i[0]

    cpdef int nrows(self):
        """
        Return the number of rows/constraints.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                              # optional - GUROBI
            sage: p.nrows()                                                      # optional - GUROBI
            0
            sage: p.add_linear_constraint([], 2, None)                           # optional - GUROBI
            sage: p.add_linear_constraint([], 2, None)                           # optional - GUROBI
            sage: p.nrows()                                                      # optional - GUROBI
            2
        """
        cdef int i[1]
        check(self.env,GRBgetintattr(self.model[0], "NumConstrs", i))
        return i[0]

    cpdef col_name(self, int index):
        """
        Return the ``index`` th col name

        INPUT:

        - ``index`` (integer) -- the col's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.add_variable(name='I am a variable')                          # optional - GUROBI
            0
            sage: p.col_name(0)                                                   # optional - GUROBI
            'I am a variable'
        """
        cdef char * name[1]
        check(self.env,GRBgetstrattrelement(self.model[0], "VarName", index, <char **> name))
        if name[0] == NULL:
            value = ""
        else:
            value = str(name[0])
        return value

    cpdef row_name(self, int index):
        """
        Return the ``index`` th row name

        INPUT:

        - ``index`` (integer) -- the row's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.add_linear_constraint([], 2, None, name='Empty constraint 1') # optional - GUROBI
            sage: p.row_name(0)                                                   # optional - GUROBI
            'Empty constraint 1'
        """
        cdef char * name[1]
        check(self.env,GRBgetstrattrelement(self.model[0], "ConstrName", index, <char **> name))
        if name[0] == NULL:
            value = ""
        else:
            value = str(name[0])
        return value

    cpdef bint is_variable_binary(self, int index):
        """
        Test whether the given variable is of binary type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.ncols()                                                        # optional - GUROBI
            0
            sage: p.add_variable()                                                 # optional - GUROBI
            0
            sage: p.set_variable_type(0,0)                                         # optional - GUROBI
            sage: p.is_variable_binary(0)                                          # optional - GUROBI
            True
        """
        cdef char vtype[1]
        check(self.env, GRBgetcharattrelement(self.model[0], "VType", index, <char *> vtype))
        return vtype[0] == 'B'

    cpdef bint is_variable_integer(self, int index):
        """
        Test whether the given variable is of integer type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver  # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                               # optional - GUROBI
            sage: p.ncols()                                                       # optional - GUROBI
            0
            sage: p.add_variable()                                                # optional - GUROBI
            0
            sage: p.set_variable_type(0,1)                                        # optional - GUROBI
            sage: p.is_variable_integer(0)                                        # optional - GUROBI
            True
        """
        cdef char vtype[1]
        check(self.env, GRBgetcharattrelement(self.model[0], "VType", index, <char *> vtype))
        return vtype[0] == 'I'

    cpdef bint is_variable_continuous(self, int index):
        """
        Test whether the given variable is of continuous/real type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver   # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                # optional - GUROBI
            sage: p.ncols()                                                        # optional - GUROBI
            0
            sage: p.add_variable()                                                 # optional - GUROBI
            0
            sage: p.is_variable_continuous(0)                                      # optional - GUROBI
            True
            sage: p.set_variable_type(0,1)                                         # optional - GUROBI
            sage: p.is_variable_continuous(0)                                      # optional - GUROBI
            False

        """
        cdef char vtype[1]
        check(self.env, GRBgetcharattrelement(self.model[0], "VType", index, <char *> vtype))
        return vtype[0] == 'C'

    cpdef bint is_maximization(self):
        """
        Test whether the problem is a maximization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.is_maximization()                                               # optional - GUROBI
            True
            sage: p.set_sense(-1)                                                   # optional - GUROBI
            sage: p.is_maximization()                                               # optional - GUROBI
            False
        """
        cdef int sense[1]
        check(self.env,GRBgetintattr(self.model[0], "ModelSense", <int *> sense))
        return sense[0] == -1

    cpdef variable_upper_bound(self, int index, value = False):
        """
        Return or define the upper bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not upper bound. When set to ``False``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variable()                                                  # optional - GUROBI
            0
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (0.0, None)
            sage: p.variable_upper_bound(0, 5)                                      # optional - GUROBI
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (0.0, 5.0)
        """
        cdef double b[1]

        if not value is False:
            check(self.env, GRBsetdblattrelement(
                    self.model[0], "UB",
                    index,
                    value if value is not None else GRB_INFINITY))

            check(self.env,GRBupdatemodel(self.model[0]))
        else:
            error = GRBgetdblattrelement(self.model[0], "UB", index, <double *> b)
            check(self.env, error)
            return None if b[0] >= 2147483647 else b[0]

    cpdef variable_lower_bound(self, int index, value = False):
        """
        Return or define the lower bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not lower bound. When set to ``False``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variable()                                                  # optional - GUROBI
            0
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (0.0, None)
            sage: p.variable_lower_bound(0, 5)                                      # optional - GUROBI
            sage: p.col_bounds(0)                                                   # optional - GUROBI
            (5.0, None)
        """
        cdef double b[1]

        if not value is False:
            check(self.env, GRBsetdblattrelement(
                    self.model[0], "LB",
                    index,
                    value if value is not None else -GRB_INFINITY))

            check(self.env,GRBupdatemodel(self.model[0]))

        else:
            error = GRBgetdblattrelement(self.model[0], "LB", index, <double *> b)
            check(self.env, error)
            return None if b[0] <= -2147483647 else b[0]

    cpdef write_lp(self, char * filename):
        """
        Write the problem to a .lp file

        INPUT:

        - ``filename`` (string)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variables(2)                                                # optional - GUROBI
            1
            sage: p.add_linear_constraint([[0, 1], [1, 2]], None, 3)                # optional - GUROBI
            sage: p.set_objective([2, 5])                                           # optional - GUROBI
            sage: p.write_lp(SAGE_TMP+"/lp_problem.lp")                             # optional - GUROBI
        """
        check(self.env, GRBwrite(self.model[0], filename))

    cpdef write_mps(self, char * filename, int modern):
        """
        Write the problem to a .mps file

        INPUT:

        - ``filename`` (string)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver    # optional - GUROBI
            sage: p = get_solver(solver = "Gurobi")                                 # optional - GUROBI
            sage: p.add_variables(2)                                                # optional - GUROBI
            1
            sage: p.add_linear_constraint([[0, 1], [1, 2]], None, 3)                # optional - GUROBI
            sage: p.set_objective([2, 5])                                           # optional - GUROBI
            sage: p.write_lp(SAGE_TMP+"/lp_problem.lp")                             # optional - GUROBI
        """
        check(self.env, GRBwrite(self.model[0], filename))

    def __dealloc__(self):
        """
        Destructor
        """
        GRBfreemodel(self.model[0])

cdef dict errors = {
    10001 : "GRB_ERROR_OUT_OF_MEMORY",
    10002 : "GRB_ERROR_NULL_ARGUMENT",
    10003 : "GRB_ERROR_INVALID_ARGUMENT",
    10004 : "GRB_ERROR_UNKNOWN_ATTRIBUTE",
    10005 : "GRB_ERROR_DATA_NOT_AVAILABLE",
    10006 : "GRB_ERROR_INDEX_OUT_OF_RANGE",
    10007 : "GRB_ERROR_UNKNOWN_PARAMETER",
    10008 : "GRB_ERROR_VALUE_OUT_OF_RANGE",
    10009 : "GRB_ERROR_NO_LICENSE",
    10010 : "GRB_ERROR_SIZE_LIMIT_EXCEEDED",
    10011 : "GRB_ERROR_CALLBACK",
    10012 : "GRB_ERROR_FILE_READ",
    10013 : "GRB_ERROR_FILE_WRITE",
    10014 : "GRB_ERROR_NUMERIC",
    10015 : "GRB_ERROR_IIS_NOT_INFEASIBLE",
    10016 : "GRB_ERROR_NOT_FOR_MIP",
    10017 : "GRB_ERROR_OPTIMIZATION_IN_PROGRESS",
    10018 : "GRB_ERROR_DUPLICATES",
    10019 : "GRB_ERROR_NODEFILE",
    10020 : "GRB_ERROR_Q_NOT_PSD",
}

cdef dict mip_status = {
    GRB_INFEASIBLE: "The problem is infeasible",
    GRB_INF_OR_UNBD: "The problem is infeasible or unbounded",
    GRB_UNBOUNDED: "The problem is unbounded",
    GRB_ITERATION_LIMIT: "The iteration limit has been reached",
    GRB_NODE_LIMIT: "The node limit has been reached",
    GRB_TIME_LIMIT: "The time limit has been reached",
    GRB_SOLUTION_LIMIT: "The solution limit has been reached",
}

cdef check(GRBenv * env, int error):
    if error:
        raise MIPSolverException("Gurobi: "+str(GRBgeterrormsg(env))+" ("+errors[error]+")")
