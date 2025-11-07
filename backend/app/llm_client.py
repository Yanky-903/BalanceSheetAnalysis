import os, json, time

# Read flags first — allow mocking without requiring OPENAI key
MOCK = os.getenv("MOCK_LLM", "0").lower() in ("1", "true", "yes")

# Only import OpenAI client if we are NOT mocking
client = None
if not MOCK:
    try:
        from openai import OpenAI
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY must be set when MOCK_LLM is not enabled")
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        # If import fails or key missing, fall back to mock mode behavior by setting client=None.
        client = None

MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def mock_response(company_name, numeric_context, question):
    rev = numeric_context.get("revenue") or numeric_context.get("Revenue") or None
    assets = numeric_context.get("total_assets") or numeric_context.get("totalAssets") or None
    return {
        "tldr": f"{company_name}: Revenue {'{:,}'.format(int(rev)) if rev else 'N/A'}.",
        "highlights": [
            f"Revenue: {rev if rev else 'N/A'}",
            f"Total assets: {assets if assets else 'N/A'}"
        ],
        "risks": ["Monitor leverage and liquidity", "Watch margin trends"],
        "actions": ["Review cost structure", "Review working capital policies"]
    }

def call_llm(company_name: str, numeric_context: dict, question: str = "Board-level summary for CEO"):
    """
    Returns parsed JSON (dict). If MOCK_LLM set, returns a deterministic mock.
    If real client is configured, calls OpenAI and attempts to parse JSON; on errors falls back to mock.
    """
    # If mocking is explicitly enabled or client isn't available, return mock
    if MOCK or client is None:
        return mock_response(company_name, numeric_context, question)

    # Compose prompts
    system_prompt = (
        "You are an expert financial analyst. Given structured numeric context, produce a concise "
        "board-level JSON with keys: tldr (string), highlights (list), risks (list), actions (list)."
    )
    user_content = (
        f"Company: {company_name}\nNumeric context:\n{json.dumps(numeric_context)}\nQuestion: {question}\n"
        "Return only valid JSON with keys: tldr, highlights, risks, actions."
    )

    retries = 0
    while True:
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":user_content}
                ],
                max_tokens=400,
                temperature=0.0,
            )
            # extract message content robustly
            try:
                content = resp.choices[0].message.content
            except Exception:
                try:
                    content = resp.choices[0]["message"]["content"]
                except Exception:
                    content = str(resp)
            content = str(content).strip()
            # try parse JSON
            try:
                return json.loads(content)
            except Exception:
                # try to extract JSON substring
                s = content.find("{")
                e = content.rfind("}")
                if s != -1 and e != -1 and e > s:
                    try:
                        return json.loads(content[s:e+1])
                    except Exception:
                        pass
            return {"raw": content}
        except Exception as e:
            # For rate limits or other OpenAIErrors, fallback to mock after small retries
            retries += 1
            if retries <= 2:
                time.sleep(1.5 ** retries)
                continue
            return {"error": "llm_failed", "message": str(e), "fallback": mock_response(company_name, numeric_context, question)}
