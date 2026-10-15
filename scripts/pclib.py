"""Small helpers shared by the scripts: talk to `photocraft-cli serve`, read and write PNGs.

Standard library only.
"""
import json
import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


class PhotoCraftError(RuntimeError):
    pass


def find_cli(explicit=None):
    """Locate photocraft-cli: --cli, $PHOTOCRAFT_CLI, PATH, or a sibling checkout."""
    candidates = [explicit, os.environ.get("PHOTOCRAFT_CLI"), shutil.which("photocraft-cli")]
    candidates.append(str(HERE.parent.parent / "photocraft/target/release/photocraft-cli"))
    for c in candidates:
        if c and Path(c).is_file() and os.access(c, os.X_OK):
            return c
    raise PhotoCraftError(
        "photocraft-cli not found. Build github.com/storytold/photocraft "
        "(cargo build --release) and set PHOTOCRAFT_CLI or put it on PATH.")


class Session:
    """One headless PhotoCraft session over JSON lines on stdio."""

    def __init__(self, cli=None, root=None):
        """root: the one directory PhotoCraft may read and write (all paths must be inside)."""
        args = [find_cli(cli), "serve"]
        if root:
            args += ["--automation-read-root", str(root), "--automation-write-root", str(root)]
        self._log = tempfile.TemporaryFile(mode="w+")  # a file, so a chatty stderr cannot block
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=self._log, text=True, bufsize=1)
        self._id = 0

    def call(self, method, params=None):
        self._id += 1
        line = json.dumps({"id": self._id, "method": method, "params": params or {}})
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        reply = self.proc.stdout.readline()
        if not reply:
            self._log.seek(0)
            raise PhotoCraftError("photocraft-cli serve exited: " + self._log.read()[-500:])
        msg = json.loads(reply)
        if not msg.get("ok"):
            raise PhotoCraftError(msg.get("error", "unknown error"))
        return msg.get("result")

    def run(self, command, params=None):
        return self.call("engine.execute", {"command": command, "params": params or {}})

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self._log.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def common_root(*paths):
    """Smallest directory containing every given file or directory path."""
    dirs = [str(Path(p).resolve() if Path(p).is_dir() else Path(p).resolve().parent) for p in paths]
    root = Path(os.path.commonpath(dirs))
    if len(root.parts) <= 1:  # never hand PhotoCraft the whole filesystem
        raise PhotoCraftError(f"files are spread too widely (common folder {root}); "
                              "keep inputs and outputs under one project folder")
    return root


def walk_layers(layers, depth=0):
    """Yield (depth, layer) for a doc.inspect layer list, children included."""
    for layer in layers:
        yield depth, layer
        yield from walk_layers(layer.get("children") or [], depth + 1)


def background_layer(doc):
    """Bottom-most pixel layer: the Background in a fresh or opened flat document."""
    pixel = [l for _, l in walk_layers(doc["layers"]) if l.get("kind") == "Pixel"]
    if not pixel:
        raise PhotoCraftError("document has no pixel layer")
    named = [l for l in pixel if l.get("name") == "Background"]
    return (named or pixel)[0]["id"]


# PNG ---------------------------------------------------------------------------

def write_png(path, width, height, pixels):
    """pixels: flat list of (r, g, b) tuples, 0..255, row-major."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for r, g, b in pixels[y * width:(y + 1) * width]:
            raw += bytes((r, g, b))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                           + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def read_png(path):
    """Decode an 8-bit RGB/RGBA/grey PNG. Returns (width, height, [(r, g, b, a), ...])."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    pos, idat = 8, b""
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    if bit_depth != 8 or interlace:
        raise ValueError("only 8-bit, non-interlaced PNGs are supported")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * channels
    raw = zlib.decompress(idat)
    rows, prev = [], bytearray(stride)
    for y in range(height):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 255
        rows.append(line)
        prev = line
    px = []
    for line in rows:
        for x in range(width):
            v = line[x * channels:(x + 1) * channels]
            if channels == 1:
                px.append((v[0], v[0], v[0], 255))
            elif channels == 2:
                px.append((v[0], v[0], v[0], v[1]))
            elif channels == 3:
                px.append((v[0], v[1], v[2], 255))
            else:
                px.append(tuple(v))
    return width, height, px
