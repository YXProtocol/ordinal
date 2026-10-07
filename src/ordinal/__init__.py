# ordinal/__init__.py
"""Provide a class to encode ordinals in Python(3.15+).

This module contains a class `Ordinal`
to encode ordinals under epsilon_{0},
including complete ordinal algorithms:
addition, multiplication, power and fundamental sequence.

Attributes
----------
ord_num : TypeAlias
    A kind of number that can be seen as ordinals,
    only including `int`(>=0) and `Ordinal`.
ord_map : TypeAlias
    A kind of mapping which uses
    each omega item's power as key and its coefficient as value.
    Actually, it's a storage of items of
    CNF(Cantor's Normal Format) ordinal.
ord_seq : TypeAlias
    A kind of sequence which only contains `int`(>=0).
ord_init : TypeAlias
    The union type of three types above,
    meaning something that can be used to build up an `Ordinal` object.
omega : Ordinal
    The first transfinite ordinal.

Submodules
----------
growing
    Four common growing-hierarchy functions provided for googologists.
"""

import warnings
from math import ceil
from collections.abc import Sequence, Mapping, Container, Callable
from typing import overload, Never, Final, TypeGuard, TypeVar

from tb_hide import tb_hide, HideMode

from .ordmeta import OrdMeta

__version__ = '1.0.0'
__author__ = 'YXProtocol'

type ord_num = int | Ordinal
type ord_map = Mapping[ord_num, int]
type ord_seq = Sequence[int]
type ord_init = ord_num | ord_map | ord_seq

ZERO_DICT: Final[frozendict[ord_num, int]] = frozendict({0: 0})
_T = TypeVar("_T")
needOrdinal = "the %s should be an ordinal['Ordinal' or 'int'(>=0)] object."


# noinspection PyPep8Naming
def _LaTeX(value: ord_num) -> str:
    if isinstance(value, int):
        return str(value)
    else:
        return value.getLaTeX()


def _sub_out_of_domain() -> Never:
    raise ValueError("can't subtract a larger ordinal from a smaller one")


def _right_out_of_domain(a: Ordinal, b: Ordinal) -> Never:
    raise ValueError(f"doesn't exist alpha making alpha+({b})=({a}) true")


