"""PNG 두 장, 또는 두 폴더의 PNG들이 픽셀 단위로 같은지 본다. 표준 라이브러리만 쓴다.

사용법:
    python -I image_diff.py <기준.png> <새.png>
    python -I image_diff.py <기준 폴더> <새 폴더> [--expect <목록 파일>]

- 같은 위치의 픽셀을 RGBA로 비교한다. 채널 값이 하나라도 다르면 다른 것이다. 허용 오차는 없다.
- 크기가 다르면 다른 것으로 본다.
- 파일의 바이트가 달라도(압축, 필터, 부가 정보) 픽셀이 같으면 같은 것이다.

파일 두 개일 때의 출력(한 줄, 표준 출력):
    identical: <폭>x<높이>
    different: <다른 픽셀 수> of <전체> pixels (<비율>%), bbox <x0>,<y0>-<x1>,<y1>, max channel delta <D>
    different: size <폭>x<높이> vs <폭>x<높이>
비교하지 못하면 표준 오류에 `cannot compare: <이유>`를 낸다. 출력은 모두 ASCII다
(Windows에서 파이프로 받아도 깨지지 않게).

폴더 두 개일 때: 이름(폴더 기준 상대 경로, `/`로 구분)이 같은 PNG끼리 비교해 PNG마다 한 줄,
끝에 합계 한 줄을 표준 출력에 낸다. PNG마다 프로세스를 띄우지 않으므로 여러 장은 이쪽으로 비교한다.
    <이름>: identical: ... / different: ... / cannot compare: ...
    <이름>: missing: not in the baseline folder / not in the candidate folder / in neither folder
    summary: <N> listed, <i> identical, <d> different, <m> missing, <c> cannot compare
- `--expect <목록 파일>`을 주면 목록에 적힌 이름만 본다. 목록에 있는데 폴더에 없는 PNG는 `missing`이다.
  목록은 UTF-8, 한 줄에 이름 하나다. 탭 뒤는 메모로 보고 읽지 않는다. 빈 줄과 `#`으로 시작하는 줄은 건너뛴다.
  이름은 두 폴더 안의 상대 경로여야 한다(절대 경로, 드라이브 글자, `..`는 받지 않는다).
- 링크(심볼릭 링크, junction)를 따라간 실제 파일이 그 폴더 밖에 있으면 비교하지 않는다(`cannot compare`).
  두 폴더의 링크가 같은 바깥 파일을 가리키면 찍은 것이 없어도 같다고 나오기 때문이다.
- 대소문자만 다른 이름은 다른 이름으로 본다. 파일 시스템이 둘을 같은 파일로 여는 곳에서는 같은 파일을 두 번 센다.
- `--expect`가 없으면 두 폴더 어느 쪽에든 있는 PNG를 모두 본다. 한쪽에만 있으면 `missing`이다.
  두 폴더 모두에서 빠진 PNG는 이 방식으로는 드러나지 않는다. 찍혀야 할 것이 정해져 있으면 목록을 준다.

종료 코드: 0 = 같다(폴더: 모두 같다), 1 = 다르다(폴더: 다른 것이 있다), 2 = 비교하지 못했다
(폴더: 빠졌거나 비교하지 못한 PNG가 하나라도 있다, 또는 비교할 PNG가 하나도 없다. 다른 것이 함께 있어도 2다)
비교하지 못하는 경우: 파일 없음, PNG 아님, 인터레이스 PNG, 16비트 PNG, 모르는 필수 청크가 있는 PNG,
깨졌거나 끊긴 PNG. 깨진 것으로 보는 것: CRC 불일치, 청크 순서나 개수가 규격과 다름(IHDR가 맨 앞에 하나,
IDAT는 서로 붙어 있음, PLTE·tRNS는 IDAT 앞, tRNS는 PLTE 뒤), IEND가 없거나 본문이 있거나 뒤에 바이트가 남음,
IHDR의 압축 방식·필터 방식이 0이 아님, PLTE·tRNS 길이가 색 형식이나 비트 깊이와 맞지 않음,
압축 데이터가 덜 끝났거나 뒤에 남는 바이트가 있음, 데이터 길이 불일치, 모르는 필터 종류, 팔레트 밖의 번호.
규격의 모든 조항을 검사하는 것은 아니다. 지원: 인터레이스 없는 PNG, 색 형식 0·2·3·4·6, 비트 깊이 1·2·4·8
(tRNS 투명도 포함). 화면 스크린샷은 보통 8비트 RGB나 RGBA다.

빠르기: 두 파일의 머리 정보와 압축을 푼 데이터가 같으면 픽셀을 풀지 않고 같다고 한다(같은 수단으로 찍은
같은 화면은 보통 이 경우다). 그 밖에는 두 장의 픽셀을 모두 푼다.
"""

