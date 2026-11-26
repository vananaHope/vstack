"""agy_limit.py의 테스트. 실행: python -I -m unittest discover -s skills/check-limits/scripts -p "test_*.py"

`agy -p /usage` 보고는 문서에 형식이 없다. 같은 사용자의 컴퓨터에서 본 두 형식(공백 정렬과 지역 시각,
탭 구분과 ISO UTC 시각)을 그대로 넣어 둘 다 읽히는지 본다.
"""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agy_limit  # noqa: E402

SPACED = """Quota:
Gemini Models          Weekly Limit Remaining     98%   2026-12-03 16:23 KST
Gemini Models          Five Hour Limit Remaining  96%   2026-11-26 21:23 KST
Claude and GPT models  Weekly Limit Remaining     100%  1970-01-01 09:00 KST
Claude and GPT models  Five Hour Limit Remaining  100%  1970-01-01 09:00 KST
"""

TABBED = ("Quota:\n"
          "Gemini Models\tWeekly Limit Remaining\t97%\t2026-12-03T07:23:57Z\n"
          "Gemini Models\tFive Hour Limit Remaining\t92%\t2026-11-26T12:23:57Z\n"
          "Claude and GPT models\tWeekly Limit Remaining\t100%\t1970-01-01T00:00:00Z\n"
          "Claude and GPT models\tFive Hour Limit Remaining\t100%\t1970-01-01T00:00:00Z\n")


def by_name(windows):
    return {item['name']: item for item in windows}


class ParseTest(unittest.TestCase):
    def test_spaced_local_time(self):
        windows = by_name(agy_limit.parse(SPACED, 'Gemini Models'))
        self.assertEqual(windows['weekly']['used_percent'], 2.0)
        self.assertEqual(windows['five_hour']['used_percent'], 4.0)
        self.assertEqual(windows['weekly']['resets_at'], '2026-12-03 16:23')

    def test_tabbed_iso_utc(self):
        windows = by_name(agy_limit.parse(TABBED, 'Gemini Models'))
        self.assertEqual(windows['weekly']['used_percent'], 3.0)
        self.assertEqual(windows['five_hour']['used_percent'], 8.0)
        local = datetime.datetime(2026, 12, 3, 7, 23, 57, tzinfo=datetime.timezone.utc).astimezone()
        self.assertEqual(windows['weekly']['resets_at'], local.strftime('%Y-%m-%d %H:%M'))

    def test_unopened_windows_are_dropped(self):
        for text in (SPACED, TABBED):
            self.assertEqual(agy_limit.parse(text, 'Claude and GPT models'), [])

    def test_group_is_case_insensitive(self):
        self.assertEqual(len(agy_limit.parse(TABBED, 'gemini models')), 2)

    def test_missing_group_is_none(self):
        self.assertIsNone(agy_limit.parse('Quota:\nnothing here\n', 'Gemini Models'))


if __name__ == '__main__':
    unittest.main()
