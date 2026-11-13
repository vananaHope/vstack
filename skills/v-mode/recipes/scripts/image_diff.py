"""PNG 두 장이 픽셀 단위로 같은지 본다. 표준 라이브러리만 쓴다.

사용법:
    python -I image_diff.py <기준.png> <새.png>

- 같은 위치의 픽셀을 RGBA로 비교한다. 채널 값이 하나라도 다르면 다른 것이다. 허용 오차는 없다.
- 크기가 다르면 다른 것으로 본다.
- 파일의 바이트가 달라도(압축, 필터, 부가 정보) 픽셀이 같으면 같은 것이다.

출력(한 줄, 표준 출력):
    identical: <폭>x<높이>
    different: <다른 픽셀 수> of <전체> pixels (<비율>%), bbox <x0>,<y0>-<x1>,<y1>, max channel delta <D>
    different: size <폭>x<높이> vs <폭>x<높이>
비교하지 못하면 표준 오류에 `cannot compare: <이유>`를 낸다. 출력은 모두 ASCII다
(Windows에서 파이프로 받아도 깨지지 않게).

종료 코드: 0 = 같다, 1 = 다르다, 2 = 비교하지 못했다
비교하지 못하는 경우: 파일 없음, PNG 아님, 인터레이스 PNG, 16비트 PNG, 모르는 필수 청크가 있는 PNG,
깨졌거나 끊긴 PNG. 깨진 것으로 보는 것: CRC 불일치, 청크 순서나 개수가 규격과 다름(IHDR가 맨 앞에 하나,
IDAT는 서로 붙어 있음, PLTE·tRNS는 IDAT 앞), IEND가 없거나 본문이 있거나 뒤에 바이트가 남음,
PLTE·tRNS 길이가 색 형식과 맞지 않음, 압축 데이터가 덜 끝났거나 뒤에 남는 바이트가 있음, 데이터 길이 불일치.
규격의 모든 조항을 검사하는 것은 아니다. 지원: 인터레이스 없는 PNG, 색 형식 0·2·3·4·6, 비트 깊이 1·2·4·8
(tRNS 투명도 포함). 화면 스크린샷은 보통 8비트 RGB나 RGBA다.
"""

import argparse
import struct
import sys
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
DEPTHS = {0: (1, 2, 4, 8), 2: (8,), 3: (1, 2, 4, 8), 4: (8,), 6: (8,)}


class Unsupported(Exception):
    pass


def read_chunks(data):
    """청크를 차례로 내준다. 끊겼거나, CRC가 틀리거나, 구조가 PNG 규격과 다르면 Unsupported.

    보는 것: IHDR가 맨 앞에 하나, IDAT는 서로 붙어 있음, PLTE는 IDAT 앞에 하나, IEND는 본문 없이 파일의 끝,
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


def unfilter(raw, height, stride, bpp):
    """PNG 필터를 풀어 줄마다 bytes로 돌려준다."""
    if len(raw) != height * (stride + 1):
        raise Unsupported("corrupt PNG (image data is %d bytes, expected %d)" % (len(raw), height * (stride + 1)))
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
        elif kind != 0:
            raise Unsupported("corrupt PNG (unknown filter type %d)" % kind)
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
    width, height, depth, color, _compression, _filter, interlace = header
    if width == 0 or height == 0:
        raise Unsupported("corrupt PNG (zero size)")
    if interlace != 0:
        raise Unsupported("interlaced PNG is not supported")
    if depth == 16:
        raise Unsupported("16-bit PNG is not supported")
    if color not in CHANNELS or depth not in DEPTHS[color]:
        raise Unsupported("unsupported PNG format (color type %d, bit depth %d)" % (color, depth))
    channels = CHANNELS[color]
    bits = channels * depth
    stride = (width * bits + 7) // 8
    bpp = max(1, bits // 8)
    if palette is not None and (len(palette) % 3 != 0 or not 3 <= len(palette) <= 768):
        raise Unsupported("corrupt PNG (PLTE length)")
    if color == 3 and palette is None:
        raise Unsupported("corrupt PNG (palette image without PLTE)")
    rows = unfilter(inflate(b"".join(idat)), height, stride, bpp)
    scale = 255 // ((1 << depth) - 1)
    # tRNS: 색 형식 0은 투명한 회색 값 하나, 2는 투명한 RGB 값 하나(둘 다 16비트로 적힌다), 3은 팔레트 번호별 알파
    key = None
    if transparency is not None:
        if color == 0:
            if len(transparency) != 2:
                raise Unsupported("corrupt PNG (tRNS length)")
            key = struct.unpack(">H", transparency)[0]
        elif color == 2:
            if len(transparency) != 6:
                raise Unsupported("corrupt PNG (tRNS length)")
            key = struct.unpack(">HHH", transparency)
        elif color == 3:
            if len(transparency) > len(palette) // 3:
                raise Unsupported("corrupt PNG (tRNS longer than the palette)")
        else:
            raise Unsupported("corrupt PNG (tRNS in an image that has an alpha channel)")
    out = []
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
            elif color == 2:
                r, g, b = values[base], values[base + 1], values[base + 2]
                a = 0 if (r, g, b) == key else 255
            else:
                r, g, b, a = values[base:base + 4]
            rgba[x * 4:x * 4 + 4] = bytes((r, g, b, a))
        out.append(bytes(rgba))
    return width, height, out


def compare(first, second):
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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two PNG files pixel by pixel.")
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    args = parser.parse_args(argv)
    images = []
    for label, path in (("baseline", args.baseline), ("candidate", args.candidate)):
        try:
            images.append(decode(path))
        except OSError as error:
            print("cannot compare: cannot read the %s file (%s)" % (label, type(error).__name__), file=sys.stderr)
            return 2
        except (Unsupported, zlib.error, struct.error) as error:
            reason = str(error).encode("ascii", "replace").decode("ascii")
            print("cannot compare: %s file: %s" % (label, reason), file=sys.stderr)
            return 2
    same, text = compare(*images)
    print(text)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
