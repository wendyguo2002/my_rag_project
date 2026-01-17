# Intelligent Proof Tutoring System (PrairieLearn)

## 1. PROJECT METADATA (Context & Facts)

- **Date Range:** 05/2024 – 01/2025  
- **Project Type:** Educational Infrastructure, AI-Augmented Feedback System  
- **Key Technical Stack:** Python, Flask, Mustache.js, PrairieLearn Core APIs, Llama-3-8B (fine-tuned), Distributed Queue, Docker  
- **Key Deliverables:**  
  - Deterministic proof-feedback engine for 800+ students  
  - Retrieval-based LLM feedback model with 85% relevance  
  - Scalable distributed request queue sustaining <250 ms latency  
- **Reference Links:**  
  - GitHub (placeholder)  
  - Documentation (placeholder)

---

## 2. SITUATION & TASK (S&T)

### 2.1. Initial Situation / Background

Before this project, PrairieLearn’s ProofBlocks system lacked structured, deterministic feedback for proof-based assignments.  
Students often received vague or inconsistent hints, TAs had to manually inspect thousands of attempts, and the feedback system was **not scalable** for multi-course adoption.  
The department wanted a robust, automated system that provided **correct, context-dependent, and pedagogically sound** hints.

### 2.2. Core Objective / Task

My role was to design and deploy an end-to-end proof feedback engine that:

- Identified 48 proof structures and 12 error patterns  
- Served deterministic, rule-based feedback at scale  
- Supported future LLM-based feedback extensions  
- Operated reliably for **800+ concurrent students**

Success required <250 ms latency per request and consistency across all courses.

---

## 3. ACTION (A: Your Steps and Rationale)

### 3.1. Technical Actions / Implementation Steps

#### **Rule-Based Backbone (Python + Mustache.js)**  
- Engineered a deterministic ordering-feedback engine that mapped student steps to canonical proof structures using a Proof Graph Model of nodes (canonical steps) and edges (valid transitions).  
- Implemented pattern matching for **48 structures** and **12 error families** via an AST-driven modular tagging system labeling constructs such as “Axiom Application,” “Modus Ponens,” and error types like “Premise Misuse” or “Circular Reasoning.”  
- Built a declarative Mustache.js frontend that rendered Python-generated JSON payloads into consistent, human-readable feedback templates, fully decoupling logic from presentation.

#### **Distributed Feedback Pipeline (Scalable Worker System)**  
- Built a distributed queue system (Redis/Celery) to route and load-balance submissions across multiple Python workers for fault-tolerant, high-volume processing.  
- Introduced asynchronous workers (asyncio) to maintain **<250 ms latency** during peaks of ~2.5K weekly submissions by minimizing blocking I/O.  
- Added monitoring hooks (Prometheus/Grafana) for real-time failure detection, automatic re-queuing of transient failures, and developer alerts for persistent issues.

#### **LLM-Enhanced Feedback (Llama-3-8B Fine-Tuning)**  
- Fine-tuned a retrieval-based **Llama-3-8B** model on **5K+ annotated attempts**, applying RAG principles to retrieve similar ambiguous proof attempts and generate high-quality explanations.  
- Built a hybrid pipeline where deterministic feedback handled ~90% of cases, and an LLM fallback triggered when the confidence score fell below a threshold (**C < 0.8**) to optimize latency and cost.  
- Increased feedback relevance from **60% → 85% (+25pp)** through A/B testing and student survey evaluations.

#### **Deployment, CI/CD, and Production Rollout**  
- Containerized all services using Docker with multi-stage builds to ensure fast, slim, and secure production deployments.  
- Updated course-level configuration to expose modularized RESTful proof-checking APIs for future assignment integrations.  
- Authored onboarding documentation and TA training materials for **15 TAs**, covering system monitoring, LLM feedback review, and rule-engine extension workflows.


### 3.2. Behavioral Actions (Decision-Making & Trade-offs)

- **Architectural Trade-Off:**  
  Chose a hybrid deterministic + LLM design instead of relying on a purely generative model.  
  The deterministic core guaranteed correctness, interpretability, and strict alignment with the course syllabus, handling ~90% of submissions with zero hallucination risk.  
  The LLM fallback addressed the remaining ~10% of complex or ambiguous cases, balancing precision with flexibility while controlling compute cost.  
  This approach delivered high-relevance feedback without sacrificing reliability.

