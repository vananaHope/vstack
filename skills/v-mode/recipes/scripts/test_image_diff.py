"""image_diff.py의 테스트. 실행: python -m unittest test_image_diff.py (이 폴더에서)

PNG는 테스트가 직접 만든다. 필터와 색 형식마다 풀어 낸 픽셀이 넣은 픽셀과 같은지,
명령줄의 출력과 종료 코드가 문서대로인지 본다.
"""

import io
import os
import shutil
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


def assemble(*chunks):
    """(이름, 본문) 목록으로 PNG를 만든다. 청크 순서와 구조를 마음대로 짤 때 쓴다."""
    return SIGNATURE + b"".join(chunk(kind, body) for kind, body in chunks)


def header(width, height, color, depth):
    return (b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, 0))


ONE_PIXEL = zlib.compress(b"\x00\x01\x02\x03\x04")  # 필터 0 + RGBA 한 픽셀
ONE_INDEX = zlib.compress(b"\x00\x00")  # 필터 0 + 팔레트 번호 0(8비트 회색 한 픽셀로도 쓴다)
END = (b"IEND", b"")


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
        changed[1][6] = (0, 0, 200, 255)  # 큰 차이가 먼저 나온다: 마지막 픽셀의 차이가 아니라 최댓값이어야 한다
        changed[5][2] = (40, 0, 0, 255)
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

    def test_extra_chunks_and_empty_idat_do_not_change_the_pixels(self):
        plain = self.write("a.png", assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL), END))
        dressed = self.write("b.png", assemble(header(1, 1, 6, 8), (b"tEXt", b"Software\x00x"), (b"pHYs", b"\x00" * 9),
                                               (b"IDAT", b""), (b"IDAT", ONE_PIXEL[:3]), (b"IDAT", ONE_PIXEL[3:]),
                                               (b"IDAT", b""), (b"tIME", b"\x00" * 7), END))
        self.assertEqual(self.run_main(plain, dressed), (0, "identical: 1x1", ""))

    def test_identical_palette_images_are_identical(self):
        palette = bytes((9, 9, 9, 200, 0, 0))
        data = png(2, 1, 3, 8, [bytes((0, 1))], 1, palette=palette)
        self.assertEqual(self.run_main(self.write("a.png", data), self.write("b.png", data)), (0, "identical: 2x1", ""))

    def test_the_same_data_under_a_different_palette_is_different(self):
        first = self.write("a.png", png(1, 1, 3, 8, [bytes((0,))], 1, palette=bytes((9, 9, 9))))
        second = self.write("b.png", png(1, 1, 3, 8, [bytes((0,))], 1, palette=bytes((9, 9, 12))))
        self.assertEqual(self.run_main(first, second),
                         (1, "different: 1 of 1 pixels (100.000%), bbox 0,0-0,0, max channel delta 3", ""))

    def test_the_same_data_read_at_a_different_size_is_different(self):
        data = (b"IDAT", zlib.compress(b"\x00\x11\x22\x00\x33\x44"))  # 2x2로도 5x1로도 맞는 데이터
        first = self.write("a.png", assemble(header(2, 2, 0, 8), data, END))
        second = self.write("b.png", assemble(header(5, 1, 0, 8), data, END))
        self.assertEqual(self.run_main(first, second), (1, "different: size 2x2 vs 5x1", ""))

    def test_the_same_data_read_at_a_different_bit_depth_is_different(self):
        data = (b"IDAT", zlib.compress(b"\x00\x80"))  # 8비트로는 회색 128, 4비트로는 8(=136)
        first = self.write("a.png", assemble(header(1, 1, 0, 8), data, END))
        second = self.write("b.png", assemble(header(1, 1, 0, 4), data, END))
        self.assertEqual(self.run_main(first, second),
                         (1, "different: 1 of 1 pixels (100.000%), bbox 0,0-0,0, max channel delta 8", ""))

    def test_the_same_data_read_as_gray_or_as_palette_is_different(self):
        palette = (b"PLTE", bytes((9, 9, 9)))
        first = self.write("a.png", assemble(header(1, 1, 0, 8), palette, (b"IDAT", ONE_INDEX), END))
        second = self.write("b.png", assemble(header(1, 1, 3, 8), palette, (b"IDAT", ONE_INDEX), END))
        self.assertEqual(self.run_main(first, second),
                         (1, "different: 1 of 1 pixels (100.000%), bbox 0,0-0,0, max channel delta 9", ""))

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
            # 청크 구조가 규격과 다른 것들. 모두 CRC는 맞다
            "idat-before-header.png": assemble((b"IDAT", ONE_PIXEL), header(1, 1, 6, 8), END),
            "two-headers.png": assemble(header(1, 1, 6, 8), header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL), END),
            "split-idat.png": assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL[:4]), (b"tEXt", b"k\x00v"),
                                       (b"IDAT", ONE_PIXEL[4:]), END),
            "iend-with-body.png": assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL), (b"IEND", b"x")),
            "data-after-iend.png": assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL), END) + b"junk",
            "unknown-critical.png": assemble(header(1, 1, 6, 8), (b"ABCD", b""), (b"IDAT", ONE_PIXEL), END),
            "palette-length.png": assemble(header(1, 1, 3, 8), (b"PLTE", b"\x01\x02\x03\x04"),
                                           (b"IDAT", ONE_INDEX), END),
            "no-palette.png": assemble(header(1, 1, 3, 8), (b"IDAT", ONE_INDEX), END),
            "two-palettes.png": assemble(header(1, 1, 3, 8), (b"PLTE", b"\x01\x02\x03"), (b"PLTE", b"\x01\x02\x03"),
                                         (b"IDAT", ONE_INDEX), END),
            "palette-after-idat.png": assemble(header(1, 1, 3, 8), (b"IDAT", ONE_INDEX), (b"PLTE", b"\x01\x02\x03"),
                                               END),
            "long-palette-trns.png": assemble(header(1, 1, 3, 8), (b"PLTE", b"\x01\x02\x03"), (b"tRNS", b"\x10\x20"),
                                              (b"IDAT", ONE_INDEX), END),
            "trns-with-alpha.png": assemble(header(1, 1, 6, 8), (b"tRNS", b"\x00\x01"), (b"IDAT", ONE_PIXEL), END),
            "two-trns.png": assemble(header(1, 1, 3, 8), (b"PLTE", b"\x01\x02\x03"), (b"tRNS", b"\x10"),
                                     (b"tRNS", b"\x10"), (b"IDAT", ONE_INDEX), END),
            "trns-after-idat.png": assemble(header(1, 1, 0, 8), (b"IDAT", ONE_INDEX), (b"tRNS", b"\x00\x40"), END),
            "gray-trns-length.png": assemble(header(1, 1, 0, 8), (b"tRNS", b"\x00"), (b"IDAT", ONE_INDEX), END),
            "rgb-trns-length.png": assemble(header(1, 1, 2, 8), (b"tRNS", b"\x00\x01"),
                                            (b"IDAT", zlib.compress(b"\x00\x01\x02\x03")), END),
            "extra-after-stream.png": assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL + b"zz"), END),
            "unfinished-stream.png": assemble(header(1, 1, 6, 8), (b"IDAT", ONE_PIXEL[:-2]), END),
            "zero-size.png": assemble(header(0, 1, 6, 8), (b"IDAT", zlib.compress(b"\x00")), END),
            "short-header.png": assemble((b"IHDR", b"\x00" * 12), (b"IDAT", ONE_PIXEL), END),
            "trns-before-palette.png": assemble(header(1, 1, 3, 8), (b"tRNS", b"\x10"), (b"PLTE", b"\x01\x02\x03"),
                                                (b"IDAT", ONE_INDEX), END),
            "compression-method.png": assemble((b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 1, 0, 0)),
                                               (b"IDAT", ONE_PIXEL), END),
            "filter-method.png": assemble((b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 1, 0)),
                                          (b"IDAT", ONE_PIXEL), END),
            "big-palette.png": assemble(header(1, 1, 3, 1), (b"PLTE", b"\x01\x02\x03" * 3), (b"IDAT", ONE_INDEX), END),
            "unknown-filter.png": assemble(header(1, 1, 6, 8), (b"IDAT", zlib.compress(b"\x05\x01\x02\x03\x04")), END),
            # 픽셀을 풀어야 드러나는 것: 팔레트에 없는 번호
            "palette-index.png": assemble(header(1, 1, 3, 8), (b"PLTE", b"\x01\x02\x03"),
                                          (b"IDAT", zlib.compress(b"\x00\x01")), END),
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

    def test_a_broken_file_is_never_identical_to_itself(self):
        # 머리 정보와 데이터가 같으면 픽셀을 풀지 않는 지름길이, 깨진 파일 한 쌍을 같다고 하면 안 된다
        for name, data in self.cases().items():
            if data is None:
                continue
            path = self.write(name, data)
            copy = self.write("copy-" + name, data)
            with self.subTest(file=name):
                self.assertEqual(self.run_main(path, path)[:2], (2, ""))
                self.assertEqual(self.run_main(path, copy)[:2], (2, ""))

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


