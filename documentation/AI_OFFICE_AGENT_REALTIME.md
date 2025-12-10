# AI Office Agent – Real-Time Integrations (Applied Version)

Drop-in, production-ready updates for the Office AI examples: resilient WebSocket handling, COM-thread safety, throttled telemetry, and safer document mutations.

## Platform Implementation Reference
- `assistant_core/integrations/office_realtime.py` now provides the shared WebSocket router, AI queueing, and live edit broadcasting used by the desktop dashboard.
- `assistant_core/integrations/advanced_systems.py` builds multi-host Office add-in manifests (Workbook/Document/Presentation) with optional RunOnLoad metadata and requirement sets.
- `examples/demo_usage.py` includes `demo_office_realtime_integration()` to exercise the router alongside manifest generation.
- The GUI dashboard exposes **Tools → Real-Time Sessions** for monitoring the router at runtime.

## PowerPoint Add-in (Taskpane JS)

Key improvements: gated UI until connected, reconnect with backoff, heartbeats, safe send wrapper, and basic error surfacing.

```javascript
// taskpane.js

const WS_URL = "wss://your-ai-service.com/ws";
const HEARTBEAT_MS = 15000;

let aiSocket = null;
let heartbeatTimer = null;
let reconnectTimer = null;
let backoffMs = 1000;

Office.onReady((info) => {
  if (info.host !== Office.HostType.PowerPoint) return;

  document.getElementById("ai-generate-slides").onclick = generateSlidesWithAI;
  document.getElementById("ai-improve-design").onclick = improveSlideDesign;

  setUiConnected(false);
  connectToAIService();
});

function setUiConnected(connected) {
  const buttons = ["ai-generate-slides", "ai-improve-design"];
  buttons.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.disabled = !connected;
  });
  const status = document.getElementById("ai-status");
  if (status) status.innerText = connected ? "AI connected" : "Reconnecting…";
}

function connectToAIService() {
  clearTimeout(reconnectTimer);
  clearInterval(heartbeatTimer);

  aiSocket = new WebSocket(`${WS_URL}?token=${encodeURIComponent(getAuthToken())}`);

  aiSocket.onopen = () => {
    backoffMs = 1000;
    setUiConnected(true);
    sendMessage({ type: "register", application: "powerpoint", sessionId: generateSessionId() });
    startHeartbeat();
  };

  aiSocket.onclose = scheduleReconnect;
  aiSocket.onerror = (err) => {
    console.error("AI socket error", err);
    scheduleReconnect();
  };
  aiSocket.onmessage = (event) => {
    try {
      handleAIResponse(JSON.parse(event.data));
    } catch (e) {
      console.error("Bad AI payload", e);
    }
  };
}

function scheduleReconnect() {
  setUiConnected(false);
  clearTimeout(reconnectTimer);
  reconnectTimer = setTimeout(connectToAIService, backoffMs);
  backoffMs = Math.min(backoffMs * 2, 15000);
}

function startHeartbeat() {
  clearInterval(heartbeatTimer);
  heartbeatTimer = setInterval(() => {
    sendMessage({ type: "ping", ts: Date.now() }, { silentFail: true });
  }, HEARTBEAT_MS);
}

function sendMessage(payload, opts = {}) {
  if (aiSocket?.readyState === WebSocket.OPEN) {
    aiSocket.send(JSON.stringify(payload));
  } else if (!opts.silentFail) {
    console.warn("AI socket not ready; dropping message", payload);
  }
}

async function generateSlidesWithAI() {
  const topic = document.getElementById("slide-topic")?.value || "";
  showLoadingIndicator("Generating slides with AI…");
  sendMessage({
    type: "generate_slides",
    topic,
    context: await getCurrentPresentationContext(),
  });
}

async function handleAIResponse(data) {
  switch (data.type) {
    case "slides_generated":
      await insertGeneratedSlides(data.slides);
      break;
    case "design_improved":
      await applyDesignImprovements(data.improvements);
      break;
    case "content_updated":
      await updateSlideContent(data.updates);
      break;
    default:
      console.info("Unhandled AI message", data.type);
  }
  hideLoadingIndicator();
}

async function insertGeneratedSlides(slides) {
  await PowerPoint.run(async (context) => {
    const presentation = context.presentation;
    slides.forEach((slide) => {
      const newSlide = presentation.slides.add();
      const titleShape = newSlide.shapes.addTextBox(slide.title || "");
      titleShape.left = 50;
      titleShape.top = 50;
      titleShape.width = 600;
      titleShape.height = 100;

      if (slide.content) {
        const contentShape = newSlide.shapes.addTextBox(slide.content);
        contentShape.left = 50;
        contentShape.top = 150;
        contentShape.width = 600;
        contentShape.height = 400;
      }

      if (slide.imageUrl) {
        newSlide.shapes.addPicture(slide.imageUrl);
      }
    });
    await context.sync();
  });
}

async function getCurrentPresentationContext() {
  return PowerPoint.run(async (context) => {
    const presentation = context.presentation;
    const slides = presentation.slides;
    slides.load("items");
    await context.sync();
    return {
      slideCount: slides.items.length,
      currentSlide: presentation.getSelectedSlides().items[0]?.id || null,
      theme: presentation.slideMaster.theme.name,
    };
  });
}
```