- **Cross-Team Alignment:**  
  Coordinated closely with faculty, TAs, and PrairieLearn maintainers through weekly syncs to standardize canonical proof structures and acceptable derivations.  
  Produced shared JSON schemas and strict backward-compatibility rules for all proof APIs, ensuring seamless integration with existing assignments and preventing regressions across semesters.

- **Stakeholder Communication & Change Management:**  
  Ran multiple pilot tests and feedback workshops with TAs and students to evaluate clarity, tone, and usefulness of LLM-generated feedback.  
  Accepted a two-week delay to incorporate refinements, including tuning the LLM system prompt for concise, supportive, and pedagogically aligned responses.  
  These actions ensured smooth adoption and improved the perceived helpfulness of the system.

---
## 4. CHALLENGES, CONFLICT, & LEARNING

### 4.1. Biggest Technical Challenge

- **Challenge:**  
  Unifying highly variable student proofs into structured representations without overfitting.  
  Early versions struggled with ambiguity in natural language proofs, unconventional reasoning paths, and multi-step lines, leading to a **15% false-negative rate** where correct proofs were flagged as incorrect.

- **Solution:**  
  Designed a hierarchical tagging system and a flexible rule graph to normalize diverse proof forms into canonical templates.  
  - **Abstract Tagging:** Added a preprocessing layer that converted raw student input into an abstract representation using tags such as `[APPLICATION_MP]`, `[ASSUMPTION_INTRO]`, and `[PREMISE_USED]`, reducing linguistic variability.  
  - **Flexible Rule Graph:** Modeled canonical proofs as a DAG instead of linear sequences, allowing multiple valid transitions between abstract tags and preventing over-rigid pattern matching.  
  - **Confidence Scoring:** Introduced a heuristic score \(C\) to detect uncertain matches; when \(C < 0.8\), the system delegated evaluation to the LLM for nuanced validation.

- **Learning:**  
  Prioritizing **generalization over specificity** is essential for educational feedback systems.  
  By focusing on abstract logical intent rather than surface wording, the system dramatically reduced false negatives and became more robust to student creativity.

### 4.2. Teamwork & Conflict Scenario

- **Scenario:**  
  Faculty disagreed on whether hints should be strict and formal (explicit rule citations) or exploratory and pedagogical (conceptual nudges).  
  One group prioritized rigor and precision, while TAs and another faculty group favored student-centered guidance that reduced frustration.

- **My Action:**  
  Ran a rigorous A/B test across ~500 students per group over three weeks:  
  - Group A received strictly formal hints  
  - Group B received exploratory hints  
  - Group C received hybrid hints (control)  
  Data showed the hybrid style achieved the best outcomes in Time-to-Correction, repeat error reduction, and student satisfaction.  
  Aligned all stakeholders on adopting a mixed hint structure: a conceptual nudge followed by a formal justification.

### 4.3. Reflection & Improvement

- **What I Learned:**  
  AI feedback must be **pedagogically grounded**, not just technically correct.  
  Conceptual nudges drive real learning; formal rule citations are scaffolding, not the teaching mechanism.

- **Future Change:**  
  Add per-student personalization using:  
  - **Historical context:** dynamically highlight recurring weaknesses (e.g., repeated errors in Disjunction Elimination).  
  - **Spaced repetition:** reduce hint detail for previously corrected mistakes to strengthen retention and recall.

---

## 5. RESULTS & METRICS (Impact)

### 5.1. Quantifiable Results

- Supported **800+ students** across Discrete Mathematics and Advanced Logic courses  
- Enabled full departmental adoption of ProofBlocks as the standardized proof-assessment tool  
- Reduced TA grading workload by **30%+** (150+ hours saved per semester)  
- Achieved **85% feedback relevance** with LLM-enhanced hybrid feedback  
- Maintained **<250 ms** end-to-end latency even during 2.5K weekly submission peaks  
- Rule-based core delivered **>99.5% accuracy** on deterministic checks  
- Improved first-attempt proof scores by **+12 percentage points**  
- Reduced student-reported frustration by **40%** in end-of-course surveys

### 5.2. Final Outcome

This project transformed PrairieLearn’s proof assessment into a **scalable, intelligent tutoring system**.  
It now serves as the standard for Discrete Math and other proof-based courses at the University of Michigan, automating routine error detection while delivering personalized, high-quality feedback that mirrors a 1:1 expert tutoring experience.

