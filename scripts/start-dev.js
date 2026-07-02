import { mkdirSync, openSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const logsDir = join(root, "logs");
mkdirSync(logsDir, { recursive: true });

function launch(name, command, args, options) {
  const out = openSync(join(logsDir, `${name}.log`), "a");
  const err = openSync(join(logsDir, `${name}.err.log`), "a");
  const child = spawn(command, args, {
    ...options,
    detached: true,
    stdio: ["ignore", out, err],
    windowsHide: true,
  });
  child.unref();
  return child.pid;
}

const backendPid = launch(
  "backend",
  join(root, "backend", ".venv-win", "Scripts", "python.exe"),
  ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
  {
    cwd: join(root, "backend"),
    env: { ...process.env, PYTHONPATH: join(root, "backend") },
  },
);

const frontendPid = launch(
  "frontend",
  process.execPath,
  [join(root, "frontend", "node_modules", "vite", "bin", "vite.js"), "--host", "127.0.0.1", "--port", "5173"],
  {
    cwd: join(root, "frontend"),
    env: process.env,
  },
);

writeFileSync(
  join(logsDir, "dev-pids.json"),
  `${JSON.stringify({ backendPid, frontendPid }, null, 2)}\n`,
);

console.log(`backend_pid=${backendPid} frontend_pid=${frontendPid}`);
