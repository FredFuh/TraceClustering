import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class SampleTest(unittest.TestCase):
    def test_check_sample_list(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