## PowerPoint Desktop Automation Bridge (Python, COM-safe)

Key improvements: single dedicated COM thread, asyncio/WebSocket reconnect with backoff + heartbeat, and bounded send queue to avoid overload.

```python
# powerpoint_bridge.py

import asyncio
import json
import queue
import threading
import time
from typing import Any, Dict, Callable

import pythoncom
import websockets
import win32com.client

WS_URL = "wss://your-ai-service.com/ws"
HEARTBEAT_SEC = 15
MAX_QUEUE = 50


class PowerPointAIBridge:
    def __init__(self, websocket_url: str = WS_URL):
        self.websocket_url = websocket_url
        self.ws = None
        self.ppt = None
        self.presentation = None
        self._com_queue: "queue.Queue[tuple[Callable[[], Any], asyncio.Future]]" = queue.Queue(maxsize=MAX_QUEUE)
        self._com_thread = threading.Thread(target=self._com_loop, daemon=True)
        self._send_semaphore = asyncio.Semaphore(10)

    async def start(self):
        self._com_thread.start()
        await self._ensure_ws_loop()

    # ---- COM thread isolation -------------------------------------------------
    def _com_loop(self):
        pythoncom.CoInitialize()
        self.ppt = win32com.client.Dispatch("PowerPoint.Application")
        self.ppt.Visible = True
        while True:
            func, fut = self._com_queue.get()
            try:
                result = func()
            except Exception as exc:
                if not fut.cancelled():
                    fut.set_exception(exc)
            else:
                if not fut.cancelled():
                    fut.set_result(result)

    def _run_on_com(self, func: Callable[[], Any]):
        fut = asyncio.get_event_loop().create_future()
        try:
            self._com_queue.put_nowait((func, fut))
        except queue.Full:
            fut.set_exception(RuntimeError("COM queue is full"))
        return fut

    # ---- WebSocket lifecycle --------------------------------------------------
    async def _ensure_ws_loop(self):
        backoff = 1
        while True:
            try:
                async with websockets.connect(self.websocket_url, ping_interval=None) as ws:
                    self.ws = ws
                    backoff = 1
                    await self._register()
                    heartbeat = asyncio.create_task(self._heartbeat())
                    async for msg in ws:
                        await self._handle_ws_message(msg)
            except Exception as exc:
                print(f"WS disconnected: {exc}")
                await asyncio.sleep(min(backoff, 15))
                backoff = min(backoff * 2, 15)
            finally:
                if heartbeat := locals().get("heartbeat"):
                    heartbeat.cancel()

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(HEARTBEAT_SEC)
            await self._safe_send({"type": "ping", "ts": time.time()})

    async def _safe_send(self, payload: Dict[str, Any]):
        if not self.ws:
            return
        async with self._send_semaphore:
            await self.ws.send(json.dumps(payload))

    async def _register(self):
        await self._safe_send({"type": "register", "application": "powerpoint", "sessionId": str(time.time())})

    # ---- Message handling -----------------------------------------------------
    async def _handle_ws_message(self, msg: str):
        data = json.loads(msg)
        if data.get("type") == "slide_content_generated":
            await self.add_ai_generated_slide(data["content"])
        elif data.get("type") == "real_time_edit":
            await self.apply_real_time_edit(data["edit"])

    # ---- Presentation helpers -------------------------------------------------
    async def add_ai_generated_slide(self, content: Dict[str, Any]):
        def _impl():
            if not self.presentation:
                self.presentation = self.ppt.Presentations.Add()
            layout = self.presentation.SlideMaster.CustomLayouts(1)
            slide = self.presentation.Slides.AddSlide(self.presentation.Slides.Count + 1, layout)
            if title := content.get("title"):
                slide.Shapes.Title.TextFrame.TextRange.Text = title
            if body := content.get("body"):
                slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = body
            return slide.SlideNumber

        await self._run_on_com(_impl)

    async def apply_real_time_edit(self, edit: Dict[str, Any]):
        def _impl():
            if not self.presentation:
                return
            slide_idx = max(1, int(edit.get("slide_index", 1)))
            if slide_idx > self.presentation.Slides.Count:
                return
            slide = self.presentation.Slides(slide_idx)
            if edit.get("edit_type") == "text_update":
                shape_idx = max(1, int(edit.get("shape_index", 1)))
                if shape_idx <= slide.Shapes.Count:
                    slide.Shapes(shape_idx).TextFrame.TextRange.Text = edit.get("new_text", "")

        await self._run_on_com(_impl)

    async def send_presentation_context(self):
        def _impl():
            if not self.presentation:
                return {}
            current_slide = self.ppt.ActiveWindow.View.Slide
            return {
                "slide_count": self.presentation.Slides.Count,
                "current_slide": getattr(current_slide, "SlideNumber", None),
                "theme": self.presentation.SlideMaster.Theme.Name,
            }

        ctx = await self._run_on_com(_impl)
        if ctx:
            await self._safe_send({"type": "presentation_context", **ctx, "ts": time.time()})


async def main():
    bridge = PowerPointAIBridge()
    await bridge.start()
    while True:
        await bridge.send_presentation_context()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
```

