import { readFileSync } from "node:fs";
import { toTraditional } from "./localize.mjs";
process.stdout.write(toTraditional(readFileSync(0, "utf8")));
