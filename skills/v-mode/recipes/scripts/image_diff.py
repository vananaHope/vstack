"""PNG 두 장이 픽셀 단위로 같은지 본다. 표준 라이브러리만 쓴다.

사용법:
    python -I image_diff.py <기준.png> <새.png> [--tolerance N]

- 같은 위치의 픽셀을 RGBA로 비교한다. 하나라도 다르면 다른 것이다.
- --tolerance N: 채널 값의 차이가 N 이하면 같은 것으로 본다. 기본 0. 스크린샷 수단이 같은 화면을
  두 번 찍어도 조금씩 다를 때만 쓰고, 쓴 값은 보고에 적는다.
- 크기가 다르면 다른 것으로 본다.

출력(한 줄):
    identical: <폭>x<높이>
    different: <다른 픽셀 수> of <전체> pixels (<비율>%), bbox <x0>,<y0>-<x1>,<y1>, max channel delta <D>
    different: size <폭>x<높이> vs <폭>x<높이>

종료 코드: 0 = 같다, 1 = 다르다, 2 = 비교하지 못했다(파일 없음, PNG 아님, 지원하지 않는 형식)
지원: 인터레이스 없는 PNG, 색 형식 0·2·3·4·6, 비트 깊이 1·2·4·8·16.
"""

import argparse
import struct
import sys
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class Unsupported(Exception):
    pass


def read_chunks(data):
    if data[:8] != SIGNATURE:
        raise Unsupported("PNG 파일이 아니다")
    pos = 8
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if len(body) != length:
            raise Unsupported("PNG가 중간에 끊겼다")
        yield kind, body
        pos += 12 + length


def unfilter(raw, height, stride, bpp):
    """PNG 필터를 풀어 줄마다 bytes로 돌려준다."""
    rows = []
    prev = bytes(stride)
    pos = 0
    for _ in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        if len(line) != stride:
            raise Unsupported("PNG 데이터가 모자란다")
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
        elif kind != 0:
            raise Unsupported("알 수 없는 PNG 필터 %d" % kind)
        prev = bytes(line)
        rows.append(prev)
    return rows


def samples(row, width, channels, depth):
    """한 줄을 채널 값(0~255)의 목록으로 만든다."""
    count = width * channels
    if depth == 8:
        return list(row[:count])
    if depth == 16:
        return [row[i * 2] for i in range(count)]
    out = []
    mask = (1 << depth) - 1
    for byte in row:
        for shift in range(8 - depth, -1, -depth):
            out.append((byte >> shift) & mask)
            if len(out) == count:
                return out
    return out


def decode(path):
    """(폭, 높이, [줄마다 RGBA bytes])를 돌려준다."""
    with open(path, "rb") as handle:
        data = handle.read()
    header = None
    palette = None
    transparency = None
    idat = []
    for kind, body in read_chunks(data):
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = body
        elif kind == b"tRNS":
            transparency = body
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
    if header is None or not idat:
        raise Unsupported("PNG에 IHDR나 IDAT가 없다")
    width, height, depth, color, _compression, _filter, interlace = header
    if interlace != 0:
        raise Unsupported("인터레이스 PNG는 지원하지 않는다")
    if color not in CHANNELS or depth not in (1, 2, 4, 8, 16):
        raise Unsupported("지원하지 않는 PNG 형식(color %d, depth %d)" % (color, depth))
    channels = CHANNELS[color]
    bits = channels * depth
    stride = (width * bits + 7) // 8
    bpp = max(1, bits // 8)
    rows = unfilter(zlib.decompress(b"".join(idat)), height, stride, bpp)
    scale = 255 // ((1 << depth) - 1) if depth < 8 else 1
    out = []
    for row in rows:
        values = samples(row, width, channels, depth)
        rgba = bytearray(width * 4)
        for x in range(width):
            base = x * channels
            if color == 3:
                index = values[base]
                if palette is None or index * 3 + 2 >= len(palette):
                    raise Unsupported("팔레트에 없는 색 번호")
                r, g, b = palette[index * 3:index * 3 + 3]
                a = transparency[index] if transparency and index < len(transparency) else 255
            elif color == 0:
                r = g = b = values[base] * scale
                a = 255
            elif color == 4:
                r = g = b = values[base]
                a = values[base + 1]
            elif color == 2:
                r, g, b = values[base], values[base + 1], values[base + 2]
                a = 255
            else:
                r, g, b, a = values[base:base + 4]
            rgba[x * 4:x * 4 + 4] = bytes((r, g, b, a))
        out.append(bytes(rgba))
    return width, height, out


def compare(first, second, tolerance=0):
    """(같은가, 설명)을 돌려준다."""
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
            delta = max(abs(row_a[base + k] - row_b[base + k]) for k in range(4))
            max_delta = max(max_delta, delta)
            if delta <= tolerance:
                continue
            differing += 1
            x0 = x if x0 is None else min(x0, x)
            y0 = y if y0 is None else y0
            x1 = max(x1, x)
            y1 = y
    if differing == 0:
        note = "" if max_delta == 0 else " (max channel delta %d within tolerance %d)" % (max_delta, tolerance)
        return True, "identical: %dx%d%s" % (width_a, height_a, note)
    total = width_a * height_a
    return False, "different: %d of %d pixels (%.3f%%), bbox %d,%d-%d,%d, max channel delta %d" % (
        differing, total, differing * 100.0 / total, x0, y0, x1, y1, max_delta)


def main(argv=None):
    parser = argparse.ArgumentParser(description="PNG 두 장을 픽셀 단위로 비교한다.")
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--tolerance", type=int, default=0)
    args = parser.parse_args(argv)
    if not 0 <= args.tolerance <= 255:
        print("cannot compare: --tolerance는 0~255다", file=sys.stderr)
        return 2
    try:
        same, text = compare(decode(args.baseline), decode(args.candidate), args.tolerance)
    except (OSError, Unsupported, zlib.error, struct.error) as error:
        print("cannot compare: %s" % error, file=sys.stderr)
        return 2
    print(text)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