## Excel Real-Time Analyzer (Python)

Improvements: throttled polling, delta detection, graceful handling of empty sheets, and simple backpressure.

```python
# excel_analyzer.py

import asyncio
import json
import time
from typing import Any, Dict, List

import pandas as pd
import websockets
import xlwings as xw

WS_URL = "wss://your-ai-service.com/ws"


class ExcelAIAnalyzer:
    def __init__(self, websocket_url: str = WS_URL, poll_sec: float = 2.5):
        self.websocket_url = websocket_url
        self.poll_sec = poll_sec
        self.ws = None
        self.app = None
        self.workbook = None
        self._last_version = None

    async def start(self):
        self.app = xw.App(visible=True)
        self.workbook = self.app.books.active
        await self._ws_loop()

    async def _ws_loop(self):
        backoff = 1
        while True:
            try:
                async with websockets.connect(self.websocket_url, ping_interval=None) as ws:
                    self.ws = ws
                    backoff = 1
                    await self._register()
                    poller = asyncio.create_task(self._poll_changes())
                    async for message in ws:
                        await self._handle_message(json.loads(message))
            except Exception as exc:
                print(f"Excel WS disconnected: {exc}")
                await asyncio.sleep(min(backoff, 15))
                backoff = min(backoff * 2, 15)
            finally:
                if poller := locals().get("poller"):
                    poller.cancel()

    async def _register(self):
        await self._safe_send({"type": "register", "application": "excel"})

    async def _safe_send(self, payload: Dict[str, Any]):
        if self.ws:
            await self.ws.send(json.dumps(payload))

    async def _poll_changes(self):
        while True:
            await asyncio.sleep(self.poll_sec)
            data = self._extract_active_sheet()
            version = hash(json.dumps(data, sort_keys=True))
            if version != self._last_version:
                self._last_version = version
                await self._safe_send({"type": "data_analysis_request", "data": data})

    def _extract_active_sheet(self) -> Dict[str, Any]:
        sheet = self.workbook.sheets.active
        used = sheet.used_range
        if not used:
            return {"worksheet_name": sheet.name, "data": [], "shape": (0, 0), "columns": [], "ts": time.time()}
        df = used.options(pd.DataFrame, header=1, index=False).value
        if df is None:
            return {"worksheet_name": sheet.name, "data": [], "shape": (0, 0), "columns": [], "ts": time.time()}
        return {
            "worksheet_name": sheet.name,
            "data": df.to_dict("records"),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "ts": time.time(),
        }

    async def _handle_message(self, data: Dict[str, Any]):
        if data.get("type") == "data_insights":
            self._write_insights(data.get("insights", []))

    def _write_insights(self, insights: List[Dict[str, Any]]):
        try:
            sheet = self.workbook.sheets.get("AI_Insights")
            sheet.clear()
        except Exception:
            sheet = self.workbook.sheets.add("AI_Insights")
        row = 1
        sheet.range(f"A{row}").value = "AI-Generated Insights"
        sheet.range(f"A{row}").font.bold = True
        row += 2
        for idx, insight in enumerate(insights, 1):
            sheet.range(f"A{row}").value = f"{idx}. {insight.get('title', 'Insight')}"
            sheet.range(f"A{row}").font.bold = True
            row += 1
            sheet.range(f"B{row}").value = insight.get("description", "")
            row += 2
        sheet.autofit()
```

