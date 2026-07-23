#!/usr/bin/env python3
"""Batch-generate images in Google Flow from image-prompts-only.txt (no GLabs extension)."""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SCENE_PREFIX_RE = re.compile(r"^Scene\s+(\d+)\.", re.IGNORECASE)
RECAPTCHA_SITE_KEY = "6LdsFiUsAAAAAIjVDZcuLhaHiDn5nnHVXVRQGeMV"
FLOW_PROJECT_RE = re.compile(r"/project/([a-f0-9-]+)")

GENERATE_JS = """
async ({ prompt, model, aspectRatio, recaptchaKey }) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const waitForRecaptcha = async (timeoutMs = 45000) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (typeof grecaptcha !== "undefined" && grecaptcha?.enterprise?.execute) {
        return true;
      }
      await sleep(500);
    }
    return false;
  };

  const getAuthToken = async () => {
    const resp = await fetch("/fx/api/auth/session", { credentials: "include" });
    if (!resp.ok) {
      throw new Error("Auth session HTTP " + resp.status);
    }
    const data = await resp.json();
    if (!data?.access_token) {
      throw new Error("No access_token in Flow session — log into labs.google");
    }
    return data.access_token;
  };

  const getProjectId = () => {
    const m = window.location.href.match(/project\\/([a-f0-9-]+)/);
    return m ? m[1] : null;
  };

  const uuid = () =>
    "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });

  if (!(await waitForRecaptcha())) {
    return { ok: false, error: "reCAPTCHA not ready — refresh the Flow project page" };
  }

  const projectId = getProjectId();
  if (!projectId) {
    return {
      ok: false,
      error: "No Flow project in URL — open https://labs.google/fx/tools/flow/project/<id>",
    };
  }

  let authToken;
  try {
    authToken = await getAuthToken();
  } catch (err) {
    return { ok: false, error: String(err.message || err) };
  }

  let recaptchaToken;
  try {
    recaptchaToken = await grecaptcha.enterprise.execute(recaptchaKey, {
      action: "IMAGE_GENERATION",
    });
  } catch (err) {
    return { ok: false, error: "reCAPTCHA execute failed: " + String(err.message || err) };
  }

  if (!recaptchaToken) {
    return { ok: false, error: "Empty reCAPTCHA token" };
  }

  const batchId = uuid();
  const sessionId = ";" + Date.now() + "0";
  const url =
    "https://aisandbox-pa.googleapis.com/v1/projects/" +
    projectId +
    "/flowMedia:batchGenerateImages";

  const body = {
    clientContext: {
      recaptchaContext: {
        applicationType: "RECAPTCHA_APPLICATION_TYPE_WEB",
        token: recaptchaToken,
      },
      projectId,
      tool: "PINHOLE",
      sessionId,
    },
    mediaGenerationContext: { batchId },
    useNewMedia: true,
    requests: [
      {
        clientContext: {
          recaptchaContext: {
            applicationType: "RECAPTCHA_APPLICATION_TYPE_WEB",
            token: recaptchaToken,
          },
          projectId,
          tool: "PINHOLE",
          sessionId,
        },
        imageAspectRatio: aspectRatio,
        imageInputs: [],
        imageModelName: model,
        seed: Math.floor(Math.random() * 300000),
        structuredPrompt: { parts: [{ text: prompt }] },
      },
    ],
  };

  let resp;
  try {
    resp = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "text/plain;charset=UTF-8",
        Authorization: "Bearer " + authToken,
      },
      body: JSON.stringify(body),
    });
  } catch (err) {
    return { ok: false, error: "Network error: " + String(err.message || err) };
  }

  const raw = await resp.text();
  if (!resp.ok) {
    return {
      ok: false,
      error: "Generate HTTP " + resp.status + ": " + raw.slice(0, 400),
    };
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    return { ok: false, error: "Invalid JSON response: " + raw.slice(0, 200) };
  }

  let mediaId = null;
  let fifeUrl = null;

  if (Array.isArray(data?.workflows)) {
    for (const wf of data.workflows) {
      const id = wf?.metadata?.primaryMediaId;
      if (id) {
        mediaId = id;
        break;
      }
    }
  }
  if (!mediaId && Array.isArray(data?.media)) {
    for (const item of data.media) {
      const id = item?.name || item?.mediaId;
      if (id) {
        mediaId = id;
        break;
      }
    }
  }
  if (Array.isArray(data?.media)) {
    for (const item of data.media) {
      const url = item?.image?.generatedImage?.fifeUrl;
      if (url) {
        fifeUrl = url;
        break;
      }
    }
  }

  if (!mediaId && !fifeUrl) {
    return { ok: false, error: "No mediaId in response", raw: raw.slice(0, 500) };
  }

  return { ok: true, mediaId, fifeUrl, projectId };
}
"""