import argparse
import collections
import os
import struct
import sys
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
DEPTHS = {0: (1, 2, 4, 8), 2: (8,), 3: (1, 2, 4, 8), 4: (8,), 6: (8,)}

# 검사를 마친 PNG 한 장. raw는 압축만 푼 데이터(줄마다 필터 종류 1바이트 + 필터가 걸린 줄)다.
Image = collections.namedtuple("Image", "width height depth color palette transparency raw")


class Unsupported(Exception):
    pass


def read_chunks(data):
    """청크를 차례로 내준다. 끊겼거나, CRC가 틀리거나, 구조가 PNG 규격과 다르면 Unsupported.

    보는 것: IHDR가 맨 앞에 하나, IDAT는 서로 붙어 있음, PLTE는 IDAT와 tRNS 앞에 하나, IEND는 본문 없이 파일의 끝,
    모르는 필수 청크(이름 첫 글자가 대문자) 없음. 부가 청크(tEXt 등)는 건너뛴다.
    """
    if data[:8] != SIGNATURE:
        raise Unsupported("not a PNG file")
    pos = 8
    seen = []
    while pos < len(data):
        if pos + 8 > len(data):
            raise Unsupported("truncated PNG (chunk header)")
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        name = kind.decode("ascii", "replace")
        end = pos + 12 + length
        if end > len(data):
            raise Unsupported("truncated PNG (chunk %s)" % name)
        body = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[end - 4:end])
        if crc != zlib.crc32(kind + body) & 0xFFFFFFFF:
            raise Unsupported("corrupt PNG (bad CRC in chunk %s)" % name)
        if not seen and kind != b"IHDR":
            raise Unsupported("corrupt PNG (first chunk is %s, not IHDR)" % name)
        if kind in (b"IHDR", b"PLTE") and kind in seen:
            raise Unsupported("corrupt PNG (more than one %s chunk)" % name)
        if kind == b"IDAT" and b"IDAT" in seen and seen[-1] != b"IDAT":
            raise Unsupported("corrupt PNG (IDAT chunks are not consecutive)")
        if kind in (b"PLTE", b"tRNS") and b"IDAT" in seen:
            raise Unsupported("corrupt PNG (%s after IDAT)" % name)
        if kind == b"PLTE" and b"tRNS" in seen:
            raise Unsupported("corrupt PNG (tRNS before PLTE)")
        if kind == b"tRNS" and b"tRNS" in seen:
            raise Unsupported("corrupt PNG (more than one tRNS chunk)")
        if kind not in (b"IHDR", b"PLTE", b"IDAT", b"IEND") and not kind[:1].islower():
            raise Unsupported("unsupported PNG (unknown critical chunk %s)" % name)
        seen.append(kind)
        if kind == b"IEND":
            if length != 0:
                raise Unsupported("corrupt PNG (IEND chunk has a body)")
            if end != len(data):
                raise Unsupported("corrupt PNG (data after IEND)")
            yield kind, body
            return
        yield kind, body
        pos = end
    raise Unsupported("truncated PNG (no IEND chunk)")


def inflate(compressed):
    """IDAT를 이은 압축 스트림을 푼다. 스트림이 끝나지 않았거나 뒤에 남는 바이트가 있으면 Unsupported."""
    stream = zlib.decompressobj()
    raw = stream.decompress(compressed)
    if not stream.eof:
        raise Unsupported("corrupt PNG (compressed image data is incomplete)")
    if stream.unused_data:
        raise Unsupported("corrupt PNG (extra bytes after the compressed image data)")
    return raw


def layout(width, depth, color):
    """(한 줄의 바이트 수, 필터가 왼쪽 픽셀로 보는 거리)를 돌려준다."""
    bits = CHANNELS[color] * depth
    return (width * bits + 7) // 8, max(1, bits // 8)


