from unittest.mock import Mock
from unittest import TestCase

from evalo.utils import count_goals


class TestCountGoals(TestCase):
    def test_count_goals_returns_zero_for_empty_list(self):
        ret = count_goals(())

        self.assertEqual(ret, 0)

    def test_count_goals_returns_number_of_elements_for_no_listed_goals(self):
        ret = count_goals((Mock(1), Mock(2), Mock(3)))

        self.assertEqual(ret, 3)

    def test_count_goals_calls_recursively_for_listed_goals(self):
        ret = count_goals(((Mock(11), Mock(12)), Mock(2), Mock(3)))

        self.assertEqual(ret, 4)