DOWNLOAD_JS = """
async ({ mediaId, fifeUrl }) => {
  const toBase64 = async (imageUrl) => {
    const resp = await fetch(imageUrl, { credentials: "include" });
    if (!resp.ok) {
      throw new Error("Download HTTP " + resp.status);
    }
    const blob = await resp.blob();
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  };

  try {
    if (fifeUrl) {
      return { ok: true, base64: await toBase64(fifeUrl), source: "fifeUrl" };
    }
    if (mediaId) {
      const redirect =
        "https://labs.google/fx/api/trpc/media.getMediaUrlRedirect?name=" +
        encodeURIComponent(mediaId);
      return { ok: true, base64: await toBase64(redirect), source: "redirect" };
    }
    return { ok: false, error: "No mediaId or fifeUrl" };
  } catch (err) {
    return { ok: false, error: String(err.message || err) };
  }
}
"""


def build_one_shot_js(*, prompt_b64: str, model: str, aspect_ratio: str) -> str:
    return f"""
(async function() {{
  const prompt = atob({json.dumps(prompt_b64)});
  const model = {json.dumps(model)};
  const aspectRatio = {json.dumps(aspect_ratio)};
  const recaptchaKey = {json.dumps(RECAPTCHA_SITE_KEY)};

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const waitForRecaptcha = async (timeoutMs = 45000) => {{
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {{
      if (typeof grecaptcha !== "undefined" && grecaptcha?.enterprise?.execute) return true;
      await sleep(500);
    }}
    return false;
  }};

  try {{
    if (!(await waitForRecaptcha())) {{
      return JSON.stringify({{ ok: false, error: "reCAPTCHA not ready — refresh the Flow project page" }});
    }}

    const projectMatch = window.location.href.match(/project\\/([a-f0-9-]+)/);
    if (!projectMatch) {{
      return JSON.stringify({{
        ok: false,
        error: "No Flow project in URL — open https://labs.google/fx/tools/flow/project/<id>",
      }});
    }}
    const projectId = projectMatch[1];

    const sessionResp = await fetch("/fx/api/auth/session", {{ credentials: "include" }});
    if (!sessionResp.ok) {{
      return JSON.stringify({{ ok: false, error: "Auth session HTTP " + sessionResp.status }});
    }}
    const sessionData = await sessionResp.json();
    const authToken = sessionData?.access_token;
    if (!authToken) {{
      return JSON.stringify({{ ok: false, error: "Not logged into labs.google in this Chrome tab" }});
    }}

    const recaptchaToken = await grecaptcha.enterprise.execute(recaptchaKey, {{
      action: "IMAGE_GENERATION",
    }});
    if (!recaptchaToken) {{
      return JSON.stringify({{ ok: false, error: "Empty reCAPTCHA token" }});
    }}

    const uuid = () =>
      "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {{
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }});

    const batchId = uuid();
    const sessionId = ";" + Date.now() + "0";
    const genUrl =
      "https://aisandbox-pa.googleapis.com/v1/projects/" +
      projectId +
      "/flowMedia:batchGenerateImages";

    const body = {{
      clientContext: {{
        recaptchaContext: {{
          applicationType: "RECAPTCHA_APPLICATION_TYPE_WEB",
          token: recaptchaToken,
        }},
        projectId,
        tool: "PINHOLE",
        sessionId,
      }},
      mediaGenerationContext: {{ batchId }},
      useNewMedia: true,
      requests: [
        {{
          clientContext: {{
            recaptchaContext: {{
              applicationType: "RECAPTCHA_APPLICATION_TYPE_WEB",
              token: recaptchaToken,
            }},
            projectId,
            tool: "PINHOLE",
            sessionId,
          }},
          imageAspectRatio: aspectRatio,
          imageInputs: [],
          imageModelName: model,
          seed: Math.floor(Math.random() * 300000),
          structuredPrompt: {{ parts: [{{ text: prompt }}] }},
        }},
      ],
    }};

    const genResp = await fetch(genUrl, {{
      method: "POST",
      headers: {{
        "Content-Type": "text/plain;charset=UTF-8",
        Authorization: "Bearer " + authToken,
      }},
      body: JSON.stringify(body),
    }});
    const genRaw = await genResp.text();
    if (!genResp.ok) {{
      return JSON.stringify({{
        ok: false,
        error: "Generate HTTP " + genResp.status + ": " + genRaw.slice(0, 400),
      }});
    }}

    let data;
    try {{
      data = JSON.parse(genRaw);
    }} catch {{
      return JSON.stringify({{ ok: false, error: "Invalid JSON from generate API" }});
    }}

    let mediaId = null;
    let fifeUrl = null;
    if (Array.isArray(data?.workflows)) {{
      for (const wf of data.workflows) {{
        const id = wf?.metadata?.primaryMediaId;
        if (id) {{ mediaId = id; break; }}
      }}
    }}
    if (!mediaId && Array.isArray(data?.media)) {{
      for (const item of data.media) {{
        const id = item?.name || item?.mediaId;
        if (id) {{ mediaId = id; break; }}
      }}
    }}
    if (Array.isArray(data?.media)) {{
      for (const item of data.media) {{
        const url = item?.image?.generatedImage?.fifeUrl;
        if (url) {{ fifeUrl = url; break; }}
      }}
    }}
    if (!mediaId && !fifeUrl) {{
      return JSON.stringify({{ ok: false, error: "No mediaId in generate response" }});
    }}

    const toBase64 = async (imageUrl) => {{
      const resp = await fetch(imageUrl, {{ credentials: "include" }});
      if (!resp.ok) throw new Error("Download HTTP " + resp.status);
      const blob = await resp.blob();
      const buffer = await blob.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = "";
      const chunk = 0x8000;
      for (let i = 0; i < bytes.length; i += chunk) {{
        binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
      }}
      return btoa(binary);
    }};

    let source = "fifeUrl";
    let b64;
    if (fifeUrl) {{
      b64 = await toBase64(fifeUrl);
    }} else {{
      source = "redirect";
      const redirect =
        "https://labs.google/fx/api/trpc/media.getMediaUrlRedirect?name=" +
        encodeURIComponent(mediaId);
      b64 = await toBase64(redirect);
    }}

    return JSON.stringify({{
      ok: true,
      mediaId,
      fifeUrl,
      source,
      base64: b64,
    }});
  }} catch (err) {{
    return JSON.stringify({{ ok: false, error: String(err.message || err) }});
  }}
}})()
"""


