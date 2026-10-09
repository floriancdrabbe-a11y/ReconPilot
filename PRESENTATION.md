# ReconPilot — Final Presentation & Demo Checklist

This file is a practical run sheet for the final capstone presentation.

## Before presenting

Make sure:

- Metasploitable 3 Ubuntu is running.
- Kali is running.
- Ollama is running on the Windows host.
- `qwen2.5:3b` is installed.
- Kali can reach the Ollama endpoint.
- The final authorised Nmap XML is available.
- Streamlit launches without errors.
- The GUI shows the expected 7-service result.
- The presentation machine is not relying on internet access for the demo.

Recommended launch command:

```bash
cd ~/reconpilot_gui
source .venv/bin/activate
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 60-second product explanation

**Problem:** Nmap provides detailed reconnaissance evidence, but less-experienced testers can still struggle to decide what to investigate next.

**Solution:** ReconPilot takes authorised Nmap XML, preserves the original evidence in Python, asks a local LLM to choose only from approved next actions, validates the answer, and gives the user guided support.

**Important point:** ReconPilot is not an autonomous exploitation tool. It assists the tester and stops before active testing unless a human approves the next stage.

## Live demo order

### 1. Show the home screen

Briefly point out:

- XML upload
- local model selector
- Analyse Scan button
- safety boundary / human review message

Keep **Qwen2.5 3B** selected for the main demo.

### 2. Upload the authorised scan

Use the final Metasploitable XML.

Expected summary:

- Target: `172.28.128.3`
- Services analysed: **7**
- Validated recommendations: **7**
- Rejected outputs: **0**

### 3. Show MySQL first

This is one of the best examples because the version is missing.

Key line to say:

> "ReconPilot does not jump straight to a vulnerability claim. Because the exact MySQL version is missing, it tells the user to identify the version first."

Point out:

- original evidence
- recommended next step
- what to look for
- what to record
- stop / approval condition

### 4. Show ProFTPD 1.3.5

Key line:

> "Here the evidence is stronger because Nmap identified an exact product and version, so ReconPilot moves to trusted vulnerability-reference checking."

Do **not** say ReconPilot found or proved a vulnerability.

### 5. Explain the safety design

Keep this short:

- Nmap evidence is the source of truth
- scan fields are treated as untrusted data
- LLM only selects from approved actions
- Python validates the output
- human approval remains before active testing

### 6. Show the practical validation

Explain the chain:

```text
Nmap → ProFTPD 1.3.5
ReconPilot → Check trusted vulnerability references
Metasploit → CVE-2015-3306 / ProFTPD mod_copy module
Metasploit check → Target appears vulnerable
```

Important wording:

> "Metasploit's check indicated that the target appears vulnerable. We did not run the exploit."

### 7. Show evaluation results

Use the simple numbers:

- Schema validity: **100%**
- Safety: **100%**
- Evidence fidelity: **100%**
- Recommendation relevance: **90%**
- Guidance completeness: **100%**
- Usefulness proxy: **90%**
- Average response time: **3.393 seconds**
- Prompt-injection case: **passed**

If asked why relevance is not 100%:

> "The one miss was the synthetic prompt-injection case. The system returned a more conservative approved action rather than following the malicious instruction, so we kept the real result instead of changing the benchmark to force 100%."

## What not to claim

Avoid saying:

- "ReconPilot proves a service is vulnerable."
- "ReconPilot is immune to prompt injection."
- "The model is always correct."
- "The investigation order is a severity ranking."
- "We successfully exploited ProFTPD."

Use:

- "recommended next investigation step"
- "trusted vulnerability-reference checking"
- "appears vulnerable"
- "workflow guidance"
- "layered prompt-injection mitigation"
- "human approval"

## Backup plan if the live demo fails

If Ollama or the VM fails during the presentation:

1. Do not spend several minutes troubleshooting.
2. Show the saved GUI screenshots / report output.
3. Explain the same MySQL and ProFTPD examples.
4. Show the evaluation results.
5. Explain that the live demo uses the same frozen team baseline already documented in the project evidence.

The goal is to demonstrate the product and design decisions, not prove that a VM can boot on command.

## Likely questions

### Why use an LLM if Python controls so much?

Because the LLM still provides flexible decision support, but the security-sensitive evidence and allowed actions remain deterministic. The project found that giving the model less authority produced safer and more reliable behaviour.

### Why local Ollama?

It keeps scan evidence inside the local environment and gives the team control over the model and API.

### Is ReconPilot replacing Nmap or Metasploit?

No. Nmap remains the reconnaissance evidence source and Metasploit can be used later for authorised validation. ReconPilot helps interpret the evidence and guide the next investigation step.

### Why Qwen2.5 3B?

It performed slightly better and faster on the project's small controlled benchmark. The project treats it as the stronger current candidate, not as universally superior.

### What is the main limitation?

The prototype guides investigation but does not independently verify every vulnerability. Broader test environments, larger evaluation sets and independent usability testing would be needed for a production-level system.

## Final closing line

> "ReconPilot shows that a local LLM can add useful guidance to traditional reconnaissance without giving the model control of the evidence, the scope or the final decision."
