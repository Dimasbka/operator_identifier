from .models import OperatorProvider

# Create your tests here.

from unittest import TestCase


class OperatorProvider_TestCase(TestCase):
    def setUp(self):
        self.op = OperatorProvider()

    def test_OperatorProvider_valid_number1(self):
        self.assertTrue(self.op.is_valid_number("79173453223"))

    def test_OperatorProvider_valid_number2(self):
        self.assertTrue(self.op.is_valid_number("79067735629"))

    def test_OperatorProvider_in_valid_number1(self):
        self.assertFalse(self.op.is_valid_number("89173453223"))

    def test_OperatorProvider_invalid_number2(self):
        self.assertFalse(self.op.is_valid_number("891453223"))

    def test_OperatorProvider_invalid_number3(self):
        self.assertFalse(self.op.is_valid_number("7917345373453734223"))

    def test_OperatorProvider_404_number(self):
        self.assertFalse(self.op.get_data("70000000000"))
        self.assertTrue(self.op.status == 404)