def parse(path):
    """파일을 읽어 검사하고 Image를 돌려준다. 픽셀은 아직 풀지 않는다.

    픽셀을 풀어야만 알 수 있는 것(팔레트 밖의 번호)을 뺀 모든 검사를 여기서 한다.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    header = None
    palette = None
    transparency = None
    idat = []
    for kind, body in read_chunks(data):
        if kind == b"IHDR":
            if len(body) != 13:
                raise Unsupported("corrupt PNG (IHDR length)")
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = body
        elif kind == b"tRNS":
            transparency = body
        elif kind == b"IDAT":
            idat.append(body)
    if header is None or not idat:
        raise Unsupported("corrupt PNG (no IHDR or IDAT)")
    width, height, depth, color, compression, filter_method, interlace = header
    if width == 0 or height == 0:
        raise Unsupported("corrupt PNG (zero size)")
    if compression != 0 or filter_method != 0:
        raise Unsupported("corrupt PNG (unknown compression or filter method)")
    if interlace != 0:
        raise Unsupported("interlaced PNG is not supported")
    if depth == 16:
        raise Unsupported("16-bit PNG is not supported")
    if color not in CHANNELS or depth not in DEPTHS[color]:
        raise Unsupported("unsupported PNG format (color type %d, bit depth %d)" % (color, depth))
    if palette is not None and (len(palette) % 3 != 0 or not 3 <= len(palette) <= 768):
        raise Unsupported("corrupt PNG (PLTE length)")
    if color == 3 and palette is None:
        raise Unsupported("corrupt PNG (palette image without PLTE)")
    if color == 3 and len(palette) // 3 > 1 << depth:
        raise Unsupported("corrupt PNG (palette has more entries than the bit depth allows)")
    # tRNS: 색 형식 0은 투명한 회색 값 하나, 2는 투명한 RGB 값 하나(둘 다 16비트로 적힌다), 3은 팔레트 번호별 알파
    if transparency is not None:
        if color == 0:
            if len(transparency) != 2:
                raise Unsupported("corrupt PNG (tRNS length)")
        elif color == 2:
            if len(transparency) != 6:
                raise Unsupported("corrupt PNG (tRNS length)")
        elif color == 3:
            if len(transparency) > len(palette) // 3:
                raise Unsupported("corrupt PNG (tRNS longer than the palette)")
        else:
            raise Unsupported("corrupt PNG (tRNS in an image that has an alpha channel)")
    raw = inflate(b"".join(idat))
    stride, _ = layout(width, depth, color)
    if len(raw) != height * (stride + 1):
        raise Unsupported("corrupt PNG (image data is %d bytes, expected %d)" % (len(raw), height * (stride + 1)))
    worst = max(raw[0::stride + 1])
    if worst > 4:
        raise Unsupported("corrupt PNG (unknown filter type %d)" % worst)
    return Image(width, height, depth, color, palette, transparency, raw)


def unfilter(raw, height, stride, bpp):
    """PNG 필터를 풀어 줄마다 bytes로 돌려준다. 길이와 필터 종류는 parse가 이미 봤다."""
    rows = []
    prev = bytes(stride)
    pos = 0
    for _ in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if kind == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif kind == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif kind == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        prev = bytes(line)
        rows.append(prev)
    return rows


def samples(row, count, depth):
    """한 줄에서 샘플 값(비트 깊이 그대로) count개를 꺼낸다."""
    if depth == 8:
        return list(row[:count])
    out = []
    mask = (1 << depth) - 1
    for byte in row:
        for shift in range(8 - depth, -1, -depth):
            out.append((byte >> shift) & mask)
            if len(out) == count:
                return out
    return out


def pixels(image):
    """줄마다 RGBA bytes를 돌려준다. 팔레트 밖의 번호가 나오면 Unsupported."""
    width, height, depth, color, palette, transparency, raw = image
    stride, bpp = layout(width, depth, color)
    rows = unfilter(raw, height, stride, bpp)
    if color == 6:  # 8비트 RGBA는 푼 줄이 그대로 답이다
        return rows
    out = []
    if color == 2 and transparency is None:  # 8비트 RGB: 채널을 통째로 옮기고 알파를 255로 채운다
        for row in rows:
            rgba = bytearray(b"\xff") * (width * 4)
            rgba[0::4] = row[0::3]
            rgba[1::4] = row[1::3]
            rgba[2::4] = row[2::3]
            out.append(bytes(rgba))
        return out
    channels = CHANNELS[color]
    scale = 255 // ((1 << depth) - 1)
    key = None
    if transparency is not None and color == 0:
        key = struct.unpack(">H", transparency)[0]
    elif transparency is not None and color == 2:
        key = struct.unpack(">HHH", transparency)
    for row in rows:
        values = samples(row, width * channels, depth)
        rgba = bytearray(width * 4)
        for x in range(width):
            base = x * channels
            if color == 3:
                index = values[base]
                if index * 3 + 2 >= len(palette):
                    raise Unsupported("corrupt PNG (palette index out of range)")
                r, g, b = palette[index * 3:index * 3 + 3]
                a = transparency[index] if transparency and index < len(transparency) else 255
            elif color == 0:
                r = g = b = values[base] * scale
                a = 0 if values[base] == key else 255
            elif color == 4:
                r = g = b = values[base]
                a = values[base + 1]
            else:
                r, g, b = values[base], values[base + 1], values[base + 2]
                a = 0 if (r, g, b) == key else 255
            rgba[x * 4:x * 4 + 4] = bytes((r, g, b, a))
        out.append(bytes(rgba))
    return out


def decode(path):
    """(폭, 높이, [줄마다 RGBA bytes])를 돌려준다."""
    image = parse(path)
    return image.width, image.height, pixels(image)


def compare(first, second):
    """(폭, 높이, 줄들) 둘을 받아 (같은가, 설명)을 돌려준다."""
    width_a, height_a, rows_a = first
    width_b, height_b, rows_b = second
    if (width_a, height_a) != (width_b, height_b):
        return False, "different: size %dx%d vs %dx%d" % (width_a, height_a, width_b, height_b)
    differing = 0
    max_delta = 0
    x0 = y0 = None
    x1 = y1 = -1
    for y in range(height_a):
        row_a, row_b = rows_a[y], rows_b[y]
        if row_a == row_b:
            continue
        for x in range(width_a):
            base = x * 4
            if row_a[base:base + 4] == row_b[base:base + 4]:
                continue
            differing += 1
            max_delta = max(max_delta, max(abs(row_a[base + k] - row_b[base + k]) for k in range(4)))
            x0 = x if x0 is None else min(x0, x)
            y0 = y if y0 is None else y0
            x1 = max(x1, x)
            y1 = y
    if differing == 0:
        return True, "identical: %dx%d" % (width_a, height_a)
    total = width_a * height_a
    return False, "different: %d of %d pixels (%.3f%%), bbox %d,%d-%d,%d, max channel delta %d" % (
        differing, total, differing * 100.0 / total, x0, y0, x1, y1, max_delta)


def plain(text):
    """ASCII가 아닌 글자를 \\u 표기로 바꾼다."""
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


def compare_files(baseline, candidate):
    """PNG 두 장을 비교해 (종료 코드, 한 줄)을 돌려준다."""
    images = []
    for label, path in (("baseline", baseline), ("candidate", candidate)):
        try:
            images.append(parse(path))
        except OSError as error:
            return 2, "cannot compare: cannot read the %s file (%s)" % (label, type(error).__name__)
        except (Unsupported, zlib.error, struct.error) as error:
            return 2, "cannot compare: %s file: %s" % (label, plain(error))
    first, second = images
    # 머리 정보와 압축을 푼 데이터가 같으면 픽셀도 같다. 팔레트 그림만은 번호가 범위 안인지 풀어서 본다.
    same = first == second
    if same and first.color != 3:
        return 0, "identical: %dx%d" % (first.width, first.height)
    decoded = []
    for label, image in (("baseline", first), ("candidate", second)):
        if same and decoded:
            decoded.append(decoded[0])
            continue
        try:
            decoded.append((image.width, image.height, pixels(image)))
        except Unsupported as error:
            return 2, "cannot compare: %s file: %s" % (label, plain(error))
    same, text = compare(*decoded)
    return (0 if same else 1), text


def unique(names):
    """글자가 똑같은 이름을 한 번만 남긴다. 순서는 그대로다.

    대소문자만 다른 이름은 합치지 않는다. 그 둘이 같은 파일인지는 폴더마다 다르다(Windows에서도 폴더별로
    대소문자를 가리게 켤 수 있다). 합치면 서로 다른 PNG 하나를 비교에서 빠뜨릴 수 있다.
    """
    out = []
    for name in names:
        if name not in out:
            out.append(name)
    return out


def png_names(folder):
    """폴더 아래 모든 PNG의 이름(폴더 기준 상대 경로, `/`로 구분)."""
    names = []
    for root, _dirs, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(".png"):
                names.append(os.path.relpath(os.path.join(root, name), folder).replace(os.sep, "/"))
    return names


def expected_names(path):
    """목록 파일에서 이름을 읽는다. 폴더 밖을 가리키는 이름이 있으면 Unsupported."""
    names = []
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            name = line.split("\t")[0].strip().replace("\\", "/")
            if not name or name.startswith("#"):
                continue
            if name.startswith("/") or os.path.splitdrive(name)[0] or ".." in name.split("/"):
                raise Unsupported("list entry is not a path inside the folders: %s" % name)
            names.append(name)
    return unique(names)


def inside(folder, name):
    """folder 아래의 name이, 링크(심볼릭 링크, junction)를 따라간 뒤에도 folder 안에 있는가.

    두 폴더 안의 링크가 같은 바깥 파일을 가리키면, 찍은 것이 없어도 그 파일을 자기 자신과 비교해 같다고 하게 된다.
    경로의 글자가 아니라 파일 시스템이 같은 폴더라고 하는지로 본다. 글자를 소문자로 맞춰 견주면, 대소문자를
    가리는 폴더에서 이름의 대소문자만 다른 바깥 폴더를 안이라고 하게 된다.
    """
    root = os.path.realpath(folder)
    path = os.path.dirname(os.path.realpath(os.path.join(folder, name)))
    while True:
        try:
            if os.path.samefile(path, root):
                return True
        except OSError:
            return False
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def compare_folders(baseline, candidate, expect):
    """두 폴더를 비교해 줄들을 표준 출력에 내고 종료 코드를 돌려준다."""
    if expect is None:
        names = unique(sorted(png_names(baseline) + png_names(candidate)))
    else:
        try:
            names = expected_names(expect)
        except (OSError, UnicodeError) as error:
            print("cannot compare: cannot read the list file (%s)" % type(error).__name__, file=sys.stderr)
            return 2
        except Unsupported as error:
            print("cannot compare: %s" % plain(error), file=sys.stderr)
            return 2
    if not names:
        print("cannot compare: no PNG files to compare", file=sys.stderr)
        return 2
    counts = collections.Counter()
    for name in names:
        in_baseline = os.path.isfile(os.path.join(baseline, name))
        in_candidate = os.path.isfile(os.path.join(candidate, name))
        if in_baseline and not inside(baseline, name):
            counts["cannot compare"] += 1
            text = "cannot compare: baseline file: resolves to a path outside the folder"
        elif in_candidate and not inside(candidate, name):
            counts["cannot compare"] += 1
            text = "cannot compare: candidate file: resolves to a path outside the folder"
        elif in_baseline and in_candidate:
            code, text = compare_files(os.path.join(baseline, name), os.path.join(candidate, name))
            counts[("identical", "different", "cannot compare")[code]] += 1
        else:
            counts["missing"] += 1
            if in_baseline:
                text = "missing: not in the candidate folder"
            elif in_candidate:
                text = "missing: not in the baseline folder"
            else:
                text = "missing: in neither folder"
        print("%s: %s" % (plain(name), text))
    print("summary: %d listed, %d identical, %d different, %d missing, %d cannot compare" % (
        len(names), counts["identical"], counts["different"], counts["missing"], counts["cannot compare"]))
    if counts["missing"] or counts["cannot compare"]:
        return 2
    return 1 if counts["different"] else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two PNG files, or the PNG files of two folders, pixel by pixel.")
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--expect", metavar="LIST", help="folders only: compare exactly the PNG names listed in this file")
    args = parser.parse_args(argv)
    folders = [os.path.isdir(path) for path in (args.baseline, args.candidate)]
    if all(folders):
        return compare_folders(args.baseline, args.candidate, args.expect)
    if any(folders):
        label = "candidate" if folders[0] else "baseline"
        print("cannot compare: the %s path is not a folder (give two PNG files or two folders)" % label, file=sys.stderr)
        return 2
    if args.expect is not None:
        print("cannot compare: --expect needs two folders", file=sys.stderr)
        return 2
    code, text = compare_files(args.baseline, args.candidate)
    print(text, file=sys.stderr if code == 2 else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
