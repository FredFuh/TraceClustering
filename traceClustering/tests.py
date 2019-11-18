import unittest
from backendcore import check_sample_list


class SampleTest(unittest.TestCase):
    def test_check_sample_list(self):
        correct, _ = check_sample_list("test_data/correctsample.txt")
        self.assertEqual(correct, True)
        toosmall, _ = check_sample_list("test_data/toosmallsample.txt")
        self.assertEqual(toosmall, False)
        toomany, _ = check_sample_list("test_data/toomanyclusterssample.txt")
        self.assertEqual(toomany, False)


if __name__ == '__main__':
    unittest.main()