def run_applescript(script: str) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if "-1723" in err or "Access not allowed" in err:
            raise RuntimeError(
                "Chrome blocked JavaScript from Apple Events. In your open Chrome window: "
                "View → Developer → Allow JavaScript from Apple Events (enable it once), then re-run."
            )
        raise RuntimeError(err or "AppleScript failed")
    return proc.stdout.strip()


def find_open_flow_project_url() -> str | None:
    script = """
tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      set u to URL of t
      if u contains "labs.google" and u contains "flow/project/" then
        return u
      end if
    end repeat
  end repeat
end tell
return ""
"""
    url = run_applescript(script)
    return url or None


def list_flow_related_tabs() -> dict[str, list[str]]:
    script = """
tell application "Google Chrome"
  set homeUrls to {}
  set projectUrls to {}
  set otherUrls to {}
  repeat with w in windows
    repeat with t in tabs of w
      set u to URL of t
      if u contains "labs.google" then
        if u contains "flow/project/" then
          set end of projectUrls to u
        else if u contains "tools/flow" then
          set end of homeUrls to u
        else
          set end of otherUrls to u
        end if
      end if
    end repeat
  end repeat
  return (length of projectUrls) & "|" & (length of homeUrls) & "|" & (length of otherUrls)
end tell
"""
    raw = run_applescript(script)
    parts = raw.split("|")
    counts = [int(p) if p.isdigit() else 0 for p in parts[:3]]
    return {"projects": counts[0], "home": counts[1], "other_labs": counts[2]}


