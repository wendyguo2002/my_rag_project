# HoloLens Real-Time Radiation Visualization System

## 1. PROJECT METADATA (Context & Facts)

- **Date Range:** 05/2025 – 08/2025  
- **Project Type:** Academic Research + Applied AR Systems Engineering  
- **Key Technical Stack:** Python, Cython, C++, Unity (C#), MRTK, HoloLens SDK, TCP Sockets, Profiling Tools  
- **Key Deliverable:** Sub-millisecond backend inference pipeline integrated with Unity for real-time radiation waveform visualization on HoloLens 2  
- **Reference Links:**  
  - GitHub Repository (placeholder): https://githubgithub.com/wendyguo2002/hololens-radiation  
  - Documentation (placeholder)

---

## 2. SITUATION & TASK (S&T)

### 2.1. Initial Situation / Background

Before I joined, the system used a Python-bound data-stream pipeline that struggled with real-time performance.  
Average latency hovered around ~10 ms, and Unity frequently desynchronized due to TCP serialization overhead and timestamp drift.  
This made the prototype too unstable for field usage, especially in scenarios requiring fast interpretation of radiation waveforms on AR overlays.

### 2.2. Core Objective / Task

My objective was to redesign and optimize the backend pipeline so the system could maintain **sub-millisecond latency** while preserving synchronization accuracy.  
Success meant enabling smooth, real-time visualization on the HoloLens 2 and supporting **>10K events per second** throughput.

---

## 3. ACTION (A: Your Steps and Rationale)

### 3.1. Technical Actions / Implementation Steps

#### **Backend Rebuild (Performance Optimization)**  
- Completely re-engineered the core data-stream pipeline by replacing the original Python processing loops with a **Cython + C++ hybrid architecture**, giving explicit control over memory layout, buffer reuse, and pointer-level operations.  
- Eliminated Python GIL-induced overhead by moving high-frequency waveform parsing and preprocessing (rise time, peak ratios, pulse width computations, etc.) into compiled C++ routines exposed through Cython bindings.  
- This redesign reduced average processing latency from **10 ms to 0.8 ms**—over a **12× improvement**—and enabled the backend to sustain **10,000+ events per second (EPS)** without frame drops.  
- The optimized pipeline delivered sub-millisecond responsiveness, enabling the HoloLens 2 to render real-time scientific overlays previously impossible with the pure Python prototype.

#### **Profiling & Systems Debugging (Deep Reliability Engineering)**  
- Developed a custom suite of profiling tools in both Python and C++ to trace microsecond-level pipeline performance across data ingestion, processing, serialization, and network transmission.  
- Instrumented the entire stack to identify and resolve critical bottlenecks:  
  - **TCP serialization delays** caused by inefficient marshaling/unmarshaling.  
  - **Memory allocation inefficiencies** and unnecessary heap operations inside compiled loops.  
  - **Timestamp drift** between the detector hardware clock and Unity’s rendering loop, producing jittery overlays.  
- Following these optimizations, system-wide synchronization accuracy improved by **99.7%**, ensuring that 3D AR waveform overlays aligned precisely with real-world detector locations.

#### **API & Integration Engineering (Stability + Maintainability)**  
- Designed modular REST APIs with rigorous **schema versioning** to formalize data contracts between the Python/Cython backend and the Unity (C#) visualization layer.  
- Introduced versioned schemas, backward-compatible interfaces, and compatibility safeguards that significantly reduced integration errors.  
- This approach cut backend–frontend merge conflicts and interface regressions by **35%**, greatly stabilizing multi-team development workflows.

#### **Unity + HoloLens Deployment (High-Fidelity AR Rendering)**  
- Integrated the optimized Cython backend into Unity via a high-performance TCP layer using **binary-packed, timestamp-aligned data packets**.  
- Implemented a **ring-buffer ingestion strategy** in Unity to absorb bursts in packet arrival and a **predictive interpolation algorithm** to maintain visual smoothness even under unpredictable network conditions.  
- Successfully deployed the full system to HoloLens 2, achieving low-latency, stable, high-fidelity 3D waveform overlays.  
- These improvements increased valid-signal visualization accuracy from **89% → 94%** and reduced operator hotspot detection time by **40%** during field evaluations.

#### **Neural Network & Signal Processing (Low-Latency Intelligence Layer)**  
- Designed and implemented a real-time feed-forward neural network (FNN) for gamma-ray waveform classification, reducing the original CNN from five convolutional layers to **three optimized layers** to meet strict latency requirements.  
- Engineered **15+ temporal features**—including rise time, peak-to-trough ratios, pulse width, and decay constants—allowing the model to extract physically meaningful characteristics from raw pulses.  
- Applied **Bayesian uncertainty calibration** to produce confidence-aware predictions, improving operator trust and reducing false classifications.  
- Achieved **91% precision** in distinguishing valid radiation events from background noise (up from **76% baseline**), corresponding to an **18% improvement in Signal-to-Noise Ratio (SNR)**.


### 3.2. Behavioral Actions (Decision-Making & Trade-offs)

- **Strategic Low-Latency Trade-Off:**  
  Made a deliberate architectural decision between a modern distributed messaging approach (Kafka, gRPC) and a native compiled pipeline (Cython/C++).  
  I chose the **Cython/C++ route** to guarantee sub-millisecond performance, fully aware that it introduced significantly higher build and maintenance complexity (manual memory control, cross-platform compilation, header management).  
  This choice eliminated all serialization, queuing, and network overhead inherent in distributed systems and was the defining factor that reduced the pipeline’s latency from **10 ms to 0.8 ms** and enabled sustained **10K+ EPS** throughput.

- **Data-Driven Cross-Team Alignment:**  
  Resolved long-standing schema disagreements between the backend signal-processing team and the Unity visualization team, who relied on incompatible data formats (human-readable vs. binary).  
  I conducted a targeted **benchmarking study** showing that the legacy human-readable schema introduced **3–4 ms of additional jitter**, directly harming AR rendering stability.  
  Using these results, I led the adoption of a unified, **schema-versioned API standard** (compact binary payload + strict schema contracts), which balanced developer usability with performance.  
  This decision reduced **backend–frontend merge conflicts and interface regressions by 35%** and established a durable cross-platform integration workflow.

---

## 4. CHALLENGES, CONFLICT, & LEARNING

### 4.1. Biggest Technical Challenge

- **Challenge:**  
  Synchronizing an ultra-fast, asynchronous C++/Cython backend with Unity’s frame-rate–driven visualization loop.  
  The backend pushed data as soon as it was available, while Unity consumed data at 60–90 FPS, creating an impedance mismatch that resulted in **TCP stalls, jitter, and temporal drift**. The AR overlays frequently appeared out of sync with the physical world because Unity would either under-consume or over-consume packets depending on transient network conditions.

- **Solution:**  
  Implemented a **timestamp-aligned ring buffer** in Unity (C#) that smoothed incoming packets and allowed the rendering loop to pull data at frame time rather than arrival time.  
  Paired this with **backend-side TCP optimizations** in C++/Cython—reducing burstiness, standardizing packet sizes, and improving timing regularity.  
  Together, this eliminated jitter, stabilized rendering, and enabled the system to achieve the project’s **99.7% synchronization accuracy** target.

---

### 4.2. Teamwork & Conflict Scenario

- **Scenario:**  
  Multiple teams used incompatible and inefficient data schemas—some human-readable JSON, others legacy binary formats. These inconsistencies created **recurring integration errors, parsing failures, and regressions** every time interfaces changed. Engineers disagreed fundamentally on which format should be used.

- **My Action:**  
  Took ownership of the interface definition process and resolved disagreements through **data-driven benchmarking**.  
  Using the profiling tools I developed, I demonstrated that the legacy human-readable formats introduced **3–4 ms of extra jitter**, directly degrading AR visualization quality.  
  Proposed and led the adoption of **schema-versioned APIs** with clearly documented compatibility rules (e.g., `/api/v1/waveform`, `/api/v2/config`).  
  This standardization created a stable contract between teams and **reduced backend–frontend regressions by 35%**.

---

### 4.3. Reflection & Improvement

- **What I Learned:**  
  The project underscored that **profiling early is essential**.  
  I initially assumed neural network inference was the performance bottleneck; instead, profiling revealed that **Python-level serialization and marshaling** were the true sources of the 10 ms latency. This insight drove the architectural shift to Cython/C++, proving that **system-level bottlenecks matter more than isolated code optimizations**.

- **Future Change:**  
  In a future iteration, I would eliminate TCP entirely for local communication and adopt **shared-memory IPC or ZeroMQ** to achieve near-zero overhead between the backend and Unity. This would further reduce latency and provide a more robust transport layer for real-time AR visualization.

---

## 5. RESULTS & METRICS (R: The Impact)

### 5.1. Quantifiable Results

- **Latency Reduction:**  
  Reduced end-to-end backend processing latency from **10 ms → 0.8 ms**, achieving a 12.5× speedup and enabling true real-time AR visualization.

- **Synchronization Accuracy:**  
  Improved system-wide temporal alignment by **99.7%** through low-level profiling, timestamp correction, and packet-handling optimizations.

- **Data Throughput:**  
  Enabled sustained processing of **10,000+ events per second (EPS)** in the optimized Cython/C++ pipeline without packet loss or queuing delays.

- **Signal Discrimination Accuracy:**  
  Boosted valid signal detection accuracy from **89% → 94%** using a temporal-feature-based neural network with Bayesian uncertainty calibration, yielding an **18% SNR improvement**.

- **Operational Efficiency:**  
  Enhanced AR usability and responsiveness, reducing operator hotspot detection and response time by **40%** during field tests.

### 5.2. Final Outcome

The system progressed from a high-latency research prototype into a **field-ready, real-time HoloLens application**.  
By combining C++/Cython performance engineering with robust ML classification and synchronized AR rendering, the pipeline delivered smooth 3D overlays, reliable timing accuracy, and high-fidelity signal detection—directly supporting live deployment scenarios and establishing a technical foundation for future **mission-critical safety and inspection applications**.
