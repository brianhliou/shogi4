#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, "index.html"), "utf8");
const start = html.indexOf("// ---- geometry ----");
const end = html.indexOf("// ---- SVG pieces");

if (start < 0 || end < 0 || end <= start) {
  throw new Error("could not locate static engine block in index.html");
}

const engineSource = html.slice(start, end);
const ctx = {};
vm.createContext(ctx);
vm.runInContext(`${engineSource}\nthis.__api = api;\nthis.__roundTrip = enc => encodePos(parsePos(enc));`, ctx);

function goldenMove(move) {
  if (move.kind === "m") {
    return `${move.from.c}${move.from.r}${move.to.c}${move.to.r}`;
  }
  return `${move.piece}@${move.to.c}${move.to.r}`;
}

const goldenPath = path.join(here, "..", "engine", "golden.txt");
const lines = fs.readFileSync(goldenPath, "utf8").trim().split(/\n+/);
let rtFail = 0;
let mvFail = 0;

for (const line of lines) {
  const [enc, want] = line.split(" ");
  const roundTripped = ctx.__roundTrip(enc);
  if (roundTripped !== enc) {
    rtFail += 1;
    if (rtFail <= 3) console.log(`  round-trip drift: ${enc} -> ${roundTripped}`);
  }

  const got = ctx.__api(enc).moves.map(goldenMove).sort().join(",");
  if (got !== want) {
    mvFail += 1;
    if (mvFail <= 3) {
      console.log(`  move-set drift @ ${enc}\n    want ${want}\n    got  ${got}`);
    }
  }
}

const n = lines.length;
console.log(`checked ${n} golden positions: round-trip ${n - rtFail}/${n} ok, move-set ${n - mvFail}/${n} ok`);
if (rtFail || mvFail) {
  console.log("FAIL");
  process.exit(1);
}
console.log("OK - static engine agrees with the oracle on every golden position");
