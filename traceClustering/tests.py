import unittest
from sample_log.sample import check_sample_list, create_sample_logs, build_sequences


class SampleTest(unittest.TestCase):
    def test_check_sample_list(self):
        seq = build_sequences("test_data/test2.xes")
        correct, _ = check_sample_list("test_data/correctsample.csv", seq)
        self.assertEqual(len(correct['1']) >= 15, True)
        toosmall, _ = check_sample_list("test_data/toosmallsample.csv", seq)
        self.assertEqual(len(toosmall['1']) > 20, False)

    def test_create_sample_logs(self):
        seq = build_sequences("test_data/test2.xes")
        correct, _ = check_sample_list("test_data/correctsample.csv", seq)
        create_sample_logs(correct, "test_data/test2.xes")

if __name__ == '__main__':
    unittest.main()
