"""
Sample tests

"""

from django.test import SimpleTestCase
from app import calc

class TestCalc(SimpleTestCase):
    """Test the calc module"""

    def test_add(self):
        """Test the add function"""
        response = calc.add(3, 8)
        self.assertEqual(response, 11)
    
    def test_subtract(self):
        """Test the subtract function"""
        response = calc.subtract(5, 2)
        self.assertEqual(response, 3)
