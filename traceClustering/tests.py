import unittest
from sample_log.sample import check_sample_list, create_sample_log


class SampleTest(unittest.TestCase):
    def test_check_sample_list(self):
        correct, _ = check_sample_list("test_data/correctsample.csv")
        self.assertEqual(correct, True)
        toosmall, _ = check_sample_list("test_data/toosmallsample.csv")
        self.assertEqual(toosmall, False)
        toomany, _ = check_sample_list("test_data/toomanyclusterssample.csv")
        self.assertEqual(toomany, False)
    def test_create_sample_log(self):
        create_sample_log("test_data/test2.xes", "test_data/correctsample.csv", "test_data/samplefile.xes")

if __name__ == '__main__':
    unittest.main()
