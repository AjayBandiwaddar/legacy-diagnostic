import json
import os
from pathlib import Path

import requests
import streamlit as st

from scanner import scan_directory, scan_zip

st.set_page_config(page_title="LSD | Legacy System Diagnostic", page_icon="🛡️", layout="wide")
st.markdown("<style>.stApp {background:#0b1020;color:#e5e7eb}.stButton>button {background:#2563eb;color:white}</style>", unsafe_allow_html=True)
st.title("Legacy System Health Diagnostic")
st.caption("Local deterministic scanning. Only redacted, structured findings go to Lambda.")

with st.sidebar:
    st.header("Lambda configuration")
    function_url = st.text_input("Function URL", value=os.getenv("LSD_FUNCTION_URL", ""))
    api_token = st.text_input("API token", value=os.getenv("LSD_APP_API_TOKEN", ""), type="password")
    timeout = st.number_input("Request timeout (seconds)", min_value=5, max_value=60, value=25)

uploaded = st.file_uploader("Upload a repository ZIP", type="zip")
use_demo = st.button("Load seeded legacy demo")
if uploaded:
    try:
        st.session_state.scan_result = scan_zip(uploaded.getvalue())
    except (ValueError, OSError) as error:
        st.error(f"ZIP rejected: {error}")
elif use_demo:
    st.session_state.scan_result = scan_directory(Path(__file__).parent / "demo_repo")

result = st.session_state.get("scan_result")

if result:
    findings = result["findings"]
    counts = {level: sum(f["severity"] == level for f in findings) for level in ("critical", "high", "medium")}
    cols = st.columns(4)
    for col, (label, value) in zip(cols, [("Critical", counts["critical"]), ("High", counts["high"]), ("Medium", counts["medium"]), ("Total", len(findings))]):
        col.metric(label, value)
    st.caption(f"Files scanned: {result['files_scanned']}")
    st.dataframe(findings, use_container_width=True, hide_index=True)
    report = {"files_scanned": result["files_scanned"], "findings": findings}
    st.download_button("Download complete report", json.dumps(report, indent=2), "lsd-report.json", "application/json")
    if st.button("Generate modernization roadmap"):
        if not function_url or not api_token:
            st.error("Enter both Function URL and API token in the sidebar.")
        else:
            try:
                response = requests.post(function_url, json={"findings": findings}, headers={"x-api-key": api_token}, timeout=timeout)
                if response.status_code in (401, 403):
                    st.error("Authentication failed. Check the API token.")
                elif response.status_code == 429:
                    st.error("Lambda is rate-limiting requests. Try again shortly.")
                elif response.status_code >= 500:
                    st.error("Lambda failed. Check its CloudWatch logs.")
                else:
                    response.raise_for_status()
                    body = response.json()
                    st.markdown(body.get("roadmap", "Lambda returned no roadmap."))
            except requests.Timeout:
                st.error("Lambda request timed out.")
            except requests.RequestException as error:
                st.error(f"Network or request failure: {error}")
            except ValueError:
                st.error("Lambda returned invalid JSON.")
