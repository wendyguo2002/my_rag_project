# ProofBlocks Project

## ProofBlocks Summary

I worked on PrairieLearn's Proof Blocks in a research project with Professor Omar. ProofBlocks is a PrairieLearn module where students construct proofs by selecting and ordering predefined logical statements, allowing automated checking of proof structure and common error patterns. The tool lets students build proofs step by step, but it struggled when steps were out of order—this tool just said 'this step is incorrect' to students with no guidance. To improve the feedback system, I added a tagging system so instructors could label blocks by role and attach custom feedback for specific orderings. That way, if a student proves B before A, they see a targeted hint instead of a dead end. I updated the Python backend and Mustache templates, documented the workflow, and opened a PR. After review, Professor Poulsen merged it and it ran in Omar's Discrete Math class. We fine-tuned an open-source language model on thousands of annotated proof attempts, and deployed it for 15 TAs handling 2,500+ weekly submissions. The result was a 30% reduction in repetitive grading while maintaining feedback quality.

## Q&A

### Q1: "What do you mean by 'hierarchical tag-based taxonomy'? What were the 48 proof patterns and 12 error types?"

"To give good feedback, the system needed to understand what the student was trying to do and where they went wrong.

So I created a classification system. The 48 proof patterns were common proof structures—things like proof by induction, proof by contradiction, proof by cases, direct proof. Within induction, there were sub-patterns like strong induction, structural induction, and so on. That's the hierarchical part.

The 12 error types were common mistakes we saw repeatedly: forgetting the base case, incorrect inductive hypothesis, logical gaps in reasoning, circular arguments, that kind of thing.

When a student submitted a proof, the system would identify 'This looks like proof by induction' and 'They made an error with the inductive step.' Then it could pull relevant hints for that specific combination. A student struggling with the base case gets different feedback than one who has a logical gap in their reasoning."

### Q2: "Why did you choose Llama-3-8B? Why fine-tune instead of using the model directly?"

We chose Llama-3-8B for a few reasons. First, it's open-source, so we could fine-tune it and deploy it ourselves without per-API-call costs—important when you're processing 2,500+ submissions weekly. Second, the 8B parameter size was a good balance: powerful enough to understand mathematical reasoning, but small enough to run with reasonable latency.

As for fine-tuning versus using it directly—the base model knew general math, but it didn't know our specific course material, our notation, or what makes good feedback for a student learning proofs. When we tried prompting the base model, the feedback was too generic: 'Check your logic.' Not helpful.

By fine-tuning on 5,000 annotated proof attempts where TAs had written good feedback, the model learned what helpful, specific feedback looks like for our context. After fine-tuning, it would say things like 'Your inductive hypothesis assumes P(k), but you need to show P(k+1) follows—you've only restated the hypothesis.' Much more actionable.

### Q3: "How did you evaluate the model's feedback? What does '85% feedback relevance' mean?"

"Just because a model generates fluent text doesn't mean the feedback is actually helpful.

So I built an evaluation harness that tracked three metrics:

Relevance was the main one—does the feedback address the actual error the student made? We had TAs rate samples on a scale, and 85% of the feedback was rated as relevant and helpful.

Latency mattered for user experience—students expect quick responses. We tracked response time to make sure it stayed under acceptable thresholds.

Coherence measured whether the feedback was clear and well-structured, not rambling or contradictory.

We ran this evaluation continuously, not just once. If relevance dropped—maybe due to a new type of assignment the model hadn't seen—we'd know immediately and could add more training data for that pattern."

### Q4: "You mentioned a 25-page deployment guide. What was in it?"

"The system was only useful if TAs actually adopted it. So I wrote comprehensive documentation covering:

For TAs: How to interpret the system's feedback suggestions, when to override them, how to flag bad suggestions so we could improve the model.

For instructors: How to add new assignment types, how to update the taxonomy if new proof patterns came up, how to monitor feedback quality.

For future developers: System architecture, how to retrain the model with new data, how to add new error types.

I also ran workshops walking TAs through the system. A tool nobody understands is a tool nobody uses. The documentation and training were as important as the technical work for actually achieving that 30% reduction in grading time."

### Q5: "How did you scale this to handle 2,500+ weekly submissions?"

A few things made scaling possible. First, the model choice. Llama-3-8B is small enough to run efficiently. We quantized it to reduce memory usage and batched multiple submissions together for inference.

Second, we didn't need real-time responses. Students submit proofs and check back later, so we could process submissions in a queue. During peak times—like right before deadlines—submissions queued up and processed over a few hours rather than instantly. Students still got feedback same-day.

Third, we cached common feedback patterns. If the system recognized a very common error—like a specific misconception about induction—it could retrieve pre-generated feedback instead of running inference every time.

The system handled the 2,500 weekly submissions comfortably, even during peak deadline times.

### Q6: "What was the 'synthetic augmentation' you mentioned?"

"We had 5,000 real student proof attempts with TA feedback, but that wasn't enough data for all the pattern-error combinations. Some error types were rare—maybe we only had 20 examples of circular reasoning in induction proofs.

So we augmented the dataset synthetically. We took existing proofs and systematically introduced variations: rephrasing the same error in different ways, combining different proof patterns with different error types, generating slightly different versions of the same mistake.

This helped the model generalize better. Instead of memorizing specific proofs, it learned to recognize the underlying patterns and error types even when the wording was different."

### Q7: "Why Llama-3-8B specifically? Why not GPT-4 or a smaller model?"

"It came down to three factors: cost, control, and capability.

GPT-4 would have been expensive at our scale—2,500+ submissions per week adds up quickly with per-token pricing. We also wanted to fine-tune on our specific data, which you can't do with closed models like GPT-4.

Smaller models like Llama-7B or Mistral-7B were options, but we found the 8B parameter size hit a sweet spot. It was large enough to understand mathematical reasoning and generate coherent feedback, but small enough to run efficiently.

Being open-source meant we could fine-tune it, deploy it ourselves, and not worry about API costs scaling with usage."

### Q8: "How did you fine-tune the model? What was the process?"

"The process had a few stages. First, data preparation. We took our 5,000 annotated proof attempts and formatted them as instruction-response pairs: 'Here's a student proof with these errors, generate helpful feedback.' We also added the synthetic augmented data to fill gaps.

Then we fine-tuned using LoRA—Low-Rank Adaptation. Instead of updating all 8 billion parameters, LoRA trains small adapter layers that modify the model's behavior. This is much faster and uses less memory than full fine-tuning.

We trained for a few epochs, monitoring loss on a validation set to avoid overfitting. The whole training process took maybe 6-8 hours on a GPU.

After training, we merged the LoRA weights back into the base model for efficient inference."

#### Follow-up - "What is LoRA?"

"LoRA is a technique where instead of fine-tuning all model weights, you freeze the original model and train small additional matrices that adjust its behavior. It's much more efficient—we could fine-tune on a single GPU instead of needing multiple expensive ones. The quality is nearly as good as full fine-tuning for most use cases."

### Q9: "Did you consider using an API like OpenAI instead of self-hosting?"

We considered it, but self-hosting made more sense for us. Cost was the main factor. At 2,500 submissions per week, API calls would cost hundreds of dollars monthly. Our GPU server was a one-time investment that paid off over the semester.

Fine-tuning was another factor. We needed the model to understand our specific notation, course material, and feedback style. You can't fine-tune GPT-4.

Privacy also mattered. Student work stayed on university infrastructure instead of going to a third-party API.

The trade-off was more operational complexity—we had to manage the server, handle updates, monitor performance. But for a research project with specific requirements, it was worth it.