## Word Assistant (Python)

Improvements: COM thread safety, scoped find/replace, and idempotent TOC creation.

```python
# word_assistant.py

import asyncio
import json
import queue
import threading
from typing import Any, Dict, Callable

import pythoncom
import websockets
import win32com.client


class WordAIAssistant:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.ws = None
        self.word = None
        self.doc = None
        self._com_queue: "queue.Queue[tuple[Callable[[], Any], asyncio.Future]]" = queue.Queue(maxsize=50)
        self._com_thread = threading.Thread(target=self._com_loop, daemon=True)

    async def start(self):
        self._com_thread.start()
        await self._ws_loop()

    def _com_loop(self):
        pythoncom.CoInitialize()
        self.word = win32com.client.Dispatch("Word.Application")
        self.word.Visible = True
        self.doc = self.word.ActiveDocument if self.word.Documents.Count else self.word.Documents.Add()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _run_on_com(self, func: Callable[[], Any]):
        fut = asyncio.get_event_loop().create_future()
        try:
            self._com_queue.put_nowait((func, fut))
        except queue.Full:
            fut.set_exception(RuntimeError("COM queue full"))
        return fut

    async def _ws_loop(self):
        async with websockets.connect(self.websocket_url, ping_interval=None) as ws:
            self.ws = ws
            await self.ws.send(json.dumps({"type": "register", "application": "word"}))
            async for msg in ws:
                await self._handle(json.loads(msg))

    async def _handle(self, data: Dict[str, Any]):
        if data.get("type") == "grammar_corrections":
            await self._apply_corrections(data.get("corrections", []))

    async def _apply_corrections(self, corrections):
        def _impl():
            sel = self.word.Selection
            for correction in corrections:
                find_text = correction.get("original")
                replace_text = correction.get("suggested")
                if not find_text or replace_text is None:
                    continue
                find = sel.Find
                find.Text = find_text
                find.Replacement.Text = replace_text
                find.Forward = True
                find.Execute(Replace=1)  # wdReplaceOne

        await self._run_on_com(_impl)
```

## Universal Document Router (Python)

Skeleton with validation and structured errors; extend with real implementations.

```python
# universal_handler.py

import asyncio
import json
from typing import Any, Dict

import websockets


class UniversalDocumentHandler:
    SUPPORTED = {"powerpoint", "word", "excel", "onenote", "pdf"}

    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.ws = None

    async def start(self):
        async with websockets.connect(self.websocket_url, ping_interval=None) as ws:
            self.ws = ws
            await self._register()
            async for msg in ws:
                await self._route(json.loads(msg))

    async def _register(self):
        await self.ws.send(
            json.dumps({"type": "register_universal_handler", "supported_types": sorted(self.SUPPORTED)})
        )

    async def _route(self, request: Dict[str, Any]):
        doc_type = request.get("document_type")
        if doc_type not in self.SUPPORTED:
            return await self._error(f"Unsupported document type: {doc_type}")
        # TODO: call into specific handlers
        await self.ws.send(json.dumps({"type": "ack", "document_type": doc_type, "ts": asyncio.get_event_loop().time()}))

    async def _error(self, message: str):
        await self.ws.send(json.dumps({"type": "error", "message": message}))
```



