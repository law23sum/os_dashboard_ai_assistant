# Computer Use Integration Guide

This document outlines how to integrate OpenAI’s computer-using agent (CUA) model, `computer-use-preview`, into our assistants. The model loops through “see → plan → act” steps and uses `computer_call` tool events so we can automate UI-driven workflows such as booking, browsing, or form filling.

> ⚠️ **Preview status:** the model is still in beta and may be exploitable. Only run it inside sandboxed, low-trust environments and keep humans in the loop for high-impact actions.

## Basics

- Available only via the **Responses API** (`responses.create`), not Chat Completions.
- Use the `computer_use_preview` tool with explicit `display_width`, `display_height`, and `environment`.
- Set `truncation="auto"`; the tool requires it.
- Include screenshots (as `input_image` objects) whenever you have them.

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="computer-use-preview",
    tools=[
        {
            "type": "computer_use_preview",
            "display_width": 1024,
            "display_height": 768,
            "environment": "browser",
        }
    ],
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Check the latest OpenAI news on bing.com."},
            ],
        }
    ],
    reasoning={"summary": "concise"},
    truncation="auto",
)
```

## Integration loop

1. **Send initial request** with task description, tool config, and optional screenshot.
2. **Receive `computer_call`** actions (clicks, scrolls, keypresses, etc.).
3. **Execute** the action in a controlled environment (Playwright, Docker VM, etc.).
4. **Capture screenshot** of the updated state.
5. **Reply** via `computer_call_output`, optionally acknowledging safety checks, and repeat.

### Handling actions (Playwright example)

```python
def handle_model_action(page, action):
    match action.type:
        case "click":
            page.mouse.click(action.x, action.y, button=action.button or "left")
        case "scroll":
            page.mouse.move(action.x, action.y)
            page.evaluate(f"window.scrollBy({action.scroll_x}, {action.scroll_y})")
        case "keypress":
            for key in action.keys:
                page.keyboard.press("Enter" if key.lower() == "enter" else key)
        case "type":
            page.keyboard.type(action.text)
        case "wait":
            time.sleep(action.duration or 2)
        case "screenshot":
            pass
        case _:
            print("Unhandled action:", action)
```

### Sending follow-up requests

```python
encoded = base64.b64encode(screenshot_bytes).decode("utf-8")
response = client.responses.create(
    model="computer-use-preview",
    previous_response_id=response.id,
    tools=[{...}],
    input=[
        {
            "type": "computer_call_output",
            "call_id": computer_call.call_id,
            "output": {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{encoded}",
            },
            "acknowledged_safety_checks": acknowledged_checks,
            "current_url": current_url,
        }
    ],
    truncation="auto",
)
```

## Environments

### Local browser automation

Use Playwright/Selenium in a sandboxed profile:

```python
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        chromium_sandbox=True,
        env={},
        args=["--disable-extensions", "--disable-file-system"],
    )
    page = browser.new_page()
    page.goto("https://bing.com")
    page.wait_for_timeout(10_000)
```

### Docker + VNC desktop

Provision a container that runs XFCE, VNC, and browsers. Example `Dockerfile` snippet:

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y xfce4 x11vnc xvfb xdotool imagemagick firefox-esr ...
USER myuser
EXPOSE 5900
CMD ["sh", "-c", "Xvfb :99 ... && startxfce4 ... && tail -f /dev/null"]
```

Use helper utilities (shown in the source content) to execute `xdotool` commands and capture screenshots (`import -window root`).

## Safety checks

`computer_call` objects may include `pending_safety_checks` such as:

- `malicious_instructions`
- `irrelevant_domain`
- `sensitive_domain`

Before continuing, surface these warnings to the user and send them back as `acknowledged_safety_checks` on the next `computer_call_output`. Always pass the current URL when available to improve detection accuracy.

```json
{
  "type": "computer_call_output",
  "call_id": "call_123",
  "acknowledged_safety_checks": [
    {"id": "cu_sc_456", "code": "malicious_instructions", "message": "..."}
  ],
  "output": {"type": "computer_screenshot", "image_url": "..."},
  "current_url": "https://openai.com/docs"
}
```

## Risks & best practices

- Keep humans in the loop for high-stakes actions; the model makes mistakes.
- Treat every screenshot as untrusted input—prompt injection is real.
- Restrict domains/actions via allowlists or blocklists.
- Run in isolated sandboxes (no host env vars, disable extensions/filesystem access).
- Send `safety_identifier` metadata to aid abuse monitoring.
- Leverage the provided safety checks and implement additional guardrails, e.g., watch mode or manual approvals.
- Stay compliant with OpenAI [Usage Policies](https://openai.com/policies/usage-policies/) and [Business Terms](https://openai.com/policies/business-terms/).

## Further reading

- [CUA sample app](https://github.com/openai/openai-cua-sample-app)
- [Computer use API reference](https://platform.openai.com/docs/api-reference/computer-use)
- [Operator system card](https://openai.com/index/operator-system-card/)
- [Your data guide](https://platform.openai.com/docs/guides/your-data)
