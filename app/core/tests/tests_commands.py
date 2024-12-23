"""
Test custom Django management commands

"""
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
# "core.management.commands.wait_for_db.Command.check" is basically the command we are testing
# we are mocking the check method to simulate the response
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db if db ready"""
        patched_check.return_value = True
        call_command('wait_for_db') # calls our custom command
        patched_check.assert_called_once_with(databases=['default']) # checks if the check method was called once


    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationalError"""
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        """
         we are mocking the behaviour of sleep by using patched_sleep
         the first 2 times that we call the mocked method we want to raise the Psycopg2Error 
         (this error indicates that the db has not even started at all )
         the OperationalError is raised when the db has not yet setup the dev tables that we wanna use
         2 and 3 are random numbers that i feel makes sense
          # we raise an exception to mock that the db is not ready yet
         # the next 3 times we want to raise the OperationalError
        """
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
