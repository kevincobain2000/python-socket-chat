import unittest

from chat.server import Server
from chat.user import User

class TestServerMethods(unittest.TestCase):

  def test_upper(self):
    self.assertEqual('todo'.upper(), 'TODO')

if __name__ == '__main__':
    unittest.main()