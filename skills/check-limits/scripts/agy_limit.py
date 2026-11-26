"""Antigravity 실제 한도를 잰다. `agy -p /usage`가 내는 글 보고(Quota 표)를 읽는다.

보고는 모델 그룹(예: Gemini Models, Claude and GPT models)마다 Weekly·Five Hour 창의 남은 비율과 초기화 시각을 준다.
판정은 한 그룹(기본 `Gemini Models`)만 본다. Antigravity 작업자는 그 그룹의 모델을 쓰기 때문이다.
초기화 시각이 1970년이면 아직 열리지 않은 창으로 보고 뺀다.

사용: python -I <check-limits 스킬 폴더>/scripts/agy_limit.py [--json] [--group "<그룹 이름>"] [--input <저장한 보고 파일>]
종료 코드: 0 = 새 작업 가능, 1 = 한도 경고(사용률 80% 이상), 2 = 소진(100%) 또는 확인 실패
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys

WARN_PERCENT = 80.0
DEFAULT_GROUP = 'Gemini Models'
WINDOWS = {'Five Hour': ('five_hour', 5 * 60), 'Weekly': ('weekly', 7 * 24 * 60)}
LINE = re.compile(r'^\s*(?P<group>\S.*?)\s{2,}(?P<kind>Weekly|Five Hour) Limit Remaining\s+'
                  r'(?P<remaining>\d+(?:\.\d+)?)%\s+(?P<reset>\d{4}-\d{2}-\d{2} \d{2}:\d{2})', re.MULTILINE)
RELOGIN = '`agy`를 한 번 대화형으로 실행해 로그인하세요'


def run_usage():
    """(보고 글, 오류) 중 하나를 돌려준다."""
    agy = shutil.which('agy')
    if agy is None:
        return None, '`agy` 명령이 없음'
    try:
        done = subprocess.run([agy, '-p', '/usage'], capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=120, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f'`agy -p /usage` 실행 실패: {error}'
    if done.returncode != 0:
        tail = (done.stderr or done.stdout).strip()[-300:]
        hint = f' ({RELOGIN})' if 'authentication' in tail.lower() else ''
        return None, f'`agy -p /usage` 종료 코드 {done.returncode}: {tail}{hint}'
    return done.stdout, None


def parse(text, group):
    """그룹의 창 목록. 그 그룹의 줄이 하나도 없으면 None."""
    windows, seen = [], False
    for match in LINE.finditer(text):
        if match['group'].strip().lower() != group.lower():
            continue
        seen = True
        name, minutes = WINDOWS[match['kind']]
        reset = datetime.datetime.strptime(match['reset'], '%Y-%m-%d %H:%M')
        if reset.year <= 1970:
            continue
        windows.append({
            'name': name,
            'used_percent': round(100.0 - float(match['remaining']), 1),
            'window_minutes': minutes,
            'resets_at': match['reset'],
        })
    return windows if seen else None


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--group', default=DEFAULT_GROUP)
    parser.add_argument('--input', help='`agy -p /usage` 출력을 저장한 파일(시험용)')
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding='utf-8') as handle:
            text, error = handle.read(), None
    else:
        text, error = run_usage()
    windows = None if text is None else parse(text, args.group)
    if windows is None:
        error = error or f'보고에서 `{args.group}` 줄을 찾지 못함(형식이 바뀌었을 수 있음)'
        print(json.dumps({'status': 'unknown', 'error': error}, ensure_ascii=False) if args.json
              else f'확인 실패: {error}')
        return 2
    highest = max((item['used_percent'] for item in windows), default=0.0)
    status = 'exhausted' if highest >= 100 else 'warning' if highest >= WARN_PERCENT else 'ok'
    measured = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    report = {'status': status, 'group': args.group, 'windows': windows, 'measured_at': measured,
              'source': 'file' if args.input else 'agy-usage'}
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        for item in windows:
            print(f"{item['name']}: {item['used_percent']:.0f}% 사용 (초기화 {item['resets_at']})")
        print(f"측정 {measured}, 판정: {status} ({args.group})")
    return {'ok': 0, 'warning': 1}.get(status, 2)


if __name__ == '__main__':
    sys.exit(main())
