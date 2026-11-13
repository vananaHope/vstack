"""image_diff.py의 테스트. 실행: python -m unittest test_image_diff.py (이 폴더에서)

PNG는 테스트가 직접 만든다. 필터와 색 형식마다 풀어 낸 픽셀이 넣은 픽셀과 같은지,
명령줄의 출력과 종료 코드가 문서대로인지 본다.
"""

import io
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import image_diff  # noqa: E402

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image_diff.py")
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def encode_rows(rows, bpp, filter_kind):
    """줄마다 지정한 PNG 필터를 걸어 압축 전 데이터를 만든다."""
    out = bytearray()
    prev = bytes(len(rows[0]))
    for row in rows:
        line = bytearray(len(row))
        for i, value in enumerate(row):
            a = row[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            pred = {0: 0, 1: a, 2: b, 3: (a + b) >> 1, 4: paeth(a, b, c)}[filter_kind]
            line[i] = (value - pred) & 0xFF
        out.append(filter_kind)
        out.extend(line)
        prev = bytes(row)
    return bytes(out)


def png(width, height, color, depth, rows, bpp, filter_kind=0, palette=None, transparency=None, interlace=0,
        declared_height=None, end=True):
    body = SIGNATURE
    body += chunk(b"IHDR", struct.pack(">IIBBBBB", width, declared_height or height, depth, color, 0, 0, interlace))
    if palette is not None:
        body += chunk(b"PLTE", palette)
    if transparency is not None:
        body += chunk(b"tRNS", transparency)
    data = zlib.compress(encode_rows(rows, bpp, filter_kind))
    half = len(data) // 2
    body += chunk(b"IDAT", data[:half]) + chunk(b"IDAT", data[half:])  # IDAT가 여러 개인 경우
    return body + (chunk(b"IEND", b"") if end else b"")


def rgba_png(pixels, filter_kind=0):
    """pixels: 줄마다 (r, g, b, a) 목록."""
    rows = [bytes(v for px in row for v in px) for row in pixels]
    return png(len(pixels[0]), len(pixels), 6, 8, rows, 4, filter_kind)


def gradient(width, height):
    return [[((x * 7 + y * 3) % 256, (x * 13) % 256, (y * 29 + x) % 256, 255) for x in range(width)]
            for y in range(height)]


class Files(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, name, data):
        path = os.path.join(self.dir.name, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def read(self, path):
        with open(path, "rb") as handle:
            return handle.read()

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = image_diff.main(list(args))
        return code, out.getvalue().strip(), err.getvalue().strip()


class DecodeTest(Files):
    def test_every_filter_decodes_to_the_pixels_that_were_written(self):
        pixels = gradient(9, 7)
        expected = [bytes(v for px in row for v in px) for row in pixels]
        for kind in range(5):
            with self.subTest(filter=kind):
                width, height, rows = image_diff.decode(self.write("f%d.png" % kind, rgba_png(pixels, kind)))
                self.assertEqual((width, height), (9, 7))
                self.assertEqual(rows, expected)

    def test_rgb_without_alpha_reads_as_opaque(self):
        rows = [bytes((10, 20, 30, 40, 50, 60))]
        _, _, decoded = image_diff.decode(self.write("rgb.png", png(2, 1, 2, 8, rows, 3, 4)))
        self.assertEqual(decoded, [bytes((10, 20, 30, 255, 40, 50, 60, 255))])

    def test_palette_with_transparency(self):
        palette = bytes((255, 0, 0, 0, 255, 0, 0, 0, 255))
        rows = [bytes((0, 1, 2))]
        data = png(3, 1, 3, 8, rows, 1, 0, palette=palette, transparency=bytes((255, 128)))
        _, _, decoded = image_diff.decode(self.write("pal.png", data))
        self.assertEqual(decoded, [bytes((255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 255))])

    def test_two_bit_palette_packs_four_pixels_in_a_byte(self):
        palette = bytes((1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4))
        rows = [bytes((0b00011011,))]  # 번호 0, 1, 2, 3
        _, _, decoded = image_diff.decode(self.write("p2.png", png(4, 1, 3, 2, rows, 1, palette=palette)))
        self.assertEqual(decoded, [bytes((1, 1, 1, 255, 2, 2, 2, 255, 3, 3, 3, 255, 4, 4, 4, 255))])

    def test_one_bit_gray_scales_to_black_and_white(self):
        rows = [bytes((0b10100000,))]  # 픽셀 3개: 1, 0, 1
        _, _, decoded = image_diff.decode(self.write("g1.png", png(3, 1, 0, 1, rows, 1)))
        self.assertEqual(decoded, [bytes((255, 255, 255, 255, 0, 0, 0, 255, 255, 255, 255, 255))])

    def test_gray_with_alpha(self):
        _, _, decoded = image_diff.decode(self.write("ga.png", png(1, 1, 4, 8, [bytes((90, 7))], 2)))
        self.assertEqual(decoded, [bytes((90, 90, 90, 7))])

    def test_transparent_key_makes_matching_gray_and_rgb_pixels_transparent(self):
        gray = png(2, 1, 0, 8, [bytes((64, 65))], 1, transparency=struct.pack(">H", 64))
        _, _, decoded = image_diff.decode(self.write("gt.png", gray))
        self.assertEqual(decoded, [bytes((64, 64, 64, 0, 65, 65, 65, 255))])
        rgb = png(2, 1, 2, 8, [bytes((16, 32, 48, 16, 32, 49))], 3, transparency=struct.pack(">HHH", 16, 32, 48))
        _, _, decoded = image_diff.decode(self.write("rt.png", rgb))
        self.assertEqual(decoded, [bytes((16, 32, 48, 0, 16, 32, 49, 255))])


class CompareTest(Files):
    def test_same_pixels_with_different_encoding_are_identical(self):
        pixels = gradient(12, 5)
        first = self.write("a.png", rgba_png(pixels, 0))
        second = self.write("b.png", rgba_png(pixels, 4))
        self.assertNotEqual(self.read(first), self.read(second))
        self.assertEqual(self.run_main(first, second), (0, "identical: 12x5", ""))

    def test_one_changed_pixel_is_reported_with_its_place_and_size(self):
        pixels = gradient(10, 6)
        changed = [list(row) for row in pixels]
        r, g, b, a = changed[4][7]
        changed[4][7] = (r + 9 if r + 9 < 256 else r - 9, g, b, a)
        code, out, _ = self.run_main(self.write("a.png", rgba_png(pixels)), self.write("b.png", rgba_png(changed, 3)))
        self.assertEqual(code, 1)
        self.assertEqual(out, "different: 1 of 60 pixels (1.667%), bbox 7,4-7,4, max channel delta 9")

    def test_a_delta_of_one_is_different(self):
        first = self.write("a.png", rgba_png([[(100, 100, 100, 255)]]))
        second = self.write("b.png", rgba_png([[(100, 101, 100, 255)]]))
        self.assertEqual(self.run_main(first, second),
                         (1, "different: 1 of 1 pixels (100.000%), bbox 0,0-0,0, max channel delta 1", ""))

    def test_bbox_covers_every_changed_pixel(self):
        pixels = [[(0, 0, 0, 255)] * 8 for _ in range(8)]
        changed = [list(row) for row in pixels]
        changed[1][6] = (0, 0, 40, 255)
        changed[5][2] = (200, 0, 0, 255)
        code, out, _ = self.run_main(self.write("a.png", rgba_png(pixels)), self.write("b.png", rgba_png(changed)))
        self.assertEqual((code, out), (1, "different: 2 of 64 pixels (3.125%), bbox 2,1-6,5, max channel delta 200"))

    def test_alpha_only_change_counts(self):
        first = self.write("a.png", rgba_png([[(5, 5, 5, 255)]]))
        second = self.write("b.png", rgba_png([[(5, 5, 5, 254)]]))
        self.assertEqual(self.run_main(first, second)[0], 1)

    def test_a_transparent_key_alone_makes_the_images_different(self):
        opaque = self.write("a.png", png(1, 1, 0, 8, [bytes((64,))], 1))
        keyed = self.write("b.png", png(1, 1, 0, 8, [bytes((64,))], 1, transparency=struct.pack(">H", 64)))
        self.assertEqual(self.run_main(opaque, keyed)[0], 1)
        opaque = self.write("c.png", png(1, 1, 2, 8, [bytes((16, 32, 48))], 3))
        keyed = self.write("d.png", png(1, 1, 2, 8, [bytes((16, 32, 48))], 3,
                                        transparency=struct.pack(">HHH", 16, 32, 48)))
        self.assertEqual(self.run_main(opaque, keyed)[0], 1)

    def test_different_size_is_different(self):
        first = self.write("a.png", rgba_png(gradient(4, 4)))
        second = self.write("b.png", rgba_png(gradient(4, 5)))
        self.assertEqual(self.run_main(first, second), (1, "different: size 4x4 vs 4x5", ""))

    def test_there_is_no_tolerance_option(self):
        good = self.write("a.png", rgba_png(gradient(2, 2)))
        with self.assertRaises(SystemExit) as raised, redirect_stderr(io.StringIO()):
            image_diff.main([good, good, "--tolerance", "2"])
        self.assertEqual(raised.exception.code, 2)


class CannotCompareTest(Files):
    def cases(self):
        whole = rgba_png(gradient(6, 6))
        flipped = bytearray(whole)
        flipped[-1] ^= 0x01  # 마지막 청크의 CRC 한 비트. 픽셀 데이터는 멀쩡하므로 CRC 검사만 잡을 수 있다
        two_rows = [bytes((1, 2, 3, 4)), bytes((5, 6, 7, 8))]
        return {
            "none.png": None,
            "not-png.jpg": b"\xff\xd8\xff\xe0 not a png",
            "interlaced.png": png(1, 1, 6, 8, [bytes((1, 2, 3, 4))], 4, interlace=1),
            "cut-in-chunk.png": whole[:60],
            "cut-last-chunk.png": whole[:-3],
            "no-iend.png": png(1, 1, 6, 8, [bytes((1, 2, 3, 4))], 4, end=False),
            "bad-crc.png": bytes(flipped),
            "short-rows.png": png(1, 1, 6, 8, two_rows[:1], 4, declared_height=2),
            "extra-rows.png": png(1, 2, 6, 8, two_rows, 4, declared_height=1),
            "sixteen-bit.png": png(1, 1, 0, 16, [bytes((0x12, 0x00))], 2),
        }

    def test_every_unreadable_input_exits_two_with_an_ascii_reason_naming_the_file(self):
        good = self.write("a.png", rgba_png(gradient(2, 2)))
        for name, data in self.cases().items():
            other = os.path.join(self.dir.name, name) if data is None else self.write(name, data)
            with self.subTest(other=name):
                code, out, err = self.run_main(good, other)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("cannot compare: "), err)
                self.assertIn("candidate", err)
                self.assertTrue(err.isascii(), err)
                code, _, err = self.run_main(other, good)
                self.assertEqual(code, 2)
                self.assertIn("baseline", err)

    def test_sixteen_bit_images_are_refused_rather_than_compared_coarsely(self):
        first = self.write("a.png", png(1, 1, 0, 16, [bytes((0x12, 0x00))], 2))
        second = self.write("b.png", png(1, 1, 0, 16, [bytes((0x12, 0xFF))], 2))
        code, out, err = self.run_main(first, second)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("16-bit", err)


class CommandLineTest(Files):
    def test_runs_as_an_isolated_script(self):
        pixels = gradient(3, 3)
        first = self.write("a.png", rgba_png(pixels))
        changed = [list(row) for row in pixels]
        changed[0][0] = (1, 2, 3, 4)
        second = self.write("b.png", rgba_png(changed))
        same = subprocess.run([sys.executable, "-I", SCRIPT, first, first], capture_output=True)
        self.assertEqual((same.returncode, same.stdout.strip()), (0, b"identical: 3x3"))
        diff = subprocess.run([sys.executable, "-I", SCRIPT, first, second], capture_output=True)
        self.assertEqual(diff.returncode, 1)
        self.assertTrue(diff.stdout.startswith(b"different: 1 of 9 pixels"), diff.stdout)

    def test_error_output_is_ascii_bytes_when_piped(self):
        bad = self.write("bad.png", b"bad")
        result = subprocess.run([sys.executable, "-I", SCRIPT, bad, bad], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr.strip(), b"cannot compare: baseline file: not a PNG file")


if __name__ == "__main__":
    unittest.main()
