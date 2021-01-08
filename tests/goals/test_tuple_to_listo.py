from kanren import run

from evalo.evalo import tuple_to_listo
from unification import var

from tests.helpers import EvaloTestCase


class test_tuple_to_listo(EvaloTestCase):
    def test_empty_tuple_is_converted_to_list(self):
        x = var()
        goals = tuple_to_listo((), x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], [])

    def test_single_element_tuple_is_converted_to_list(self):
        x = var()
        goals = tuple_to_listo((1,), x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], [1])

    def test_multiple_element_tuple_is_converted_to_list(self):
        x = var()
        goals = tuple_to_listo((1, 2), x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], [1, 2])

    def test_nested_tuple_is_converted_to_list(self):
        x = var()
        goals = tuple_to_listo((1, (2,)), x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], [1, [2]])

    def test_empty_list_is_converted_to_tuple(self):
        x = var()
        goals = tuple_to_listo(x, [])
        ret = run(1, x, goals)
        self.assertEqual(ret[0], ())

    def test_single_element_list_is_converted_to_tuple(self):
        x = var()
        goals = tuple_to_listo(x, [1])
        ret = run(1, x, goals)
        self.assertEqual(ret[0], (1,))

    def test_multiple_element_list_is_converted_to_tuple(self):
        x = var()
        goals = tuple_to_listo(x, [1, 2])
        ret = run(1, x, goals)
        self.assertEqual(ret[0], (1, 2))

    def test_nested_list_is_converted_to_tuple(self):
        x = var()
        goals = tuple_to_listo(x, [1, [2]])
        ret = run(1, x, goals)
        self.assertEqual(ret[0], (1, (2,)))
