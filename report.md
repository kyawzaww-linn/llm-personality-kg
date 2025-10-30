# Report: Personality Knowledge Graph Generation via LLM Workflow

### 1. Introduction & Objective

This report outlines the design, implementation, and evaluation of a Python solution that builds a knowledge graph (KG) from text documents. The primary objective was to not only extract entities and relationships but to specifically model the **personality of subjects** within the graph in a structured and verifiable way.

This project was developed by leveraging a Large Language Model (LLM) as a tool for research, code generation, and workflow execution, per the assessment guidelines.

---

### 2. Design Choices

The architecture of the solution was based on several key design decisions, justified below.

**2.1. KG Modeling Approach: Evidence-Based Triples**
The core challenge was representing personality. We chose an **evidence-based modeling approach**. Instead of directly linking a subject to a trait (e.g., `Kyaw -> Conscientious`), our graph introduces an intermediary "evidence" node.

The final structure is a chain of two triples:
1.  `(Subject) --[exhibits]--> (Behavior/Evidence)`
2.  `(Behavior/Evidence) --[implies]--> (Trait)`

* **Justification:** This design makes the graph **verifiable and transparent**. A user can query the graph and see *why* a subject was assigned a specific trait by tracing it back to the exact behavioral evidence from the source text. This aligns with the assessment's focus on logical thinking.

**2.2. LLM Workflow: Multi-Step Prompt Chain**
A single prompt is insufficient for this complex task. We implemented a **3-step prompt chain** to process each document:

1.  **Subject Extraction:** Identifies all human names (e.g., "Kyaw").
2.  **Behavior Extraction:** For each subject, extracts specific, observable behaviors (e.g., "triple-checked [the spreadsheet] for errors").
3.  **Trait Inference:** For each behavior, infers a standardized personality trait.

* **Justification:** This chain breaks the problem down, improving reliability. It also allows for **error isolation**; by evaluating each step's output, we can pinpoint which part of the workflow needs improvement.

**2.3. Personality Framework: The "Big Five" (OCEAN)**
To avoid an inconsistent graph (e.g., "shy," "introverted," "quiet"), we standardized the trait inference step.

* **Justification:** The **Big Five (OCEAN) model** (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) is a scientifically validated and well-defined framework. Using it as the target for our "Trait Inference" prompt ensures all behaviors are mapped to a consistent, limited set of nodes, making the final KG far more powerful for queries and analysis.

**2.4. Data Handling and Output**
* **Synthetic Data:** As real data was unavailable, we generated 5 synthetic text documents. These documents were designed to describe *behaviors* rather than stating traits, providing a good test for the LLM's inference capabilities.
* **Structured Output:** All prompts were engineered to return **JSON objects**. This is a critical design choice for robustness, as it allows the Python script to reliably parse the LLM's output and feed it into the next step of the chain or the graph library.

---

### 3. Insights and Observations

* **Prompt Engineering is Key:** The success of the entire system hinges on the precision of the prompts. Forcing JSON output and giving the LLM a clear "role" (e.g., "psychological analyst") dramatically improved the quality and consistency of the results.
* **Effectiveness of Chaining:** The multi-step chain proved highly effective on the synthetic data. It successfully identified subjects, extracted their relevant behaviors, and mapped those behaviors to plausible Big Five traits.
* **Verifiability:** The final graph visualization clearly demonstrates the value of the chosen model. The "Kyaw" node does not connect directly to "Conscientiousness"; instead, it connects through his actions, which is a much richer and more accurate representation of the source text.

---

### 4. Limitations and Future Work

This solution, while effective, has several limitations:

* **Subjectivity:** Trait inference is inherently subjective. While "triple-checking work" strongly implies "Conscientiousness," other behaviors might be ambiguous.
* **Cascading Errors:** The linear chain is a vulnerability. If **Step 1** fails to identify a subject, that subject is dropped from the entire analysis. An error in behavior extraction (Step 2) will lead to a missing or incorrect inference (Step 3).
* **Scalability:** The current script makes multiple LLM calls for *each* document. This is slow and would be expensive to run on a large corpus of thousands of documents.

**Future Work:**
1.  **Graph Database:** Implement a proper graph database (like Neo4j) to store and query the triples, rather than just visualizing with `networkx`.
2.  **Error Handling:** Build more robust error handling and retry logic for failed LLM calls or JSON parsing.
3.  **Batch Processing:** Modify the prompts to handle a *batch* of documents or behaviors at once to reduce the number of LLM calls.

---

### 5. Evaluation Strategy

Evaluating a generative system like this is challenging due to the lack of a "ground truth" dataset.

* **Method:** We proposed a **qualitative, rubric-based evaluation**. For each of the 5 synthetic "golden set" documents, we would manually grade the system's output on a 0-10 scale.
* **Rubric:** The rubric evaluates each step of the chain independently (Subject Extraction, Behavior Extraction, Trait Inference), allowing us to assign a score for the quality and relevance of the output at each stage.
* **Justification:** This method is superior to simple accuracy metrics because it pinpoints *where* in the workflow the model is succeeding or failing, providing a clear path for future improvements.
