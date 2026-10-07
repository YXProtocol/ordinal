# ordinal/growing.py
"""Provide four common growing-hierarchy functions.

This module contains FGH, MGH, HH and SGH for googologists.
In the code, all of them are writen in lower case.
"""

from . import Ordinal, ord_num


def _check(alpha: object, n: object):
    if not isinstance(alpha, (Ordinal, int)) or alpha < 0:
        raise TypeError("'alpha' must be an 'Ordinal' object")
    if not isinstance(n, int):
        raise TypeError("'n' must be an 'int' object")
    if n < 0:
        raise ValueError("'n' must be a natural number")


def fgh(alpha: ord_num, n: int) -> int:
    r"""The Fast Growing Hierarchy (FGH) function.

    Parameters
    ----------
    alpha : ord_num
        The hierarchy.
    n : int
        The argument.

    Returns
    -------
    int
        The result.

    Raises
    ------
    TypeError
        If `alpha`'s type isn't `ord_num` or `n` isnot an `int` object.
    ValueError
        If `n` is an `int` object but less than `0`.

    Notes
    -----
    The definition of FGH:
        f_{0}(n) = n+1
        f_{\alpha+1}(n) = f_{\alpha}^{n}(n)
        f_{\alpha}(n) = f_{\alpha[n]}(n) if \alpha is limit
    """
    _check(alpha, n)
    alpha = Ordinal(alpha)
    stack = [[alpha, 1]]
    while stack:
        p = stack[-1]
        alpha = p[0]
        p[1] -= 1
        if p[1] <= 0:
            stack.pop()
        while alpha.is_limit():
            alpha = alpha[n]
        if alpha.is_zero():
            n += 1
        else:
            alpha = alpha.predecessor()
            stack.append([alpha, n])
    return n


def mgh(alpha: ord_num, n: int) -> int:
    r"""The Medium Growing Hierarchy (MGH) function.

    Parameters
    ----------
    alpha : ord_num
        The hierarchy.
    n : int
        The argument.

    Returns
    -------
    int
        The result.

    Raises
    ------
    TypeError
        If `alpha`'s type isn't `ord_num` or `n` isnot an `int` object.
    ValueError
        If `n` is an `int` object but less than `0`.

    Notes
    -----
    The definition of MGH:
        m_{0}(n) = n+1
        m_{\alpha+1}(n) = m_{\alpha}(m_{\alpha}(n))
        m_{\alpha}(n) = m_{\alpha[n]}(n) if \alpha is limit
    """
    _check(alpha, n)
    alpha = Ordinal(alpha)
    stack = [alpha]
    while stack:
        alpha = stack.pop()
        while alpha.is_limit():
            alpha = alpha[n]
        if alpha.is_zero():
            n += 1
            continue
        alpha = alpha.predecessor()
        stack.extend([alpha, alpha])
    return n


def hh(alpha: ord_num, n: int) -> int:
    r"""The Hardy Hierarchy (HH) function.

    Parameters
    ----------
    alpha : ord_num
        The hierarchy.
    n : int
        The argument.

    Returns
    -------
    int
        The result.

    Raises
    ------
    TypeError
        If `alpha`'s type isn't `ord_num` or `n` isnot an `int` object.
    ValueError
        If `n` is an `int` object but less than `0`.

    Notes
    -----
    The definition of HH:
        H_{0}(n) = n
        H_{\alpha+1}(n) = H_{\alpha}(n+1)
        H_{\alpha}(n) = H_{\alpha[n]}(n) if \alpha is limit
    """
    _check(alpha, n)
    alpha = Ordinal(alpha)
    while True:
        if alpha.is_zero():
            return n
        if alpha.is_limit():
            alpha = alpha[n]
        else:
            alpha = alpha.predecessor()
            n += 1


def sgh(alpha: ord_num, n: int) -> int:
    r"""The Slow Growing Hierarchy (SGH) function.

    Parameters
    ----------
    alpha : ord_num
        The hierarchy.
    n : int
        The argument.

    Returns
    -------
    int
        The result.

    Raises
    ------
    TypeError
        If `alpha`'s type isn't `ord_num` or `n` isnot an `int` object.
    ValueError
        If `n` is an `int` object but less than `0`.

    Notes
    -----
    The definition of SGH:
        g_{0}(n) = 0
        g_{\alpha+1}(n) = g_{\alpha}(n)+1
        g_{\alpha}(n) = g_{\alpha[n]}(n) if \alpha is limit
    """
    _check(alpha, n)
    alpha = Ordinal(alpha)
    k = 0
    while True:
        while alpha.is_successor():
            alpha = alpha.predecessor()
            k += 1
        if alpha.is_zero():
            return k
        alpha = alpha[n]


__all__ = ['fgh', 'mgh', 'hh', 'sgh']
