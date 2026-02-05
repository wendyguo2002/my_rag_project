# HoloLens Project

## HoloLens Project Summary

Our goal was to build a real-time radiation visualization system for HoloLens 2 that researchers could use in the field. The main challenge was latency—the existing pipeline had about 10 milliseconds of delay, which caused noticeable lag in the AR display.

I focused on streamlining the backend data path to cut down overhead and make the system more predictable in real time. That mainly meant pushing the most performance-sensitive parts closer to C-level execution and cleaning up how data flowed from ingestion through serialization into Unity. At the same time, I added lightweight profiling to track timing drift and synchronization issues across the network boundary.

With those changes, we brought end-to-end latency down from around 10 milliseconds to under 1 millisecond, sustained throughput above 10,000 events per second, and were able to support stable, real-time waveform visualization on HoloLens.

## Q&A

### Q1: "What do you mean by 'events'? What data were you processing?"

Good Answer:

"Each 'event' is a radiation detection—when a particle hits the detector, it generates data: energy level, timestamp, detector position, and waveform characteristics.

The backend needed to:
1. Parse raw detector data
2. Extract features from the waveform
3. Classify the event type (different radiation signatures)
4. Package it for transmission to Unity/HoloLens

At 10,000+ events per second, each step needed to be extremely efficient."

### Q2: "You mentioned rewriting code in Cython. What is Cython and why did you use it?"

"Cython is basically a way to turn Python code into C-speed code by adding type annotations and compiling it. In our HoloLens pipeline, we had a wave-analysis function that ran over a hundred thousand times per file, and pure Python was just too slow and blocked parallelism. We rewrote that inner loop in Cython so it runs as compiled code, avoids the GIL, and behaves much closer to our Rust implementation, while still keeping the rest of the system in Python. That gave us a big speedup without sacrificing development flexibility."

### Q3: "How did you identify which code to optimize? What was your process?"

We started by profiling the pipeline end-to-end to see where time was actually going, instead of guessing. That showed one wave-analysis function being called over a hundred thousand times per file and dominating runtime. We then compared Python output step-by-step against the Rust implementation to make sure the logic was correct before optimizing anything. Once we were confident it was a true hotspot, we isolated just that inner loop and rewrote it in Cython, rather than changing the whole system. That way we got the speedup where it mattered most without risking regressions elsewhere.

### Q4: "What was the clock drift bug? How did you fix it?"

"The backend timestamped events using system time. The HoloLens had its own clock. Even small differences—50 milliseconds—caused events to render at wrong times, making the visualization jump around.

The fix was using relative timestamps. Instead of absolute time ('10:45:32.123'), we sent time relative to a synchronized start point ('event occurred 5.234 seconds after stream started'). Both systems agreed on when the stream started, so relative timing stayed accurate."

### Q7: Walk me through your debugging process for the incorrect visualizations.

"So the problem was that what operators were seeing in the HoloLens didn't match reality—radiation sources were showing up in the wrong positions, and the intensity levels were off.

The tricky part was that data flowed through several systems: from the detector to our Python backend, then over TCP to Unity, and finally to the HoloLens display. The bug could be anywhere in that chain.

My first step was to add logging at each stage so I could see exactly what the data looked like as it moved through the pipeline. I logged the raw detector data, what our backend parsed, what we sent over TCP, and what Unity received.

Once I had that visibility, I compared the data stage by stage. Everything looked fine until the TCP-to-Unity boundary—that's where the numbers started going wrong.

Turns out there were two issues. First, our backend and the HoloLens had different clock references, so timestamps were off and events appeared at the wrong times. Second, we were sending coordinates in meters, but Unity expected centimeters—so everything was 100x smaller than it should be.

Pretty simple bugs in hindsight, but without systematically tracing the data through each stage, I would've been guessing for days. After fixing them, I built a small test harness that sends known values through the pipeline and verifies they come out correctly. That way we'd catch any regressions immediately."

### Q8: Challenge

#### Option A - Performance (Recommended based on your notes)

"Getting under the latency threshold was harder than I expected. I thought I could just use Numba—it's a library that compiles Python to machine code with minimal changes. It helped, but not enough. We were still too slow.

So I made the decision to rewrite the critical sections in Cython. That wasn't easy because it meant rewriting a large portion of the codebase—not just adding a decorator like with Numba. I had to think about memory management, eliminate Python objects from the hot loops, and make sure I wasn't accidentally calling back into Python anywhere.

Even my first Cython version was only about 3x faster. I had to go through several rounds of profiling, optimizing, and measuring again. Each time I'd find another place where Python overhead was sneaking in—maybe a function call that looked innocent but was actually going through Python's call mechanism.

It took probably two weeks of iteration to finally hit the sub-millisecond target. The lesson was that performance optimization is rarely a one-shot fix. You have to measure, improve, measure again, and keep going until you get there."

#### Option B - Debugging

"The visualization bugs were the most frustrating part. The symptom was just 'it looks wrong'—positions were off, intensities seemed incorrect, but it wasn't consistent enough to easily reproduce.

I couldn't just compare input and output because the data went through so many stages: detector to Python backend, backend to TCP stream, TCP to Unity, Unity to HoloLens. The bug could be anywhere.

What finally worked was adding checkpoints at each stage. I logged what the data looked like after parsing, after serialization, after deserialization in Unity. Then I could compare stage by stage and see exactly where the values started going wrong.

It took time to build that instrumentation, but it was the only way to systematically find the issues. Once I had visibility, the actual bugs—clock drift and unit conversion—were straightforward to fix.

The lesson I took away: when you're debugging a distributed system, invest in observability first. Don't guess—add the logging and checkpoints so you can actually see what's happening."
