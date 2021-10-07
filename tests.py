"""Tests for currency_actualizer"""

import unittest
from bitrix24 import Bitrix24
import currency_actualizer


class TestCurrencyActualizer(unittest.TestCase):
    def test_parse_exchange_rates_empty_list(self):
        self.assertEqual(currency_actualizer.parse_exchange_rates([]), [])

    def test_parse_exchange_rates_right_list(self):
        list_of_currencies = ['USD']
        self.assertIn(list_of_currencies[0],
                      currency_actualizer.parse_exchange_rates(list_of_currencies)[0]['CharCode'])

    def test_parse_exchange_rates_right_list_2_currencies(self):
        list_of_currencies = ['USD', 'EUR']
        result_of_parse = currency_actualizer.parse_exchange_rates(list_of_currencies)
        for i, currency in enumerate(list_of_currencies):
            self.assertIn(currency, result_of_parse[i]['CharCode'])

    def test_parse_exchange_rates_wrong_list(self):
        list_of_currencies = ['USD1']
        self.assertEqual(currency_actualizer.parse_exchange_rates(list_of_currencies), [])

    def test_parse_exchange_rates_not_list_empty(self):
        list_of_currencies = ''
        self.assertEqual(currency_actualizer.parse_exchange_rates(list_of_currencies), [])

    def test_parse_exchange_rates_not_list_but_str(self):
        list_of_currencies = 'USD'
        self.assertEqual(currency_actualizer.parse_exchange_rates(list_of_currencies), [])

    def test_parse_exchange_rates_not_list_but_int(self):
        list_of_currencies = 100
        self.assertEqual(currency_actualizer.parse_exchange_rates(list_of_currencies), [])
