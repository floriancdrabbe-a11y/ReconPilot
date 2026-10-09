# ReconPilot

**ReconPilot** is an AI-assisted reconnaissance guidance prototype developed for the UTS Cybersecurity Capstone Studio by Team C15.

It takes evidence from an authorised **Nmap XML scan**, converts it into structured evidence, asks a **local Ollama model** to select from a restricted set of approved next actions, validates the model response in Python, and presents guided advice for **human review**.

> **Authorised lab use only.** ReconPilot is a university proof of concept for controlled environments such as Metasploitable. It does not automatically authenticate, exploit, or modify a target.

---

## The problem

Nmap can identify open ports, services, products and versions, but less-experienced testers can still struggle to decide what evidence matters and what should be investigated next.

ReconPilot sits between **reconnaissance output** and the tester's next decision. It does not replace Nmap, Metasploit or human judgement.

---

## How it works

```text
Nmap Scan
   ↓
XML
   ↓
Python Parser
   ↓
Structured Evidence
   ↓
Local Ollama LLM
   ↓
Python Validation
   ↓
Guided Recommendation
   ↓
Human Review
```

The Python layer remains the source of truth for the original scan evidence. The LLM is deliberately given a narrow role: choose an approved next action and confidence value.

---

## Main features

- Upload and analyse authorised Nmap XML
- Extract target, port, protocol, service, product, version and banner evidence
- Local Ollama integration
- Support for `qwen2.5:3b` and `llama3.2:3b`
- Context-aware approved action list
- Structured model output
- Python validation before recommendations are accepted
- Target-controlled scan fields treated as untrusted data
- Guided support explaining:
  - what was found
  - what to do next
  - what to look for
  - why the step helps
  - what to record
  - when to stop for approval
- Streamlit dashboard
- JSON and text report export

---

## Safety design

ReconPilot uses layered controls rather than relying on prompt wording alone.

1. **Authorised scope** — designed only for controlled lab targets.
2. **Evidence preservation** — original Nmap evidence is kept by Python.
3. **Untrusted-data handling** — service names, versions and banners are treated as data, never instructions.
4. **Restricted actions** — the model can only choose from context-appropriate approved actions.
5. **Structured output** — unrestricted commands are not accepted.
6. **Python validation** — returned actions are checked before display.
7. **Human approval boundary** — ReconPilot stops before active authentication, exploitation or modification.

The prompt-injection testing in this project demonstrates mitigation of a documented synthetic case. It does **not** claim that ReconPilot is immune to prompt injection.

---

## Current models

- **Qwen2.5 3B** — default model in the current team baseline
- **Llama 3.2 3B** — available alternative

Qwen performed better on the project's small automated benchmark, but this is treated as a result for this workflow rather than proof that Qwen is universally better.

---

## Quick start

### 1. Requirements

- Python 3
- Nmap
- Ollama
- Streamlit
- An authorised lab target
- A supported local model

Install the Python dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pull a supported model:

```bash
ollama pull qwen2.5:3b
```

or:

```bash
ollama pull llama3.2:3b
```

### 2. Create an authorised Nmap XML scan

```bash
nmap -sV -oX testscan.xml <AUTHORISED_TARGET_IP>
```

### 3. Run the command-line baseline

```bash
python3 reconpilot_team_baseline.py testscan.xml
```

Choose another model:

```bash
python3 reconpilot_team_baseline.py testscan.xml --model llama3.2:3b
```

If Ollama is running at a different address:

```bash
python3 reconpilot_team_baseline.py testscan.xml --ollama-url http://<OLLAMA_HOST>:11434/api/generate
```

The current lab baseline defaults to:

```text
http://172.28.128.1:11434/api/generate
```

### 4. Run the Streamlit GUI

```bash
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

The GUI allows the user to upload Nmap XML, choose a model, analyse the scan, review validated recommendations and export JSON/text reports.

---

## Current validated baseline

The team-integrated baseline was run against an authorised Metasploitable scan with **7 open services**.

End-to-end result:

- **7 services analysed**
- **7 validated recommendations**
- **0 rejected outputs**

The workflow placed exact-version services such as ProFTPD, OpenSSH and Apache into trusted-reference checking, while incomplete evidence such as MySQL with no exact version was directed back into information gathering.

### 10-case evaluation

| Metric | Result |
|---|---:|
| Schema validity | 10/10 (100%) |
| Safety | 10/10 (100%) |
| Recommendation relevance | 9/10 (90%) |
| Evidence fidelity | 10/10 (100%) |
| Guidance completeness | 10/10 (100%) |
| Automated usefulness proxy | 9/10 (90%) |
| Average response time | 3.393 s |
| Synthetic prompt-injection case | Passed |

The only relevance miss was the synthetic prompt-injection case, where the model returned a conservative `request_more_evidence` action instead of the benchmark's expected action. It remained inside the approved action set and was not treated as a safety failure.

---

## Practical recommendation validation

One ReconPilot recommendation was checked independently in the authorised Metasploitable lab:

```text
Nmap
→ ProFTPD 1.3.5 detected on port 21

ReconPilot
→ Check trusted vulnerability references

Metasploit
→ Matching ProFTPD mod_copy module / CVE-2015-3306

Metasploit check
→ The target appears to be vulnerable
```

The exploit itself was **not** run. This demonstrates that the ReconPilot recommendation led to a technically relevant next investigation step without claiming that ReconPilot itself proved exploitation.

---
---

## Project files

```text
ReconPilot/
├── app.py
├── reconpilot_team_baseline.py
├── requirements.txt
├── README.md
├── PRESENTATION.md
└── .gitignore
```

---

## Team integration

The current team baseline combines contributions including:

- **Ahmed** — dynamic scan-file handling and parser repeatability work
- **Eklal** — all-in-one workflow structure, all-open-port processing, error handling and consolidated reporting
- **Florian** — context-aware allow-list, prompt-injection hardening, reduced LLM authority, guided support, evaluation, human-approval boundary, integration and GUI
- **Isaac** — independent Teach-the-Team reproduction and workflow validation

Additional testing and documentation contributed to the overall Team C15 delivery.

---

## Limitations

ReconPilot is a proof of concept, not a production penetration-testing platform.

- A validated recommendation does not prove that a target is vulnerable.
- The current automated benchmark contains 10 cases.
- Prompt-injection testing covers a documented synthetic case rather than every possible attack.
- The end-to-end parser tests are based mainly on the authorised project lab environment.
- The manual guidance review was initially a self-review rather than a formal usability study.
- Further independent testing and broader environments would be needed before stronger claims could be made.

---

## Academic project

**UTS Cybersecurity Capstone Studio — Team C15, 2026**

ReconPilot is intended to demonstrate how a local LLM can support reconnaissance while keeping evidence, safety controls and human oversight outside the model.
