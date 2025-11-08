# backend/app/main.py


import os, tempfile
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from dotenv import load_dotenv
load_dotenv()
from .db import SessionLocal, engine
from .models import Base, Company, BalanceSheet, FinancialLine, UserCompany, User
from .pdf_extractor import extract_tables_and_text, extract_key_numbers
from .metrics import debt_equity, net_margin
from .llm_client import call_llm
from .auth import verify_password, create_access_token, get_current_user, get_password_hash
from . import seed_data
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from typing import Optional

# Create DB
Base.metadata.create_all(bind=engine)
# Seed minimal data if empty
seed_data.seed()

app = FastAPI(title="Balance Sheet Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://balancesheetanalysis-r6pedsb7h-yashrajs-projects-b78a66e5.vercel.app/"
    
        # add other origins you use (e.g. "http://localhost" if using nginx)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/login")
def login(payload: dict):
    db = SessionLocal()
    user = db.query(User).filter(User.email == payload.get("email")).first()
    db.close()
    if not user or not verify_password(payload.get("password", ""), user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": user.role, "group": user.group_name})
    return {"access_token": token, "token_type": "bearer"}

def get_user_companies(user: User):
    db = SessionLocal()
    if user.role == "group_admin" and user.group_name:
        companies = db.query(Company).filter(Company.group_name == user.group_name).all()
    else:
        company_ids = [r.company_id for r in db.query(UserCompany).filter(UserCompany.user_id == user.id).all()]
        companies = db.query(Company).filter(Company.id.in_(company_ids)).all()
    db.close()
    return companies



# Replace the upload_pdf endpoint with this implementation (adjust names if your function signature differs):
# add this helper (place after imports, before endpoint definitions)
def compute_kpis(numeric_context: dict):
    """
    Compute basic KPIs from numeric_context dict.
    numeric_context keys expected: 'total_liabilities', 'total_assets', 'revenue', 'profit_after_tax', 'ebitda'
    Falls back gracefully if values missing.
    """
    # safe extraction with fallbacks
    def _get(k):
        v = numeric_context.get(k)
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    total_liabilities = _get("total_liabilities")
    total_assets = _get("total_assets")
    revenue = _get("revenue")
    profit_after_tax = _get("profit_after_tax")
    ebitda = _get("ebitda")

    kpis = {}
    try:
        if total_assets and total_liabilities is not None:
            # debt_equity expects liabilities and equity (we approximate equity = assets - liabilities)
            equity = None
            if total_assets is not None and total_liabilities is not None:
                equity = total_assets - total_liabilities
            if equity and total_liabilities is not None:
                kpis["debt_equity"] = debt_equity(total_liabilities, equity)  # adapt if your function signature differs
    except Exception:
        pass

    try:
        if profit_after_tax is not None and revenue:
            kpis["net_margin"] = net_margin(profit_after_tax, revenue)  # adapt if signature differs
    except Exception:
        pass

    # include raw values for UI
    kpis["revenue"] = revenue
    kpis["total_assets"] = total_assets
    kpis["total_liabilities"] = total_liabilities
    kpis["profit_after_tax"] = profit_after_tax
    kpis["ebitda"] = ebitda
    return kpis


# Replace your existing upload_pdf with this Python-3.9-compatible function:
  # you already have this; keep it

@app.post("/upload_pdf")
def upload_pdf(
    company_name: str = Form(...),
    pdf_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        # fetch company and eager-load if needed
        comp = db.query(Company).filter(Company.name == company_name).options(joinedload(Company.balance_sheets)).first()
        if not comp:
            raise HTTPException(status_code=404, detail="Company not found")

        # create a new BalanceSheet record for this upload
        period_label = "uploaded:" + (file.filename if file else "url_upload")
        bs = BalanceSheet(company_id=comp.id, period_label=period_label)
        db.add(bs)
        db.commit()
        db.refresh(bs)

        # download or save uploaded file to a temp file
        tmp_pdf_path = None
        if pdf_url:
            import requests, tempfile
            try:
                r = requests.get(pdf_url, timeout=30)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                tmp.write(r.content)
                tmp.close()
                tmp_pdf_path = tmp.name
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to download PDF: {e}")
        elif file:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(file.file.read())
            tmp.close()
            tmp_pdf_path = tmp.name
        else:
            raise HTTPException(status_code=400, detail="Either pdf_url or file must be provided")

        # extract tables and text
        tables, text = extract_tables_and_text(tmp_pdf_path)

        # extract numeric context and compute KPIs
        numeric_context = extract_key_numbers(tables, text)
        kpis = compute_kpis(numeric_context)

        # call LLM (mock or real, depending on your llm_client.py)
        analysis = call_llm(comp.name, numeric_context, question="Board-level summary for CEO")

        # prepare response by reading values into plain Python types (avoid lazy-load after closing session)
        response_payload = {
            "company": comp.name,
            "period": bs.period_label,
            "numeric_context": numeric_context,
            "kpis": kpis,
            "analysis": analysis
        }

    finally:
        db.close()

    return response_payload



@app.get("/companies")
def list_companies(current_user: User = Depends(get_current_user)):
    comps = get_user_companies(current_user)
    return [{"id": c.id, "name": c.name, "group": c.group_name, "ticker": c.ticker} for c in comps]

@app.get("/companies/{company_id}/balance_sheets")
def company_balance_sheets(company_id: int, current_user: User = Depends(get_current_user)):
    # RBAC: ensure user may access company
    allowed = [c.id for c in get_user_companies(current_user)]
    if company_id not in allowed:
        raise HTTPException(status_code=403, detail="Access denied")
    db = SessionLocal()
    sheets = db.query(BalanceSheet).filter(BalanceSheet.company_id == company_id).all()
    out = []
    for s in sheets:
        lines = db.query(FinancialLine).filter(FinancialLine.balance_sheet_id == s.id).all()
        lines_out = {l.line_code: l.amount for l in lines}
        out.append({"id": s.id, "period_label": s.period_label, "lines": lines_out})
    db.close()
    return out

# more endpoints (metrics, chat, alerts) can be added similarly