class Ordinal(metaclass=OrdMeta):
    r"""The ordinal numbers.

    Parameters
    ----------
    init_num : ord_init
        The object which will be used to build up an `Ordinal`.
        If the init_num is an `Ordinal`, it will be directly returned.

    Raises
    ------
    TypeError
        If `init_num`'s type is not `ord_init`.
    ValueError
        If `init_num` contains or is negative `int` object(s).

    Attributes
    ----------
    LaTeX : str
        The LaTeX format string of the `Ordinal`. Read-only.

    Methods
    -------
    register(subclass)
        (class method) register a virtual subclass for `Ordinal`
    collect(const_dict, replace)
        (class method) collect ordinal constants
    fundamental_sequence(alpha, n)
        (static method) get `n`-th term of
                        the fundamental sequence of `alpha`
    get_coef(power)
        get the coefficient of relevant omega item
    is_zero()
        check whether the ordinal is zero ordinal
    is_limit()
        check whether the ordinal is a limit ordinal
    is_successor()
        check whether the ordinal is a successor ordinal
    predecessor()
        get the predecessor of a successor ordinal
    right_sub(value)
        get smallest `diff` making `diff+value=self` true

    Notes
    -----
    If you want to implement `Ordinal`'s subclass,
    please make sure the subclass's instances
    are the fixed points of f(alpha) = omega^{alpha}.

    Examples
    --------
    >>> a = Ordinal(6)
    >>> a.LaTeX
    '6'
    >>> b = Ordinal([3, 5, 2])
    >>> b.LaTeX
    '\\omega^{2} \\cdot 3+\\omega \\cdot 5+2'
    >>> print(a+b)
    omega^{2}*3+omega*5+2
    >>> print(b+7)
    omega^{2}*3+omega*5+9
    >>> c = Ordinal({4: 1, 7: 2})
    >>> print(c)
    omega^{7}*2+omega^{4}
    >>> omega[4]
    4
    >>> print((omega**omega)[3])
    omega^{3}
    """
    __slots__ = ('power_coefs', 'powers')
    __consts: dict[str, Ordinal] = dict()

    def __init__(self, content: ord_init, /):
        # the argument has been formalized in `OrdMeta`.
        content = frozendict(content) or ZERO_DICT  # type: ignore
        self.power_coefs: Final[frozendict[ord_num, int]] = content
        powers = list(self.power_coefs)
        powers.sort(reverse=True)
        self.powers: Final[tuple[ord_num, ...]] = tuple(powers)

    @tb_hide(exceptions=(AttributeError,))
    def __setattr__(self, name: str, value: object) -> None:
        if hasattr(self, name):
            raise AttributeError(f"cannot set {name!r} attribute "
                                 f"of immutable type {type(self).__name__!r}")
        super().__setattr__(name, value)

    @tb_hide(exceptions=(AttributeError,))
    def __delattr__(self, name: str) -> Never:
        if hasattr(self, name):
            raise AttributeError(f"cannot set {name!r} attribute "
                                 f"of immutable type {type(self).__name__!r}")
        raise AttributeError(f"{type(self).__name__!r} object "
                             f"has no attribute {name!r} and "
                             "no __dict__ for setting new attributes")

    @tb_hide(exceptions=(OverflowError,))
    def __int__(self) -> int:
        """Try translating an `Ordinal` into an `int`.

        Returns
        -------
        int
            An `int` equals to original `Ordinal`.

        Raises
        ------
        OverflowError
            If the `Ordinal` object is past omega(include),
            it can't translate into an `int`
            because it's transfinite.
        """
        if self.powers[0] == 0:
            return self.power_coefs[0]
        raise OverflowError(
            "the ordinal past omega(include) can't translate into an integer.")

    __index__ = __int__

    @tb_hide(exceptions=(ValueError,))
    def __float__(self) -> float:
        """Try translating an `Ordinal` into a `float`.

        Returns
        -------
        float
            A `float` equals to original `Ordinal`.

        Raises
        ------
        OverflowError
            If the `Ordinal` object is finite
            but larger than the max value of `float`.
        ValueError
            If the `Ordinal` object is past omega(include),
            it can't translate into a `float`
            because it's transfinite.
        """
        if self.powers[0] == 0:
            return float(self.power_coefs[0])
        raise ValueError(
            "the ordinal past omega(include) can't translate into a float.")

    @tb_hide(exceptions=(ValueError,))
    def __complex__(self) -> complex:
        """Try translating an `Ordinal` into a `complex`.

        Returns
        -------
        complex
            A `complex` equals to original `Ordinal`.

        Raises
        ------
        OverflowError
            If the `Ordinal` object is finite
            but larger than the max value of `float`.
        ValueError
            If the `Ordinal` object is past omega(include),
            it can't translate into a `complex`
            because it's transfinite.
        """
        return complex(float(self))

    def __bool__(self) -> bool:
        """Translate an `Ordinal` into a `bool`.

        Returns
        -------
        bool
            `True` if the `Ordinal` object doesn't equal to `0`
            else `False`.
        """
        return not self.is_zero()

    def __str__(self) -> str:
        """Return human-readable representation for end-users.

        Returns
        -------
        str
            A formatted string.

        Examples
        --------
        >>> print(Ordinal({4: 2, 2: 1, 1: 4, 0: 3}))
        omega^{4}*2+omega^{2}+omega*4+3
        """
        # NOTICE:
        # We use '{}' to package the power
        # in case the power is another ordinal number.
        s = list()
        for power in self.powers:
            value = self.power_coefs[power]
            if power == 0:
                s.append(f"{value}")
            elif power == 1:
                if value == 1:
                    s.append("omega")
                else:
                    s.append(f"omega*{value}")
            elif type(power) not in (int, Ordinal):
                # power is an instance of Ordinal's subclass
                # which means power should be
                # a fixed point of omega^{alpha}
                if value == 1:
                    s.append(f"{str(power)}")
                else:
                    s.append(f"{str(power)}*{value}")
            elif value == 1:
                s.append("omega^{0}".format('{' + str(power) + '}'))
            else:
                s.append("omega^{0}*{1}".format('{' + str(power) + '}', value))
        return "+".join(s)

    def __repr__(self) -> str:
        """Return a expression string which can recreate an `Ordinal`.

        Returns
        -------
        str
            A formatted string which can be evaluated by `eval`.

        Examples
        --------
        >>> repr(Ordinal(5))
        'Ordinal({0: 5})'
        >>> repr(Ordinal([3, 4]))
        'Ordinal({0: 4, 1: 3})'
        >>> repr(Ordinal({3: 4}))
        'Ordinal({3: 4})'
        """
        return f"{self.power_coefs!r}".replace("frozendict", "Ordinal")

    def __hash__(self) -> int:
        """Return the hash value of an `Ordinal`.

        Returns
        -------
        int
            The hash value.
        """
        try:
            # a==b => hash(a)==hash(b)
            return hash(int(self))
        except OverflowError:
            return hash((self.power_coefs, Ordinal))
    
    def __eq__(self, value: object) -> bool:
        """Implement equality operator (`==`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool`
                if `value` is an `Ordinal`
                or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means `False`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__eq__`)
        """
        if not self._check_in_compare(value):
            if isinstance(value, int):
                return False
            try:
                int_value = int(value)
                return (int_value == value) and (self == int_value)
            except (TypeError, ValueError, OverflowError):
                return NotImplemented
        value = Ordinal(value)
        sd = self.power_coefs
        vd = value.power_coefs
        for p1, p2 in zip(self.powers, value.powers):
            if p1 != p2: return False
            if sd[p1] != vd[p2]: return False
        return len(self.powers) == len(value.powers)
    
    def __ne__(self, value: object) -> bool:
        """Implement inequality operator (`!=`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool`
                if `value` is an `Ordinal`
                or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means `True`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__ne__`)
        """
        return not (self == value)
    
    def __lt__(self, value: object) -> bool:
        """Implement less-than operator (`<`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool`
                if `value` is an `Ordinal`
                or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__gt__`)
        """
        if not self._check_in_compare(value):
            if isinstance(value, int):
                return False
            try:
                int_value = ceil(value)
                # check whether value is comparable with int.
                _ = (value < int_value)
                return self < int_value
            except (TypeError, ValueError, OverflowError):
                return NotImplemented
        value = Ordinal(value)
        sd = self.power_coefs
        vd = value.power_coefs
        for p1, p2 in zip(self.powers, value.powers):
            if p1 < p2: return True
            if p1 > p2: return False
            if sd[p1] < vd[p2]: return True
            if sd[p1] > vd[p2]: return False
        return len(self.powers) < len(value.powers)

    def __le__(self, value: object) -> bool:
        """Implement less-than-or-equal-to operator (`<=`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool`
                if `value` is an `Ordinal`
                or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__ge__`)
        """
        return (self < value) or (self == value)

    def __gt__(self, value: object) -> bool:
        """Implement greater-than operator (`>`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool`
                if `value` is an `Ordinal`
                or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__lt__`)
        """
        return not ((self < value) or (self == value))

    def __ge__(self, value: object) -> bool:
        """Implement greater-than-or-equal-to operator (`>=`).

        Parameters
        ----------
        value : object
            Another operand to compare with.

        Returns
        -------
        bool or NotImplemented
            `bool` if `value` is an `Ordinal`
            or can translate into an `int`
            `NotImplemented`
                if `value`'s type is not `ord_num`
                and can't translate into an `int`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__le__`)
        """
        return not (self < value)

    @tb_hide(exceptions=(ValueError,))
    def __add__(self, value: ord_num) -> Ordinal:
        """Implement addition operator (`+`).

        Parameters
        ----------
        value : ord_num
            The right addend, which means `b` in `a+b`.
        
        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            'NotImplemented'
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling the subclass's `__radd__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.

        Notes
        -----
        In ordinal theory,
        the sum depends on the order of addends,
        which means alpha+beta maynot equals to beta+alpha.
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
            newd = {0: value}
            vpm = 0
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                return NotImplemented
            newd = dict(value.power_coefs)
            vpm = value.powers[0]
        else:
            return NotImplemented
        sd = self.power_coefs
        for p in self.powers:
            if p == vpm:
                newd[p] += sd[p]  # type: ignore
                break
            elif p < vpm:
                break
            newd[p] = sd[p]  # type: ignore
        return Ordinal(newd)

    @tb_hide(exceptions=(ValueError,))
    def __radd__(self, value: int) -> Ordinal:
        """Implement reflected addition operator (`+`).

        Parameters
        ----------
        value : int
            The left append, which means `a` in `a+b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value` is an `int`.
            `NotImplemented`
                if `value` isn't an `int` (which means a `TypeError`).

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        """
        # The value isn't an Ordinal,
        # or Python will call __add__ not __radd__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        if self.powers[0] > 0:
            return self
        return Ordinal(value + self.power_coefs[0])

    __iadd__ = __add__

    @tb_hide(exceptions=(ValueError,), mode=HideMode.RECURSIVE)
    def __sub__(self, value: ord_num) -> Ordinal:
        """Implement subtraction operator (`-`).

        Parameters
        ----------
        value : ord_num
            The subtrahend, which means `b` in `a-b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rsub__`)

        Raises
        ------
        ValueError
            If `value` is less than `0` or `self` is less than `value`.

        See Also
        --------
        `~Ordinal.right_sub`: The implementation of right subtraction.

        Notes
        -----
        In ordinal theory, there are two subtractions: left and right.
        The `__sub__` implements the left one.
        The left subtraction is a partial operation,
        which means alpha-beta doesn't always make sense.
        It makes sense only when
        alpha is greater than or equals to beta.
        alpha-beta=gamma means beta+gamma=alpha.

        Examples
        --------
        >>> omega-1
        Ordinal({1: 1})
        >>> omega-omega
        Ordinal({0: 0})
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
            value = Ordinal(value)
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                return NotImplemented
        else:
            return NotImplemented
        newd = dict(self.power_coefs)
        ls = len(self.powers)
        lv = len(value.powers)
        for i in range(min(ls, lv)):
            pa = self.powers[i]
            pb = value.powers[i]
            if pa < pb:
                _sub_out_of_domain()
            if pa > pb:
                return Ordinal(newd)
            # pa == pb
            va = self.power_coefs[pa]
            vb = value.power_coefs[pb]
            if va < vb:
                _sub_out_of_domain()
            if va > vb:
                newd[pa] = va - vb
                return Ordinal(newd)
            # va == vb
            del newd[pa]
        if ls < lv:
            _sub_out_of_domain()
        return Ordinal(newd)

    @tb_hide(exceptions=(ValueError,))
    def __rsub__(self, value: int) -> Ordinal:
        """Implement reflected subtraction operator (`-`).

        Parameters
        ----------
        value : int
            The minuend, which means `a` in `a-b`.

        Returns
        -------
        Ordinal or NotImplemented
            'Ordinal'
                if `value` is an `int`.
            'NotImplemented'
                if `value` isn't an `int` (which means a `TypeError`).

        Raises
        ------
        ValueError
            If `value` is less than `0` or `value` is less than `self`.
        """
        # The value isn't an Ordinal,
        # or Python will call __sub__ not __rsub__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        return Ordinal(value) - self

    __isub__ = __sub__

    @tb_hide(exceptions=(ValueError,))
    def __mul__(self, value: ord_num) -> Ordinal:
        """Implement multiplication operator (`*`).

        Parameters
        ----------
        value : ord_num
            The right multiplier, which means `b` in `a*b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rmul__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.

        Notes
        -----
        In ordinal theory,
        the product depends on the order of multipliers,
        which means alpha*beta maynot equals to beta*alpha.
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
            if value == 0:
                return Ordinal['zero']
            elif value == 1:
                return self
            newd = dict(self.power_coefs)
            newd[self.powers[0]] *= value
            return Ordinal(newd)
        if not isinstance(value, Ordinal):
            return NotImplemented
        if type(value) != Ordinal:
            return NotImplemented
        if self.is_zero() or value.is_zero():
            return Ordinal['zero']
        newd = dict()
        smp = self.powers[0]
        for p in value.powers:
            coef = value.power_coefs[p]
            if p == 0:
                for p2 in self.powers:
                    newd[p2] = self.power_coefs[p2]
                newd[smp] *= coef
                break
            newd[smp + p] = coef
        return Ordinal(newd)

    @tb_hide(exceptions=(ValueError,))
    def __rmul__(self, value: int) -> Ordinal:
        """Implement reflected multiplication operator (`*`).

        Parameters
        ----------
        value : int
            The left multiplier, which means `a` in `a*b`.

        Returns
        -------
        Ordinal or NotImplemented
            'Ordinal'
                if `value` is an `int`.
            'NotImplemented'
                if `value` isn't an `int` (which means a `TypeError`).

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        """
        # The value isn't an Ordinal,
        # or Python will call __mul__ not __rmul__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        if value == 0:
            return Ordinal['zero']
        elif value == 1:
            return self
        newd = dict(self.power_coefs)
        try:
            newd[0] *= value
        except KeyError:
            return self
        return Ordinal(newd)

    __imul__ = __mul__

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __floordiv__(self, value: ord_num) -> Ordinal:
        """Implement floor division operator (`//`).

        Parameters
        ----------
        value : ord_num
            The divisor, which means `b` in `a//b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rfloordiv__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `value` equals to `0`

        See Also
        --------
        `~Ordinal.__mod__`: Return the remainder
        `~Ordinal.__divmod__`: The internally delegated method
            More efficient to get both quotient and remainder.

        Examples
        --------
        >>> omega//2
        Ordinal({1: 1})
        >>> omega//omega
        Ordinal({0: 1})
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                return NotImplemented
        else:
            return NotImplemented
        return divmod(self, value)[0]

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __rfloordiv__(self, value: int) -> Ordinal:
        """Implement reflected floor division operator (`//`).

        Parameters
        ----------
        value : int
            The dividend, which means `a` in `a//b`.

        Returns
        -------
        Ordinal or NotImplemented
            'Ordinal'
                if `value` is an `int`.
            'NotImplemented'
                if `value` isn't an `int` (which means a `TypeError`).

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `self` equals to `0`
        """
        # The value isn't an Ordinal,
        # or Python will call __floordiv__ not __rfloordiv__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        return Ordinal(value) // self

    __ifloordiv__ = __floordiv__

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __mod__(self, value: ord_num) -> Ordinal:
        """Implement modulo operator (`%`).

        Parameters
        ----------
        value : ord_num
            The divisor, which means `b` in `a%b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rmod__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `value` equals to `0`

        See Also
        --------
        `~Ordinal.__floordiv__`: Return the quotient
        `~Ordinal.__divmod__`: The internally delegated method
            More efficient to get both quotient and remainder.

        Examples
        --------
        >>> omega%2
        Ordinal({0: 0})
        >>> (omega+1)%omega
        Ordinal({0: 1})
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                return NotImplemented
        else:
            return NotImplemented
        return divmod(self, value)[1]

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __rmod__(self, value: int) -> Ordinal:
        """Implement reflected modulo operator (`%`).

        Parameters
        ----------
        value : int
            The dividend, which means `a` in `a%b`.

        Returns
        -------
        Ordinal or NotImplemented
            'Ordinal'
                if `value` is an `int`.
            'NotImplemented'
                if `value` isn't an `int` (which means a `TypeError`).

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `self` equals to `0`
        """
        # The value isn't an Ordinal,
        # or Python will call __mod__ not __rmod__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        return Ordinal(value) % self

    __imod__ = __mod__

    @tb_hide(exceptions=(ValueError,))
    def __pow__(self, value: ord_num,
                modulo: ord_num | None = None) -> Ordinal:
        """Implement power operator (`**`) and `pow()`.

        Parameters
        ----------
        value : ord_num
            The exponent, which means `b` in `a**b` or `pow(a, b, c)`.
        modulo : ord_num or None
            The divisor, which means `c` in `pow(a, b, c)`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rpow__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`
            or `modulo` is less than or equals to `0`.
        """
        if modulo == 0:
            raise ValueError("pow() 3rd argument cannot be 0")
        if modulo is not None:
            return (self ** value) % modulo
        if not isinstance(value, (int, Ordinal)):
            return NotImplemented
        if self == 1 or value == 0:
            return Ordinal['one']
        if self == 0 or value == 1:
            return Ordinal(self)
        if self.powers[0] == 0:
            return Ordinal(self.power_coefs[0] ** value)
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
            a = value >> 1  # a = value // 2
            temp = self ** a
            temp *= temp
            if value & 1 == 0:  # if value % 2 == 0:
                return temp
            return temp * self
        if type(value) != Ordinal:
            return NotImplemented
        tempd = dict(value.power_coefs)
        tempd[0] = 0
        temp = Ordinal({self.powers[0] * Ordinal(tempd): 1})
        coef = value.get_coef(0)
        if coef == 0:
            return temp
        return temp * (self ** coef)

    @tb_hide(exceptions=(ValueError,))
    def __rpow__(self, value: int) -> Ordinal:
        """Implement reflected power operator (`**`).

        Parameters
        ----------
        value : int
            The base number, which means `a` in `a**b`.

        Returns
        -------
        Ordinal or NotImplemented
            `Ordinal`
                if `value` is an `int`.
            `NotImplemented`
                if `value` isn't an `int` (which means a `TypeError`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        """
        # The value isn't an Ordinal,
        # or Python will call __pow__ not __rpow__.
        if not isinstance(value, int):
            return NotImplemented
        if value < 0:
            raise ValueError(needOrdinal % 'number')
        if self == 0 or value == 1:
            return Ordinal['one']
        if value == 0:
            return Ordinal['zero']
        if self >= Ordinal['omegapo']:
            return Ordinal({self: 1})
        if self.powers[0] == 0:
            return Ordinal(value ** int(self))
        coef = 1
        newd = dict()
        for p in self.powers:
            if p == 0:
                coef = value ** self.power_coefs[0]
                break
            newd[p - 1] = self.power_coefs[p]  # type: ignore
        return Ordinal({Ordinal(newd): coef})

    __ipow__ = __pow__

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __divmod__(self, value: ord_num) -> tuple[Ordinal, Ordinal]:
        """Implement `divmod()`.

        Return quotient and remainder as a tuple.

        Parameters
        ----------
        value : ord_num
            The divisor, which means `b` in `divmod(a, b)`.

        Returns
        -------
        tuple[Ordinal, Ordinal] or NotImplemented
            `tuple[Ordinal, Ordinal]`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rdivmod__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `value` equals to `0`

        See Also
        --------
        `~Ordinal.__floordiv__`: Return the quotient
        `~Ordinal.__mod__`: Return the remainder

        Notes
        -----
        In ordinal theory,
        if alpha = beta * gamma + delta (delta < beta),
        divmod(alpha, beta) = (gamma, delta)

        Examples
        --------
        >>> divmod(omega+1, omega)
        (Ordinal({0: 1}), Ordinal({0: 1}))
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                return NotImplemented
        else:
            return NotImplemented
        try:
            q, r = divmod(int(self), int(value))
            return Ordinal(q), Ordinal(r)
        except OverflowError:
            pass
        value = Ordinal(value)
        if value.is_zero():
            raise ZeroDivisionError("division by zero")
        q = Ordinal['zero']
        r = self
        pv = value.powers[0]
        try:
            while r >= value:
                pr = r.powers[0]
                newp = pr - pv
                newv = r.power_coefs[pr]
                if newp == 0:
                    newv //= value.power_coefs[pv]
                if newv == 0:
                    break
                newq = Ordinal({newp: newv})
                try:
                    r -= value * newq
                except ValueError:
                    newq -= 1
                    r -= value * newq
                q += newq
        except ValueError:
            pass
        return q, r

    @tb_hide(exceptions=(ValueError, ZeroDivisionError))
    def __rdivmod__(self, value: int) -> tuple[Ordinal, Ordinal]:
        """Implement reflected `divmod()`.

        Return quotient and remainder as a tuple.

        Parameters
        ----------
        value : ord_num
            The dividend, which means `a` in `divmod(a, b)`.

        Returns
        -------
        tuple[Ordinal, Ordinal] or NotImplemented
            `tuple[Ordinal, Ordinal]`
                if `value`'s type is `Ordinal` or `int`.
            `NotImplemented`
                if `value`'s type is not `ord_num`
                    (which means a `TypeError`)
                or `value` is an instance of subclass of `Ordinal`
                    (which means calling subclass's `__rdivmod__`)

        Raises
        ------
        ValueError
            If `value` is less than `0`.
        ZeroDivisionError
            If `value` equals to `0`
        """
        # The value isn't an Ordinal,
        # or Python will call __divmod__ not __rdivmod__.
        return divmod(Ordinal(value), self)

    @tb_hide(exceptions=(TypeError, IndexError))
    def __getitem__(self, n: int) -> Ordinal:
        """Return the `n`-th term of the fundamental sequence.

        Parameters
        ----------
        n : int
            The index.

        Returns
        -------
        Ordinal
            The `n`-th term of the fundamental sequence.

        Raises
        ------
        TypeError
            If `n` is not an `int`.
            The finite `Ordinal` can be seen as `int`.
        IndexError
            If `n` is less than `0`.

        See Also
        --------
        `~Ordinal.fundamental_sequence`: The internally delegated method
        """
        return type(self).fundamental_sequence(self, n)

    def __contains__(self, value: object) -> bool:
        if not self._check_in_compare(value):
            return False
        return value < self

    __iter__ = None
    
    @tb_hide(exceptions=(KeyError,))
    def __class_getitem__(cls, name: str) -> Ordinal:
        """Class method to visit important ordinals.

        Parameters
        ----------
        name : str
            The name of the ordinal

        Returns
        -------
        Ordinal
            The corresponding ordinal.

        Raises
        ------
        KeyError
            If no ordinals are named `name`.
        """
        try:
            return cls.__consts[name]
        except KeyError:
            raise KeyError("no such constant stored.") from None

    @overload
    @classmethod
    def register(cls, subclass: type[_T],
                 *, ignore: bool | Container[str] = False
                 ) -> type[_T]:
        ...
    @overload
    @classmethod
    def register(cls, *, ignore: bool | Container[str]
                 ) -> Callable[[type[_T]], type[_T]]:
        ...
    @classmethod
    @tb_hide
    def register(cls,
                 subclass: type[_T] | None = None,
                 *, ignore: bool | Container[str] = False
                 ) -> type[_T] | Callable[[type[_T]], type[_T]]:
        """Class method to register a virtual subclass for `Ordinal`.

        Register `subclass` as a virtual subclass for `Ordinal`,
        which means `issubclass(subclass, Ordinal)` will return `True`.
        There are two ways to use it as a decorator:
            @Ordinal.register
            class xxx:
                ...
        or
            @Ordinal.register(ignore=...)
            class xxx:
                ...
        
        Parameters
        ----------
        subclass : type[_T] | None
            A class who will be registered.
            You shouldn't set it as `None` manually.
 
        ignore : bool | Container[str]
            `Container[str]`:
                The methods you don't want to check or redirect.
            `True`:
                skip all checks and redirections.
            `False` (default):
                accept all checks and redirections.
            

        Returns
        -------
        type[_T]
            `subclass` itself.
        Callable[[type[_t]], type[_T]]
            `Ordinal.register` with fixed `ignore` argument.

        Raises
        ------
        ExceptionGroup[TypeError]
            Failed in registration, which means:
            1. the `subclass` doesn't implement all necessary methods
            2. one or more necessary methods are covered by attributes
            3. both 1. and 2.

        Warns
        -----
        RuntimeWarning
            If one or more methods
            which have default implementation as an ordinal
            are covered by attributes.

        Notes
        -----
        The nessary methods contains:
            `__add__`, `__radd__`,
            `__mul__`, `__rmul__`,
            `__pow__`, `__rpow__`,
            `__eq__`, `__lt__`,
            `__str__`, `__repr__`, `__hash__`,
            `getLaTeX`, `fundamental_sequence`,
            `is_zero`, `is_limit`, `is_successor`
        The methods below will be given a default implementation
        if `subclass` doesn't implement them:
            `__ne__`:
                `return not self == value`
            `__le__`:
                `return self < value or self == value`
            `__gt__`:
                `return not (self < value or self == value)`
            `__ge__`:
                `return not self < value`
            `__bool__` :
                `return not self.is_zero()`
            `__getitem__` :
                `return type(self).fundamental_sequence(self, n)`
        The `LaTeX` attribute will be given a default value
        if `subclass` doesn't implement it:
            `LaTeX` : `property(getLaTeX)`
        """
        def actual_register(subclass: type[_T]) -> type[_T]:
            nonlocal ignore
            if ignore:
                if ignore is True:
                    return super(OrdMeta, Ordinal).register(subclass)
                ignore = set(ignore)
            else:
                ignore = set()
            subname: str = subclass.__name__
            errors: list[TypeError] = list()
            needed_methods: set[str] = {
                '__add__', '__radd__',
                '__mul__', '__rmul__',
                '__pow__', '__rpow__',
                '__eq__', '__lt__',
                '__str__', '__repr__', '__hash__',
                'getLaTeX', 'fundamental_sequence',
                'is_zero', 'is_limit', 'is_successor'
            } - ignore
            needed2_methods: set[str] = {
                '__ne__', '__le__', '__gt__', '__ge__',
                '__bool__', '__getitem__'
            } - ignore
            blocked: set[str] = set()
            for C in subclass.__mro__:
                if C is object:
                    # the jump here is used to avoid a hidden bug
                    # that methods like __eq__
                    # already have implementation
                    # in class `object`
                    continue
                for method in C.__dict__:
                    called = callable(C.__dict__[method])
                    if method in needed_methods:
                        if called:
                            needed_methods.remove(method)
                        else:
                            errors.append(TypeError(
                                "method covered by attribute in "
                                f"class '{subname}'s MRO: {(method, C)}"
                                ))
                    elif method in needed2_methods:
                        needed2_methods.remove(method)
                        if not called:
                            blocked.add(method)
            for method in needed_methods:
                errors.append(TypeError(
                    "missing method expected for ordinal "
                    f"in class '{subname}': {method}"
                    ))
            if errors:
                raise ExceptionGroup(
                    "failed in registering virtual subclass of 'Ordinal'",
                    errors
                    )
            for method in blocked:
                warnings.warn(
                    f"the method '{method}' of "
                    f"'{subname}' are covered by attributes, "
                    "already auto redirected it to default implementation",
                    RuntimeWarning, stacklevel=2
                    )
                setattr(subclass, method, Ordinal.__dict__[method])
            for method in needed2_methods:
                setattr(subclass, method, Ordinal.__dict__[method])
            if not hasattr(subclass, 'LaTeX'):
                setattr(subclass, 'LaTeX', property(subclass.getLaTeX))
            return super(OrdMeta, Ordinal).register(subclass)
        if subclass is None:
            return actual_register
        return actual_register(subclass)
    
    @classmethod
    @tb_hide
    def collect(cls, const_dict: dict[str, Ordinal],
                replace: bool = False) -> None:
        """Collect important ordinals.

        This method allows you to collect important ordinals uniformly,
        when you want to visit them, simply using `Ordinal[name]`.
        
        Parameters
        ----------
        const_dict : dict[str, Ordinal]
            A `dict` containsthe ordinals (as value)
            and their names (as key).
        replace : bool, optional
            Whether you need to replace old values
            if new values have the same names.
            Default value: `False`
        
        Raises
        ------
        ExceptionGroup[TypeError]
            If one or more values of `const_dict`'
            are not `Ordinal` objects.
        """
        errors: list[TypeError] = list()
        consts = cls.__consts
        for name, value in const_dict.items():
            if not isinstance(value, cls):
                errors.append(TypeError(f"{value} is not an ordinal"))
            if name not in consts or replace:
                consts[name] = value
        if errors:
            raise ExceptionGroup("something is not ordinal", errors)

    @staticmethod
    def _pre_check(content: ord_init, /) -> Ordinal | None:
        if isinstance(content, Ordinal):
            return content
        return None

    @staticmethod
    def _post_check(content: dict[ord_num, int], /) -> Ordinal | None:
        if len(content) == 1:
            power, value = next(iter(content.items()))
            if value == 1 and type(power) not in (int, Ordinal):
                # `power` is an instance of Ordinal's subclass
                # which means `power` should be
                # a fixed point of omega^{alpha}
                # so we shouldn't package it again
                # because it won't make more sense
                return power  # type: ignore
        return None

    @staticmethod
    @tb_hide(exceptions=(TypeError, ValueError))
    def formalize(content: int | ord_map | ord_seq, /) -> dict[ord_num, int]:
        """Static method to translate object into formal format.

        Parameters
        ----------
        content : int | ord_map | ord_seq
            The object used to build `Ordinal`.

        Returns
        -------
        dict[ord_num, int]
            A formalized dict, storing CNF ordinal information.

        Raises
        ------
        TypeError
            If `content`'s type isn't `int`, `ord_num` or `ord_seq`.
        ValueError
            If `content` is an `int` but less than `0`.

        Notes
        -----
        This method will be called in building automatically,
        so you needn't call this method manually.
        """
        if isinstance(content, int):
            if content < 0:
                raise ValueError(needOrdinal % 'number')
            content = {0: content}
        elif isinstance(content, Sequence):
            content = {idx: value
                       for idx, value in enumerate(reversed(content))}
        elif isinstance(content, Mapping):
            oricontent = content
            content = dict(content)
            for p in oricontent:
                if type(p) == Ordinal and p.powers[0] == 0:
                    power = p.power_coefs[0]
                    coef = content[p]
                    del content[p]
                    content[power] = coef
        else:
            # noinspection PyStringConversionWithoutDunderMethod
            raise TypeError(f"unsupported type: {type(content).__name__}")
        powers: dict[ord_num, int] = dict()
        for p in content:
            if not isinstance(p, Ordinal):
                if not isinstance(p, int):
                    raise TypeError(p, needOrdinal % 'power')
                if p < 0:
                    raise ValueError(p, needOrdinal % 'power')
            v = content[p]
            if not isinstance(v, int):
                raise TypeError(v, "the coefficient should be an 'int' object.")
            if v < 0:
                raise ValueError(v, "the coefficient should be a natural number.")
            if v == 0:
                continue
            powers[p] = int(v)
        return powers

    @staticmethod
    @tb_hide(exceptions=(TypeError, ValueError, IndexError))
    def fundamental_sequence(alpha: ord_num, n: int, /) -> Ordinal:
        """Static method to get a term of the fundamental sequence.

        Parameters
        ----------
        alpha : ord_num
            The ordinal
            whose `n`-th term of fundamental sequence you want to get.
        n : int
            The index.

        Returns
        -------
        Ordinal
            The `n`-th term of the fundamental sequence of `alpha`.

        Raises
        ------
        TypeError
            If `alpha`'s type is not `ord_num`.
            If `n` is not an `int`.
            The finite `Ordinal` can be seen as `int`.
        ValueError
            If `alpha` is less than `0`.
        IndexError
            If `n` is less than `0`.

        Notes
        -----
        The fundamental sequence of a limit ordinal
        is a sequence containing smaller ordinals,
        whose supremum is the limit ordinal.
        Successor ordinals don't have a fundamental sequence,
        if you try to get it in our code,
        you will simply get its predecessor.
        """
        if not isinstance(alpha, Ordinal):
            if not isinstance(alpha, int):
                raise TypeError(alpha, needOrdinal % 'number')
            if alpha < 0:
                raise ValueError(alpha, needOrdinal % 'number')
        alpha = Ordinal(alpha)
        if type(alpha) != Ordinal:
            return type(alpha).fundamental_sequence(alpha, n)
        if not isinstance(n, int):
            if not isinstance(n, Ordinal) or n >= Ordinal['omega']:
                raise TypeError("the index should be a natural number.")
            n = int(n)
        if n < 0:
            raise IndexError("the index should be a natural number.")
        if alpha.is_zero():
            return alpha
        if alpha.is_successor():
            return alpha.predecessor()
        if len(alpha.powers) == 1:
            mp = alpha.powers[0]
            coef = alpha.power_coefs[mp]
            if coef >= 2:
                return Ordinal({mp: coef - 1}) + (Ordinal({mp: 1})[n])
            if isinstance(mp, int):
                mp -= 1
            else:
                if mp.is_limit():
                    return Ordinal({mp[n]: 1})
                newd = dict(mp.power_coefs)
                newd[0] -= 1
                mp = Ordinal(newd)
            return Ordinal({mp: n})
        newd = dict(alpha.power_coefs)
        mp = alpha.powers[-1]
        coef = newd[mp]
        del newd[mp]
        gamma = Ordinal(newd)
        beta = Ordinal({mp: coef})
        return gamma + beta[n]

    def _check_in_compare(self, value: object) -> TypeGuard[ord_num]:
        return ((type(value) == type(self))
                or (isinstance(value, int) and value >= 0))

    @tb_hide(exceptions=(TypeError, ValueError))
    def get_coef(self, power: ord_num) -> int:
        """Return the coefficient of the corresponding `power`.

        Parameters
        ----------
        power : ord_num
            The power of omega item.

        Returns
        -------
        int
            The coefficient of corresponding omega item.

        Raises
        ------
        TypeError
            If `power` is not an `ord_num`.
        ValueError
            If `power` is less than `0`.
        """
        try:
            return self.power_coefs[power]
        except KeyError:
            if not isinstance(power, Ordinal):
                if not isinstance(power, int):
                    raise TypeError(power, needOrdinal % 'power') from None
                if power < 0:
                    raise ValueError(power, needOrdinal % 'power') from None
            return 0

    def is_zero(self) -> bool:
        """Check whether an `Ordinal` is zero ordinal.

        Returns
        -------
        bool
            `True` if this `Ordinal` is zero ordinal.
            `False` if not.
        """
        return self == Ordinal['zero']

    def is_limit(self) -> bool:
        """Check whether an `Ordinal` is a limit ordinal.

        Returns
        -------
        bool
            `True` if this `Ordinal` is a limit ordinal.
            `False` if not.

        Notes
        -----
        Zero ordinal is deemed as a limit ordinal sometimes,
        but in this method,
        zero ordinal isn't deemed as a limit ordinal.
        """
        return self.get_coef(0) == 0 and self != Ordinal['zero']

    def is_successor(self) -> bool:
        """Check whether an `Ordinal` is a successor ordinal.

        Returns
        -------
        bool
            `True` if this `Ordinal` is a successor ordinal.
            `False` if not.
        """
        return self.get_coef(0) != 0

    @tb_hide(exceptions=(ValueError,))
    def predecessor(self) -> Ordinal:
        """Return the predecessor of an `Ordinal`.

        Returns
        -------
        Ordinal
            The predecessor.

        Raises
        ------
        ValueError
            If this `Ordinal` isn't a successor ordinal.
        """
        if not self.is_successor():
            raise ValueError("only successor ordinals have predecessor")
        newd = dict(self.power_coefs)
        newd[0] -= 1
        return Ordinal(newd)

    @tb_hide(exceptions=(TypeError, ValueError), mode=HideMode.RECURSIVE)
    def right_sub(self, value: ord_num, /) -> Ordinal:
        """Implement the right subtraction.

        Parameters
        ----------
        value : ord_num
            The subtrahend.

        Returns
        -------
        Ordinal
            The difference.
        
        Raises
        ------
        TypeError
            If `value`'type isn't `ord_num`.
        ValueError
            If doesn't exist `diff` making `diff+value=self` true.

        See Also
        --------
        `~Ordinal.__sub__`: The implementation of left subtraction.

        Notes
        -----
        In ordinal theory, there are two subtractions: left and right.
        The `right_sub` implements the right one.
        The right subtraction is a partial operation,
        which means alpha-beta doesn't always make sense.
        It makes sense only when exists gamma making gamma+beta=alpha.
        alpha-beta=gamma means gamma+beta=alpha
        and doesn't exist smaller gamma making it true.

        Examples
        --------
        >>> (omega+4).right_sub(2)
        Ordinal({0: 2, 1: 1})
        """
        if isinstance(value, int):
            if value < 0:
                raise ValueError(needOrdinal % 'number')
            value = Ordinal(value)
        elif isinstance(value, Ordinal):
            if type(value) != Ordinal:
                _right_out_of_domain(self, value)
        else:
            raise TypeError(needOrdinal % 'number')
        if value.is_zero():
            return self
        newd = dict(self.power_coefs)
        sp = self.powers
        vp = value.powers
        length = len(vp)
        try:
            for i in range(1, length):
                p = vp[-i]
                coef = value.get_coef(p)
                if sp[-i] != p or newd[p] != coef:
                    _right_out_of_domain(self, value)
                del newd[p]
            p = vp[0]
            coef = value.get_coef(p)
            if sp[-length] != p or newd[p] < coef:
                _right_out_of_domain(self, value)
            newd[p] -= coef
            return Ordinal(newd)
        except IndexError:
            pass
        _right_out_of_domain(self, value)

    # noinspection PyPep8Naming
    def getLaTeX(self) -> str:
        """Return the LaTeX format string of an `Ordinal`.

        Returns
        -------
        str
            The LaTeX format string of this `Ordinal`.
        """
        s = list()
        for power in self.powers:
            value = self.power_coefs[power]
            if power == 0:
                s.append(f"{value}")
            elif power == 1:
                if value == 1:
                    s.append(r"\omega")
                else:
                    s.append(rf"\omega \cdot {value}")
            elif type(power) not in (int, Ordinal):
                # power is an instance of Ordinal's subclass
                # which means power should be
                # a fixed point of omega^{alpha}
                if value == 1:
                    s.append(f"{_LaTeX(power)}")
                else:
                    s.append(rf"{_LaTeX(power)} \cdot {value}")
            elif value == 1:
                s.append(r"\omega^{0}".format('{' + _LaTeX(power) + '}'))
            else:
                s.append(r"\omega^{0} \cdot {1}".format(
                    '{' + _LaTeX(power) + '}', value))
        return "+".join(s)

    LaTeX = property(getLaTeX,
                     doc="The LaTeX format string of an `Ordinal`. Read-only.")


consts = dict()
consts['zero'] = Ordinal(0)
consts['one'] = Ordinal(1)
omega: Final[Ordinal] = Ordinal({1: 1})
consts['omega'] = omega
consts['omegapo'] = Ordinal({omega: 1})
Ordinal.collect(consts)
del consts

__all__ = ['Ordinal', 'omega', 'ord_num', 'ord_map', 'ord_seq', 'ord_init']
