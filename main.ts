// THE WORLD TODAY — Sunday 22 November 2026 edition.
// Entry program for make.fun's news-image-20261122 competition.
//
// The repository ships the finished front page as entry.png (drawn by
// build_image.py from the wire reports listed in SOURCES.md). This
// program validates the file against the competition's gate limits and
// copies it to the output directory, byte for byte, on every run.

import { copyFileSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const MAX_BYTES = 1_048_576; // the gate's 1 MiB cap
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const JPEG_SIGNATURE = [0xff, 0xd8, 0xff];

function fail(message: string): never {
  console.error(`entry: ${message}`);
  process.exit(1);
}

function looksLikeImage(bytes: Buffer): boolean {
  const has = (sig: number[]) => sig.every((b, i) => bytes[i] === b);
  return has(PNG_SIGNATURE) || has(JPEG_SIGNATURE);
}

const botDir = process.env.MAKEFUN_BOT_DIR ?? ".";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(botDir, "entry.png");
const target = join(outDir, "entry.png");

const bytes = readFileSync(source);
if (bytes.length === 0) fail("entry.png is empty");
if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the 1 MiB gate limit`);
}
if (!looksLikeImage(bytes)) fail("entry.png is neither a PNG nor a JPEG");

// The gate also caps the canvas at 1024x1024. A PNG carries its size in
// the IHDR chunk: width and height are big-endian uint32s at bytes 16-24.
if (PNG_SIGNATURE.every((b, i) => bytes[i] === b)) {
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width > 1024 || height > 1024) {
    fail(`entry.png is ${width}x${height}, over the 1024x1024 gate limit`);
  }
  console.log(`entry: canvas ${width}x${height}, ${bytes.length} bytes`);
}

copyFileSync(source, target);
const written = statSync(target);
if (written.size !== bytes.length) fail("copy to /output changed the file size");
console.log(`entry: wrote ${written.size} bytes to ${target}`);
