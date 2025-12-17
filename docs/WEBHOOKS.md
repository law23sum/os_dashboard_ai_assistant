# Webhooks

Use webhooks to receive real-time updates from the OpenAI API. OpenAI [webhooks](http://chatgpt.com/?q=eli5+what+is+a+webhook?) notify your server when batch jobs finish, background responses complete, fine-tuning concludes, and more. Events are delivered to an HTTPS endpoint you control using the [Standard Webhooks specification](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md). The complete catalog of events lives in the [API reference](/docs/api-reference/webhook-events).

[API reference for webhook events](/docs/api-reference/webhook-events)

Below are minimal Flask and Express servers that handle [`response.completed`](/docs/api-reference/webhook-events/response/completed) events.

---

## Webhook server examples

```python
import os
from openai import OpenAI, InvalidWebhookSignatureError
from flask import Flask, request, Response

app = Flask(__name__)
client = OpenAI(webhook_secret=os.environ["OPENAI_WEBHOOK_SECRET"])

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        event = client.webhooks.unwrap(request.data, request.headers)

        if event.type == "response.completed":
            response_id = event.data.id
            response = client.responses.retrieve(response_id)
            print("Response output:", response.output_text)

        return Response(status=200)
    except InvalidWebhookSignatureError as e:
        print("Invalid signature", e)
        return Response("Invalid signature", status=400)

if __name__ == "__main__":
    app.run(port=8000)
```

```javascript
import OpenAI from "openai";
import express from "express";

const app = express();
const client = new OpenAI({ webhookSecret: process.env.OPENAI_WEBHOOK_SECRET });

// Don't use express.json(); signature verification needs the raw text body
app.use(express.text({ type: "application/json" }));

app.post("/webhook", async (req, res) => {
  try {
    const event = await client.webhooks.unwrap(req.body, req.headers);

    if (event.type === "response.completed") {
      const response_id = event.data.id;
      const response = await client.responses.retrieve(response_id);
      const output_text = response.output
        .filter((item) => item.type === "message")
        .flatMap((item) => item.content)
        .filter((contentItem) => contentItem.type === "output_text")
        .map((contentItem) => contentItem.text)
        .join("");

      console.log("Response output:", output_text);
    }
    res.status(200).send();
  } catch (error) {
    if (error instanceof OpenAI.InvalidWebhookSignatureError) {
      console.error("Invalid signature", error);
      res.status(400).send("Invalid signature");
    } else {
      throw error;
    }
  }
});

app.listen(8000, () => {
  console.log("Webhook server is running on port 8000");
});
```

To observe events, configure a webhook endpoint in the dashboard for `response.completed`, then trigger a [background response](/docs/guides/background). You can also fire sample deliveries from the [webhook settings page](/settings/project/webhooks).

```bash
curl https://api.openai.com/v1/responses \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $OPENAI_API_KEY" \
-d '{
  "model": "o3",
  "input": "Write a very long novel about otters in space.",
  "background": true
}'
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const resp = await client.responses.create({
  model: "o3",
  input: "Write a very long novel about otters in space.",
  background: true,
});

console.log(resp.status);
```

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
  model="o3",
  input="Write a very long novel about otters in space.",
  background=True,
)

print(resp.status)
```

---

## Creating webhook endpoints

Webhooks are configured per project. Visit the [webhook settings page](/settings/project/webhooks) and click **Create** to define:

1. A friendly name.
2. The public URL of your server.
3. One or more event types. When they fire, OpenAI POSTs the payload to your URL.

After saving, copy the signing secret for request verification—you won't be able to view it again.

![webhook endpoint edit dialog](https://cdn.openai.com/API/images/webhook_config.png)

---

## Handling webhook requests

When subscribed events occur, OpenAI sends an HTTP POST similar to:

```
POST https://yourserver.com/webhook
user-agent: OpenAI/1.0 (+https://platform.openai.com/docs/webhooks)
content-type: application/json
webhook-id: wh_685342e6c53c8190a1be43f081506c52
webhook-timestamp: 1750287078
webhook-signature: v1,K5oZfzN95Z9UVu1EsfQmfVNQhnkZ2pj9o9NDN/H/pI4=
{
  "object": "event",
  "id": "evt_685343a1381c819085d44c354e1b330e",
  "type": "response.completed",
  "created_at": 1750287018,
  "data": { "id": "resp_abc123" }
}
```

Respond quickly with `2xx` so retries do not occur. Offload heavy processing to background workers and treat `webhook-id` as an idempotency key because duplicates are possible. OpenAI retries failed attempts for up to 72 hours with exponential backoff. Redirects (3xx) count as failures, so always supply the final URL.

### Testing locally

You need a publicly reachable URL. Options include:

* [ngrok](https://ngrok.com/) tunnels for local servers.
* Cloud dev environments such as [Replit](https://replit.com/), [GitHub Codespaces](https://github.com/features/codespaces), [Cloudflare Workers](https://workers.cloudflare.com/), or [v0 from Vercel](https://v0.dev/).

---

## Verifying webhook signatures

Always verify inbound requests before acting on them. When your endpoint receives a payload, use the signing secret provided in the dashboard:

```
export OPENAI_WEBHOOK_SECRET="<your secret here>"
```

### OpenAI SDK helpers

```python
client = OpenAI()
webhook_secret = os.environ["OPENAI_WEBHOOK_SECRET"]

event = client.webhooks.unwrap(request.data, request.headers, secret=webhook_secret)
```

```javascript
const client = new OpenAI();
const webhook_secret = process.env.OPENAI_WEBHOOK_SECRET;

const event = client.webhooks.unwrap(req.body, req.headers, { secret: webhook_secret });
```

### Standard Webhooks libraries

```rust
use standardwebhooks::Webhook;

let webhook_secret = std::env::var("OPENAI_WEBHOOK_SECRET").expect("OPENAI_WEBHOOK_SECRET not set");
let wh = Webhook::new(webhook_secret);
wh.verify(webhook_payload, webhook_headers).expect("Webhook verification failed");
```

```php
$webhook_secret = getenv("OPENAI_WEBHOOK_SECRET");
$wh = new \StandardWebhooks\Webhook($webhook_secret);
$wh->verify($webhook_payload, $webhook_headers);
```

Alternatively, implement your own verifier per the [Standard Webhooks spec](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md#verifying-webhook-authenticity). If a signing secret leaks or is lost, rotate it in the [webhook settings](/settings/project/webhooks).

---

Was this page useful?
