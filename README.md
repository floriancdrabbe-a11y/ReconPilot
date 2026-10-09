# ReconPilot

**ReconPilot** is a proof-of-concept, AI-assisted reconnaissance helper developed for the UTS Cybersecurity Capstone Studio by Team C15.

The system takes evidence from an authorised **Nmap XML scan**, converts it into structured data, sends a restricted decision task to a **local Ollama model**, validates the returned action in Python, and presents a guided next step for human review.

> **Authorised lab use only.** ReconPilot is designed for controlled cybersecurity training environments such as Metasploitable. It does not automatically authenticate, exploit, or modify a target. Active testing remains a human decision.


## What ReconPilot does

- Accepts Nmap XML produced with `-oX`
- Extracts the target, open ports, protocol, service, product, version, and banner information
- Uses a local Ollama model instead of sending scan evidence to an external AI service
- Restricts the model to context-aware approved actions
- Treats target-controlled scan content as untrusted data
- Validates model output in Python before it reaches the user
- Produces guided support explaining what to do next, what to look for, why it helps, what to record, and when to stop for approval
- Provides both a command-line workflow and a Streamlit GUI
- Exports JSON and text reports

## Architecture

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

The LLM does **not** control the evidence fields or generate unrestricted actions. Python preserves the original scan evidence, creates the context-aware allow-list, validates the structured response, and constructs the guided support around the approved action.

## Current models

ReconPilot currently supports these local Ollama models:

- `qwen2.5:3b` — default model in the current team baseline
- `llama3.2:3b`

In the project benchmark, Qwen2.5 3B was the stronger current candidate for this workflow, but the result should not be interpreted as proving that it is universally the better model.

## Requirements

- Python 3
- Nmap
- Ollama
- One of the supported local models
- Streamlit for the GUI
- An authorised lab target and Nmap XML scan

Install the Python dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pull at least one supported Ollama model on the machine running Ollama:

```bash
ollama pull qwen2.5:3b
```

or:

```bash
ollama pull llama3.2:3b
```

## Ollama connection

The current lab baseline expects Ollama at:

```text
http://172.28.128.1:11434/api/generate
```

This matched the Windows host-only address used in the team's VirtualBox lab. If your Ollama host is different, either change `DEFAULT_OLLAMA_URL` near the top of `reconpilot_team_baseline.py` or use the CLI `--ollama-url` option.

If Ollama is running on Windows and must accept requests from the Kali VM, configure Ollama appropriately for your isolated lab before running ReconPilot.

## Run the CLI

First create an XML scan from an **authorised** target, for example:

```bash
nmap -sV -oX testscan.xml <AUTHORISED_TARGET_IP>
```

Then run ReconPilot:

```bash
python3 reconpilot_team_baseline.py testscan.xml
```

Choose a different model if required:

```bash
python3 reconpilot_team_baseline.py testscan.xml --model llama3.2:3b
```

Use a different Ollama endpoint if required:

```bash
python3 reconpilot_team_baseline.py testscan.xml --ollama-url http://<OLLAMA_HOST>:11434/api/generate
```

The CLI writes:

```text
reconpilot_team_recommendations.json
reconpilot_team_recommendations.txt
```

## Run the Streamlit GUI

```bash
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

The interface lets the user upload Nmap XML, select a local model, analyse the scan, review validated recommendations, inspect guidance/evidence/safety information, and export reports.


## Safety design

ReconPilot uses several layers rather than relying on prompt wording alone:

1. **Authorised-scope design** — intended only for controlled lab targets.
2. **Evidence preservation** — target, port, service, product, version, and banner are taken from the parser/Python layer.
3. **Untrusted-data separation** — service names, versions, banners, and other target-controlled content are treated as data, not model instructions.
4. **Restricted action set** — the model can only select from approved reconnaissance actions that are valid for the available evidence.
5. **Structured output** — the model returns a narrow response rather than unrestricted commands.
6. **Python validation** — returned actions are checked before they are accepted.
7. **Human approval boundary** — ReconPilot stops before active authentication, exploitation, or modification.

## Current validated baseline

The team-integrated baseline was tested against an authorised Metasploitable scan containing seven open services. It produced seven validated recommendations with zero rejected outputs in that end-to-end run.

A separate 10-case team-baseline evaluation recorded:

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

The single relevance miss was a conservative `request_more_evidence` fallback during the synthetic prompt-injection case. It remained inside the approved action set and was not treated as a safety failure.

## Practical recommendation validation

One ReconPilot path was independently checked in the authorised Metasploitable lab:

```text
Nmap → ProFTPD 1.3.5 detected
ReconPilot → Check trusted vulnerability references
Metasploit → Matching ProFTPD mod_copy module / CVE-2015-3306
Metasploit check → Target appears to be vulnerable
```

The exploit itself was **not** run. This validation demonstrates that the recommendation led to a technically relevant investigation step without claiming that ReconPilot itself proved exploitation.

## Project files

```text
ReconPilot/
├── app.py
├── reconpilot_team_baseline.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Team integration

The current baseline combines contributions from Team C15, including:

- Ahmed — dynamic scan-file handling and parser repeatability work
- Eklal — all-in-one workflow structure, all-open-port processing, error handling, and consolidated reporting
- Florian — context-aware allow-list, reduced LLM authority, prompt-injection hardening, Python-generated guided support, evaluation, human-approval boundary, integration, and GUI work
- Isaac — independent Teach-the-Team reproduction and workflow validation

Additional team testing and documentation contributed to the overall capstone delivery.

## Scope and limitations

ReconPilot is a university proof of concept, not a production penetration-testing platform. A validated recommendation means the suggested next investigation step passed the current structural and safety checks; it does **not** prove that a detected service is vulnerable. The current evaluation set is limited, prompt-injection testing uses a documented synthetic case, and broader independent usability testing would be required before stronger claims could be made.

## Academic project

UTS Cybersecurity Capstone Studio — Team C15, 2026.
