const outputDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outputDir) throw new Error("MAKEFUN_OUTPUT_DIR is not set");

const source = new URL("./entry.png", import.meta.url);
const destination = new URL("entry.png", `file://${outputDir.replace(/\/$/, "")}/`);
await Bun.write(destination, Bun.file(source));
