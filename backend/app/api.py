from dotenv import load_dotenv
import os 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .detector import run_analysis
from .razorpay_client import fetch_payments, fetch_payment_events

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "backend" / ".env")

print("Razorpay key loaded:", bool(os.getenv("RAZORPAY_KEY_ID")))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
def analyze():
    return run_analysis()

@app.get("/analyze/razorpay")
def analyze_razorpay():
    payments = fetch_payment_events()
    return run_analysis(payments)

@app.get("/razorpay/payments")
def razorpay_payments():
    return fetch_payments()