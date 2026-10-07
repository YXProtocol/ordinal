# tests/test_ordinal

import unittest
from random import randrange

from ordinal import Ordinal, omega


class TestOrdinal(unittest.TestCase):
    def test_init_valueerror(self):
        cases = (
            {-1, 3}, {7: -3},
            -3, -1,
            (-3, 2), [9, -2]
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertRaises(ValueError, Ordinal, case)
    
    def test_init_typeerror(self):
        cases = (
            {1.9: 3}, {2: 9.8},
            1.0, -2.9,
            (1.0, ), [-1.7],
            {'1': 3}, {2: '9'},
            '1', ('1', )
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertRaises(TypeError, Ordinal, case)
    
    def test_init(self):
        for _ in range(100):
            i = randrange(100000)
            with self.subTest(i=i):
                self.assertEqual(Ordinal(i), i)
        for _ in range(100):
            i, j = randrange(100), randrange(100)
            with self.subTest(i=i, j=j):
                self.assertEqual(Ordinal([i, j]), Ordinal({1: i, 0: j}))
    
    def test_add(self):
        for _ in range(100):
            i = randrange(100000)
            with self.subTest(i=i):
                self.assertEqual(Ordinal({1: 1, 0: i}), omega + i)
            with self.subTest(i=i):
                self.assertEqual(omega, i + omega)
        self.assertEqual(Ordinal({1: 1, 0: 1}) + omega, Ordinal({1: 2}))
    
    def test_mul(self):
        for _ in range(100):
            i = randrange(100000)
            with self.subTest(i=i):
                self.assertEqual(Ordinal({1: i}), omega * i)
            with self.subTest(i=i):
                self.assertEqual(omega, i * omega)
        self.assertEqual(Ordinal({1: 1, 0: 1}) * omega, Ordinal({2: 1}))
    
    def test_pow(self):
        for _ in range(100):
            i = randrange(100000)
            with self.subTest(i=i):
                self.assertEqual(omega ** i, Ordinal({i: 1}))
            with self.subTest(i=i):
                self.assertEqual(i ** omega, omega)
    
    def test_fund(self):
        alpha = omega ** 3
        for _ in range(100):
            i = randrange(100000)
            with self.subTest(i=i):
                self.assertEqual(omega[i], i)
            with self.subTest(i=i):
                self.assertEqual(alpha[i], Ordinal({2: i}))
    
    def test_divmod(self):
        for _ in range(100):
            a, b = randrange(1, 101), randrange(1, 101)
            q, r = divmod(a, b)
            with self.subTest(a=a, b=b):
                self.assertEqual(divmod(Ordinal(a), Ordinal(b)), (q, r))
        self.assertEqual(divmod(omega + 1, 2), (omega, 1))
