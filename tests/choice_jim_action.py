import unittest

from common.variables import NOT_BYTES, NO_ACTION, NO_TIME, BROKEN_JIM, UNKNOWN_ACTION
from server import choice_jim_action


class TestSplitFunction(unittest.TestCase):
    def setUp(self):
        self.jim_obj = {'action': 'presence', 'time': 1593004547.839623,
                        'type': 'status',
                        'user': {
                            'account_name': 'C0deMaver1ck',
                            'status': 'Yep, I am here!'}
                        }

    def test_choice_jim_action_not_bytes(self):
        res = choice_jim_action(NOT_BYTES)
        self.assertEqual(res, {'response': 500})

    def test_choice_jim_action_no_action(self):
        res = choice_jim_action(NO_ACTION)
        self.assertEqual(res, {'response': 400, 'error': NO_ACTION})

    def test_choice_jim_action_no_time(self):
        res = choice_jim_action(NO_TIME)
        self.assertEqual(res, {'response': 400, 'error': NO_TIME})

    def test_choice_jim_action_no_time_broken_jim(self):
        res = choice_jim_action(BROKEN_JIM)
        self.assertEqual(res, {'response': 400, 'error': BROKEN_JIM})

    def test_choice_jim_action_no_time_unknown_action(self):
        self.jim_obj['action'] = 'unknown'
        res = choice_jim_action(self.jim_obj)
        self.assertEqual(res, {'response': 400, 'error': UNKNOWN_ACTION})

    def test_choice_jim_action_no_time_ok(self):
        self.jim_obj['action'] = 'presence'
        res = choice_jim_action(self.jim_obj)
        self.assertEqual(res, {'response': 200})


if __name__ == '__main__':
    unittest.main()