def check_chrome_js_permission() -> None:
    """Fail fast if Chrome blocks execute javascript from Apple Events."""
    script = """
tell application "Google Chrome"
  if (count of windows) = 0 then
    return "NO_CHROME"
  end if
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "flow/project/" then
        try
          execute javascript "1" in t
          return "OK"
        on error errMsg number errNum
          return "BLOCKED:" & errNum
        end try
      end if
    end repeat
  end repeat
  tell active tab of front window
    try
      execute javascript "1"
      return "OK_ANY_TAB"
    on error errMsg number errNum
      return "BLOCKED:" & errNum
    end try
  end tell
end tell
"""
    status = run_applescript(script)
    if status.startswith("BLOCKED:") or status == "NO_CHROME":
        raise RuntimeError(
            "Chrome blocked JavaScript from Apple Events.\n"
            "  Fix: Chrome menu → View → Developer → Allow JavaScript from Apple Events\n"
            "  Enable it, then re-run this command."
        )


def describe_flow_tab_state() -> str:
    tabs = list_flow_related_tabs()
    if tabs["projects"]:
        return f"{tabs['projects']} Flow project tab(s) open"
    if tabs["home"]:
        return (
            f"Flow home open ({tabs['home']} tab(s)) but no project yet — "
            "click an existing project or create one (URL must contain /flow/project/)"
        )
    if tabs["other_labs"]:
        return (
            f"labs.google open ({tabs['other_labs']} tab(s)) but not Flow — "
            "finish sign-in, then open https://labs.google/fx/tools/flow/ and a project"
        )
    return "no labs.google tabs open — open https://labs.google/fx/tools/flow/ in Chrome"


def open_flow_tab_in_chrome(flow_url: str | None = None) -> None:
    target = flow_url or "https://labs.google/fx/tools/flow/"
    script = f"""
tell application "Google Chrome"
  activate
  if (count of windows) = 0 then
    make new window
  end if
  tell front window
    make new tab with properties {{URL:{json.dumps(target)}}}
  end tell
end tell
"""
    run_applescript(script)


def run_js_in_open_flow_tab(js: str) -> str:
    script = f"""
tell application "Google Chrome"
  activate
  repeat with w in windows
    repeat with t in tabs of w
      set u to URL of t
      if u contains "labs.google" and u contains "flow/project/" then
        set active tab index of w to (index of t)
        set index of w to 1
        return execute javascript {json.dumps(js)} in t
      end if
    end repeat
  end repeat
  error "No Flow project tab open in Chrome"
end tell
"""
    return run_applescript(script)


def wait_for_open_flow_project(wait_seconds: int, flow_url: str | None) -> str:
    check_chrome_js_permission()

    deadline = time.time() + max(0, wait_seconds)
    last_hint = ""
    while True:
        url = find_open_flow_project_url()
        if url:
            check_chrome_js_permission()
            return url
        if time.time() >= deadline:
            break
        remaining = int(deadline - time.time())
        hint = describe_flow_tab_state()
        if remaining % 15 == 0 and remaining > 0:
            if hint != last_hint:
                log(f"Chrome status: {hint}")
                last_hint = hint
            log(
                f"Waiting for Flow project tab ({remaining}s left) — "
                "open a project so the URL contains /flow/project/"
            )
        time.sleep(1)

    log("No Flow project tab found — opening Flow in your current Chrome window")
    open_flow_tab_in_chrome(flow_url)
    extra = max(30, min(wait_seconds, 120)) if wait_seconds else 60
    log(f"Waiting {extra}s for you to open a Flow project in that Chrome tab...")
    deadline = time.time() + extra
    while time.time() < deadline:
        url = find_open_flow_project_url()
        if url:
            return url
        time.sleep(1)

    raise RuntimeError(
        "No Flow project tab in your open Chrome. Open a project "
        "(URL must contain /flow/project/) and re-run with --wait-for-login 300"
    )