class FolderTest(Files):
    """폴더 두 개를 비교하는 방식. 이름이 같은 PNG끼리 비교하고, 빠진 PNG를 드러낸다."""

    def setUp(self):
        super().setUp()
        self.pixels = gradient(3, 3)
        self.changed = [list(row) for row in self.pixels]
        self.changed[1][2] = (1, 2, 3, 4)
        self.base = os.path.join(self.dir.name, "base")
        self.new = os.path.join(self.dir.name, "new")
        os.makedirs(self.base)
        os.makedirs(self.new)

    def put(self, folder, name, pixels=None, data=None):
        path = os.path.join(folder, *name.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(rgba_png(pixels or self.pixels) if data is None else data)

    def both(self, *names):
        for name in names:
            self.put(self.base, name)
            self.put(self.new, name)

    def listing(self, text, encoding="utf-8"):
        path = os.path.join(self.dir.name, "list.txt")
        with open(path, "w", encoding=encoding, newline="") as handle:
            handle.write(text)
        return path

    def test_every_png_identical_exits_zero_with_a_line_each_and_a_summary(self):
        self.both("one.png", "sub/two.png", "sub/deep/THREE.PNG")
        self.put(self.new, "notes.txt", data=b"not a picture")
        code, out, err = self.run_main(self.base, self.new)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines(), [
            "one.png: identical: 3x3",
            "sub/deep/THREE.PNG: identical: 3x3",
            "sub/two.png: identical: 3x3",
            "summary: 3 listed, 3 identical, 0 different, 0 missing, 0 cannot compare",
        ])

    def test_a_changed_png_exits_one_and_names_it(self):
        self.both("one.png")
        self.put(self.base, "sub/two.png")
        self.put(self.new, "sub/two.png", self.changed)
        code, out, _ = self.run_main(self.base, self.new)
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines()[1:], [
            "sub/two.png: different: 1 of 9 pixels (11.111%), bbox 2,1-2,1, max channel delta 251",
            "summary: 2 listed, 1 identical, 1 different, 0 missing, 0 cannot compare",
        ])

    def test_a_png_in_only_one_folder_is_missing_and_exits_two(self):
        self.both("one.png")
        self.put(self.base, "gone.png")
        self.put(self.new, "extra.png")
        code, out, err = self.run_main(self.base, self.new)
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(out.splitlines(), [
            "extra.png: missing: not in the baseline folder",
            "gone.png: missing: not in the candidate folder",
            "one.png: identical: 3x3",
            "summary: 3 listed, 1 identical, 0 different, 2 missing, 0 cannot compare",
        ])

    def test_missing_outranks_different_in_the_exit_code(self):
        self.put(self.base, "one.png")
        self.put(self.new, "one.png", self.changed)
        self.put(self.base, "gone.png")
        code, out, _ = self.run_main(self.base, self.new)
        self.assertEqual(code, 2)
        self.assertEqual(out.splitlines()[-1], "summary: 2 listed, 0 identical, 1 different, 1 missing, 0 cannot compare")

    def test_an_unreadable_png_is_reported_on_its_line_and_exits_two(self):
        self.both("one.png")
        self.put(self.base, "bad.png")
        self.put(self.new, "bad.png", data=b"bad")
        code, out, err = self.run_main(self.base, self.new)
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(out.splitlines(), [
            "bad.png: cannot compare: candidate file: not a PNG file",
            "one.png: identical: 3x3",
            "summary: 2 listed, 1 identical, 0 different, 0 missing, 1 cannot compare",
        ])

    def test_expect_compares_only_the_listed_names_in_list_order(self):
        self.both("b.png", "a.png")
        self.put(self.base, "unlisted.png")
        self.put(self.new, "unlisted.png", self.changed)
        code, out, _ = self.run_main(self.base, self.new, "--expect", self.listing("b.png\na.png\n"))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "b.png: identical: 3x3",
            "a.png: identical: 3x3",
            "summary: 2 listed, 2 identical, 0 different, 0 missing, 0 cannot compare",
        ])

    def test_expect_reports_a_listed_png_that_neither_folder_has(self):
        # 기준을 찍을 때도 뒤에 찍을 때도 실패한 화면은 폴더만 봐서는 드러나지 않는다. 목록이 드러낸다
        self.both("one.png")
        self.assertEqual(self.run_main(self.base, self.new)[0], 0)
        code, out, _ = self.run_main(self.base, self.new, "--expect", self.listing("one.png\nnever-shot.png\n"))
        self.assertEqual(code, 2)
        self.assertEqual(out.splitlines()[1:], [
            "never-shot.png: missing: in neither folder",
            "summary: 2 listed, 1 identical, 0 different, 1 missing, 0 cannot compare",
        ])

    def test_expect_list_format(self):
        self.both("one.png", "sub/two.png")
        bom = chr(0xFEFF)  # Windows의 편집기와 PowerShell 5가 UTF-8 파일 앞에 붙인다
        text = bom + "# screens\r\n\r\none.png\ttarget, empty state\r\nsub\\two.png\t# note\r\none.png\r\n"
        code, out, _ = self.run_main(self.base, self.new, "--expect", self.listing(text))
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "one.png: identical: 3x3",
            "sub/two.png: identical: 3x3",
            "summary: 2 listed, 2 identical, 0 different, 0 missing, 0 cannot compare",
        ])

    def test_expect_refuses_names_that_point_outside_the_folders(self):
        # 절대 경로를 받으면 같은 파일을 자기 자신과 비교해 "같다"가 나온다
        self.both("one.png")
        absolute = os.path.join(self.base, "one.png")
        entries = [absolute, "../base/one.png", "sub/../../base/one.png", "/one.png"]
        if os.name == "nt":
            entries.append("C:one.png")  # 드라이브만 적은 상대 경로. 폴더와 이으면 폴더가 버려진다
        for entry in entries:
            with self.subTest(entry=entry):
                code, out, err = self.run_main(self.base, self.new, "--expect", self.listing("one.png\n%s\n" % entry))
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("cannot compare: list entry is not a path inside the folders"), err)

    def link(self, target, path):
        """path를 target 폴더로 가는 링크로 만든다. 심볼릭 링크를 못 만드는 Windows에서는 junction을 쓴다."""
        try:
            os.symlink(target, path, target_is_directory=True)
        except (OSError, NotImplementedError):
            if os.name != "nt":
                self.skipTest("cannot create a directory link here")
            import _winapi
            _winapi.CreateJunction(target, path)

    def test_a_png_reached_through_a_link_that_leaves_the_folder_is_refused(self):
        # 두 폴더 안의 링크가 같은 바깥 폴더를 가리키면, 찍은 것이 없어도 바깥 파일을 자기 자신과 비교하게 된다
        outside = os.path.join(self.dir.name, "outside")
        self.put(outside, "shared.png")
        self.both("one.png")
        self.link(outside, os.path.join(self.base, "external"))
        self.link(outside, os.path.join(self.new, "external"))
        listing = self.listing("one.png\nexternal/shared.png\n")
        code, out, _ = self.run_main(self.base, self.new, "--expect", listing)
        self.assertEqual(code, 2)
        self.assertEqual(out.splitlines(), [
            "one.png: identical: 3x3",
            "external/shared.png: cannot compare: baseline file: resolves to a path outside the folder",
            "summary: 2 listed, 1 identical, 0 different, 0 missing, 1 cannot compare",
        ])
        self.assertEqual(self.run_main(self.base, self.new)[0], 2)  # 목록 없이 폴더를 훑어도 통과하지 않는다

    def test_a_link_that_leaves_the_folder_on_one_side_only_is_refused(self):
        outside = os.path.join(self.dir.name, "outside")
        self.put(outside, "shared.png")
        listing = self.listing("external/shared.png\n")
        for linked, real, label in ((self.base, self.new, "baseline"), (self.new, self.base, "candidate")):
            with self.subTest(side=label):
                self.link_one_side(linked, real, outside)
                code, out, _ = self.run_main(self.base, self.new, "--expect", listing)
                self.assertEqual(code, 2)
                self.assertEqual(out.splitlines()[0],
                                 "external/shared.png: cannot compare: %s file: resolves to a path outside the folder" % label)

    def link_one_side(self, linked, real, outside):
        """linked 쪽의 external은 바깥으로 가는 링크, real 쪽의 external은 진짜 폴더로 만든다."""
        for folder in (linked, real):
            path = os.path.join(folder, "external")
            if os.path.lexists(path):
                try:
                    os.unlink(path)  # 링크나 junction
                except OSError:
                    shutil.rmtree(path)
        self.link(outside, os.path.join(linked, "external"))
        self.put(real, "external/shared.png")

    def test_a_link_that_stays_inside_the_folder_is_followed(self):
        for folder in (self.base, self.new):
            self.put(folder, "real/shot.png")
            self.link(os.path.join(folder, "real"), os.path.join(folder, "alias"))
        code, out, _ = self.run_main(self.base, self.new, "--expect", self.listing("alias/shot.png\n"))
        self.assertEqual((code, out.splitlines()[0]), (0, "alias/shot.png: identical: 3x3"))

    @unittest.skipUnless(os.name == "nt", "names differ only in case on a case-insensitive file system")
    def test_names_that_differ_only_in_case_are_one_file_on_windows(self):
        self.put(self.base, "Case.PNG")
        self.put(self.new, "case.png")
        code, out, _ = self.run_main(self.base, self.new)
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[-1], "summary: 1 listed, 1 identical, 0 different, 0 missing, 0 cannot compare")
        listing = self.listing("case.png\nCASE.png\n")
        code, out, _ = self.run_main(self.base, self.new, "--expect", listing)
        self.assertEqual(out.splitlines()[-1], "summary: 1 listed, 1 identical, 0 different, 0 missing, 0 cannot compare")

    def test_nothing_to_compare_exits_two(self):
        self.put(self.base, "notes.txt", data=b"x")
        code, out, err = self.run_main(self.base, self.new)
        self.assertEqual((code, out, err), (2, "", "cannot compare: no PNG files to compare"))
        self.both("one.png")
        code, out, err = self.run_main(self.base, self.new, "--expect", self.listing("# nothing\n\n"))
        self.assertEqual((code, out, err), (2, "", "cannot compare: no PNG files to compare"))

    def test_an_unreadable_list_exits_two(self):
        self.both("one.png")
        missing = os.path.join(self.dir.name, "no-list.txt")
        code, out, err = self.run_main(self.base, self.new, "--expect", missing)
        self.assertEqual((code, out, err), (2, "", "cannot compare: cannot read the list file (FileNotFoundError)"))
        code, out, err = self.run_main(self.base, self.new, "--expect", self.listing("one.png\n", encoding="utf-16"))
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("cannot compare: cannot read the list file"), err)

    def test_a_folder_and_a_file_cannot_be_compared(self):
        self.both("one.png")
        file = os.path.join(self.base, "one.png")
        self.assertEqual(self.run_main(self.base, file),
                         (2, "", "cannot compare: the candidate path is not a folder (give two PNG files or two folders)"))
        self.assertEqual(self.run_main(os.path.join(self.dir.name, "not-shot"), self.new),
                         (2, "", "cannot compare: the baseline path is not a folder (give two PNG files or two folders)"))
        self.assertEqual(self.run_main(file, file, "--expect", self.listing("one.png\n")),
                         (2, "", "cannot compare: --expect needs two folders"))

    def test_names_outside_ascii_are_escaped(self):
        self.both("한글.png")
        code, out, _ = self.run_main(self.base, self.new)
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "\\ud55c\\uae00.png: identical: 3x3")
        self.assertTrue(out.isascii())

    def test_runs_as_an_isolated_script(self):
        self.both("one.png")
        self.put(self.base, "two.png")
        self.put(self.new, "two.png", self.changed)
        listing = self.listing("one.png\n")
        same = subprocess.run([sys.executable, "-I", SCRIPT, self.base, self.new, "--expect", listing],
                              capture_output=True)
        self.assertEqual(same.returncode, 0)
        self.assertEqual(same.stdout.splitlines()[-1],
                         b"summary: 1 listed, 1 identical, 0 different, 0 missing, 0 cannot compare")
        diff = subprocess.run([sys.executable, "-I", SCRIPT, self.base, self.new], capture_output=True)
        self.assertEqual(diff.returncode, 1)


if __name__ == "__main__":
    unittest.main()
