// Entry program for the gta6-meme-x-01 bounty.
//
// The meme itself lives on X; this program's only job is to hand the
// grader the address of that post. It reads POST.json out of the bot
// directory and leaves an identical copy in the output directory,
// where the gate picks it up.
//
// Two environment variables choose the directories:
//   MAKEFUN_BOT_DIR     — where POST.json lives (default: /bot)
//   MAKEFUN_OUTPUT_DIR  — where the copy goes (default: /output)
// No network, no clock, and no paths outside those two directories,
// so two runs always produce the same bytes. On success it prints
// nothing; on any failure it reports the problem and exits non-zero.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const POST_FILE = 'POST.json';

function fail(message: string): never {
  console.error(`gta6-meme-x-01: ${message}`);
  process.exit(1);
}

try {
  mkdirSync(outputDir, { recursive: true });
} catch (err) {
  fail(`could not create output directory ${outputDir}: ${(err as Error).message}`);
}

try {
  copyFileSync(join(botDir, POST_FILE), join(outputDir, POST_FILE));
} catch (err) {
  fail(`could not copy ${POST_FILE} from ${botDir} to ${outputDir}: ${(err as Error).message}`);
}