def generate_batch_open_chrome(
    *,
    prompts_file: Path,
    output_dir: Path,
    start: int,
    count: int,
    flow_url: str | None,
    model: str,
    aspect_ratio: str,
    delay_seconds: float,
    wait_for_login: int,
) -> int:
    all_prompts = parse_prompts(prompts_file)
    if not all_prompts:
        raise RuntimeError(f"No prompts found in {prompts_file}")

    start_idx = max(1, start) - 1
    batch = all_prompts[start_idx : start_idx + count]
    if not batch:
        raise RuntimeError(
            f"Nothing to generate: start={start}, count={count}, file has {len(all_prompts)} prompts"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    log(f"Prompt file: {prompts_file}")
    log(f"Using your already-open Chrome (AppleScript)")
    log(f"Generating {len(batch)} image(s) → {output_dir}")

    project_url = wait_for_open_flow_project(wait_for_login, flow_url)
    log(f"Found Flow project tab: {project_url}")

    saved = 0
    for i, (scene_num, prompt) in enumerate(batch, start=1):
        label = scene_num if scene_num is not None else (start_idx + i)
        out_name = f"scene_{label:03d}.png"
        out_path = output_dir / out_name

        if out_path.exists():
            log(f"[{i}/{len(batch)}] Skip existing {out_name}")
            saved += 1
            continue

        log(f"[{i}/{len(batch)}] Scene {label} — generating ({len(prompt)} chars)...")
        prompt_b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
        js = build_one_shot_js(
            prompt_b64=prompt_b64,
            model=model,
            aspect_ratio=aspect_ratio,
        )
        raw = run_js_in_open_flow_tab(js)
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Scene {label}: invalid JSON from Chrome: {raw[:200]}") from exc

        if not result.get("ok"):
            raise RuntimeError(f"Scene {label} failed: {result.get('error')}")

        out_path.write_bytes(base64.b64decode(result["base64"]))
        log(
            f"[{i}/{len(batch)}] Saved {out_path} "
            f"(mediaId={result.get('mediaId')}, {result.get('source')})"
        )
        saved += 1

        if i < len(batch) and delay_seconds > 0:
            log(f"Waiting {delay_seconds}s before next prompt...")
            time.sleep(delay_seconds)

    return saved


def log(msg: str) -> None:
    print(msg, flush=True)


def parse_prompts(path: Path) -> list[tuple[int | None, str]]:
    items: list[tuple[int | None, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        if text.endswith("||"):
            text = text[:-2].rstrip()
        scene_match = SCENE_PREFIX_RE.match(text)
        scene_num = int(scene_match.group(1)) if scene_match else None
        items.append((scene_num, text))
    return items


CREATE_PROJECT_JS = """
async () => {
  const title = new Date().toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).replace(",", "");
  try {
    const resp = await fetch("/fx/api/trpc/project.createProject", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ json: { projectTitle: title, toolName: "PINHOLE" } }),
    });
    if (!resp.ok) {
      return { ok: false, error: "createProject HTTP " + resp.status };
    }
    const data = await resp.json();
    const projectId =
      data?.result?.data?.json?.result?.projectId ||
      data?.result?.data?.json?.projectId ||
      null;
    if (!projectId) {
      return { ok: false, error: "No projectId returned" };
    }
    return {
      ok: true,
      projectId,
      url: "https://labs.google/fx/tools/flow/project/" + projectId,
    };
  } catch (err) {
    return { ok: false, error: String(err.message || err) };
  }
}
"""


def ensure_flow_project(page, flow_url: str | None, *, wait_seconds: int = 0):
    if FLOW_PROJECT_RE.search(page.url or ""):
        return page

    for pg in page.context.pages:
        if FLOW_PROJECT_RE.search(pg.url or ""):
            pg.bring_to_front()
            return pg

    deadline = time.time() + max(0, wait_seconds)
    while time.time() < deadline:
        for pg in page.context.pages:
            if FLOW_PROJECT_RE.search(pg.url or ""):
                pg.bring_to_front()
                return pg
        remaining = int(deadline - time.time())
        if remaining % 15 == 0 and remaining > 0:
            log(
                f"Waiting for Flow project tab ({remaining}s left) — "
                "log into labs.google and open a project in the automation Chrome window"
            )
        page.wait_for_timeout(1000)

    if not FLOW_PROJECT_RE.search(page.url or ""):
        target = flow_url or "https://labs.google/fx/tools/flow/"
        if "labs.google" not in (page.url or ""):
            page.goto(target, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(3000)

    log("No Flow project open — creating one...")
    created = page.evaluate(CREATE_PROJECT_JS)
    if not created.get("ok"):
        raise RuntimeError(
            "Could not create Flow project. Log into labs.google in the automation "
            f"Chrome window and open a project manually. ({created.get('error')})"
        )

    project_url = created["url"]
    log(f"Opening new project: {project_url}")
    page.goto(project_url, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(5000)
    return page


def pick_flow_page(context, flow_url: str | None, *, wait_seconds: int = 0):
    from playwright.sync_api import Page

    pages: list[Page] = []
    for pg in context.pages:
        url = pg.url or ""
        if "labs.google/fx" in url and "/tools/flow/" in url:
            pages.append(pg)

    if not pages:
        page = context.new_page()
        target = flow_url or "https://labs.google/fx/tools/flow/"
        log(f"Opening Flow: {target}")
        page.goto(target, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(4000)
        return ensure_flow_project(page, flow_url, wait_seconds=wait_seconds)

    for pg in pages:
        if FLOW_PROJECT_RE.search(pg.url or ""):
            pg.bring_to_front()
            return pg

    page = pages[0]
    page.bring_to_front()
    if not FLOW_PROJECT_RE.search(page.url or ""):
        log("Flow tab open but no project yet — waiting up to 30s for /project/ URL...")
        deadline = time.time() + 30
        while time.time() < deadline:
            if FLOW_PROJECT_RE.search(page.url or ""):
                break
            page.wait_for_timeout(1000)
    return ensure_flow_project(page, flow_url, wait_seconds=wait_seconds)


def connect_browser(*, cdp_url: str | None, chrome_user_data: Path, profile: str):
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    if cdp_url:
        log(f"Connecting to Chrome CDP: {cdp_url}")
        browser = pw.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        owns_context = False
    else:
        log("Launching Chrome with your profile (quit other Chrome windows first)")
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(chrome_user_data),
            channel="chrome",
            headless=False,
            args=[
                f"--profile-directory={profile}",
                "--disable-blink-features=AutomationControlled",
            ],
            viewport={"width": 1440, "height": 900},
        )
        browser = None
        owns_context = True
    return pw, browser, context, owns_context


def generate_batch(
    *,
    prompts_file: Path,
    output_dir: Path,
    start: int,
    count: int,
    cdp_url: str | None,
    flow_url: str | None,
    model: str,
    aspect_ratio: str,
    delay_seconds: float,
    wait_for_login: int,
    chrome_user_data: Path,
    profile: str,
) -> int:
    from playwright.sync_api import sync_playwright

    all_prompts = parse_prompts(prompts_file)
    if not all_prompts:
        raise RuntimeError(f"No prompts found in {prompts_file}")

    start_idx = max(1, start) - 1
    batch = all_prompts[start_idx : start_idx + count]
    if not batch:
        raise RuntimeError(
            f"Nothing to generate: start={start}, count={count}, file has {len(all_prompts)} prompts"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    log(f"Prompt file: {prompts_file}")
    log(f"Generating {len(batch)} image(s) → {output_dir}")

    pw, browser, context, owns_context = connect_browser(
        cdp_url=cdp_url,
        chrome_user_data=chrome_user_data,
        profile=profile,
    )

    saved = 0
    try:
        page = pick_flow_page(context, flow_url, wait_seconds=wait_for_login)
        page.wait_for_load_state("domcontentloaded", timeout=60_000)
        page.wait_for_timeout(2000)

        if not FLOW_PROJECT_RE.search(page.url or ""):
            raise RuntimeError(
                "Flow project not detected. Open a project at "
                "https://labs.google/fx/tools/flow/project/<id> and re-run."
            )

        log(f"Using Flow project tab: {page.url}")

        for i, (scene_num, prompt) in enumerate(batch, start=1):
            label = scene_num if scene_num is not None else (start_idx + i)
            out_name = f"scene_{label:03d}.png"
            out_path = output_dir / out_name

            if out_path.exists():
                log(f"[{i}/{len(batch)}] Skip existing {out_name}")
                saved += 1
                continue

            log(f"[{i}/{len(batch)}] Scene {label} — generating ({len(prompt)} chars)...")
            result = page.evaluate(
                GENERATE_JS,
                {
                    "prompt": prompt,
                    "model": model,
                    "aspectRatio": aspect_ratio,
                    "recaptchaKey": RECAPTCHA_SITE_KEY,
                },
            )

            if not result.get("ok"):
                raise RuntimeError(f"Scene {label} generation failed: {result.get('error')}")

            media_id = result.get("mediaId")
            fife_url = result.get("fifeUrl")
            log(f"[{i}/{len(batch)}] Generated mediaId={media_id}")

            dl = page.evaluate(
                DOWNLOAD_JS,
                {"mediaId": media_id, "fifeUrl": fife_url},
            )
            if not dl.get("ok"):
                raise RuntimeError(f"Scene {label} download failed: {dl.get('error')}")

            out_path.write_bytes(base64.b64decode(dl["base64"]))
            log(f"[{i}/{len(batch)}] Saved {out_path} ({dl.get('source')})")
            saved += 1

            if i < len(batch) and delay_seconds > 0:
                log(f"Waiting {delay_seconds}s before next prompt...")
                time.sleep(delay_seconds)

    finally:
        if owns_context:
            context.close()
        pw.stop()

    return saved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate images in Google Flow from image-prompts-only.txt"
    )
    parser.add_argument(
        "prompts_file",
        type=Path,
        help="Path to image-prompts-only.txt",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output folder (default: <prompts_dir>/generated)",
    )
    parser.add_argument("--start", type=int, default=1, help="First prompt index (1-based)")
    parser.add_argument("--count", type=int, default=5, help="How many prompts to run")
    parser.add_argument(
        "--cdp-url",
        default="http://127.0.0.1:9223",
        help="Chrome remote debugging URL (default: http://127.0.0.1:9223)",
    )
    parser.add_argument(
        "--use-open-chrome",
        action=argparse.BooleanOptionalAction,
        default=sys.platform == "darwin",
        help="Use your already-open Chrome window (default on macOS)",
    )
    parser.add_argument(
        "--cdp",
        action="store_true",
        help="Attach to Chrome remote debugging instead of using open Chrome",
    )
    parser.add_argument(
        "--no-cdp",
        action="store_true",
        help="Launch Chrome with your profile instead of CDP attach (with --cdp)",
    )
    parser.add_argument(
        "--flow-url",
        default=None,
        help="Flow URL to open if no Flow tab exists",
    )
    parser.add_argument(
        "--model",
        default="NARWHAL",
        choices=["NARWHAL", "GEM_PIX_2"],
        help="Flow image model (default: NARWHAL / Nano Banana 2)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="IMAGE_ASPECT_RATIO_LANDSCAPE",
        choices=["IMAGE_ASPECT_RATIO_LANDSCAPE", "IMAGE_ASPECT_RATIO_PORTRAIT"],
    )
    parser.add_argument("--delay", type=float, default=5.0, help="Seconds between prompts")
    parser.add_argument(
        "--wait-for-login",
        type=int,
        default=0,
        help="Seconds to wait for you to log into labs.google and open a Flow project",
    )
    parser.add_argument(
        "--chrome-user-data",
        type=Path,
        default=Path.home() / "Library/Application Support/Google/Chrome",
    )
    parser.add_argument("--profile", default="Default")
    args = parser.parse_args(argv)

    prompts_file = args.prompts_file.resolve()
    if not prompts_file.is_file():
        log(f"Prompt file not found: {prompts_file}")
        return 1

    output_dir = args.output_dir or (prompts_file.parent / "generated")

    use_open_chrome = args.use_open_chrome and not args.cdp

    try:
        if use_open_chrome:
            saved = generate_batch_open_chrome(
                prompts_file=prompts_file,
                output_dir=output_dir,
                start=args.start,
                count=args.count,
                flow_url=args.flow_url,
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                delay_seconds=args.delay,
                wait_for_login=args.wait_for_login,
            )
        else:
            cdp_url = None if args.no_cdp else args.cdp_url
            saved = generate_batch(
                prompts_file=prompts_file,
                output_dir=output_dir,
                start=args.start,
                count=args.count,
                cdp_url=cdp_url,
                flow_url=args.flow_url,
                model=args.model,
                aspect_ratio=args.aspect_ratio,
                delay_seconds=args.delay,
                wait_for_login=args.wait_for_login,
                chrome_user_data=args.chrome_user_data,
                profile=args.profile,
            )
    except Exception as exc:
        log(f"ERROR: {exc}")
        if use_open_chrome:
            log("")
            log("Using your open Chrome requires:")
            log("  1. View → Developer → Allow JavaScript from Apple Events (in Chrome)")
            log("  2. A Flow project tab open: https://labs.google/fx/tools/flow/project/...")
            log("  3. Re-run with wait time if you still need to sign in:")
            log(
                f"     python3 library/flow_generate.py '{prompts_file}' "
                f"--use-open-chrome --start {args.start} --count {args.count} --wait-for-login 300"
            )
        elif not use_open_chrome and args.cdp_url and "connect" in str(exc).lower():
            log("")
            log("Or use your already-open Chrome instead:")
            log(
                f"  python3 library/flow_generate.py '{prompts_file}' "
                f"--use-open-chrome --start {args.start} --count {args.count}"
            )
            log("")
            log("Or start debug Chrome:")
            log("  ./story-agent/start-flow-browser.sh")
        return 1

    log(f"Done — {saved} image(s) in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
