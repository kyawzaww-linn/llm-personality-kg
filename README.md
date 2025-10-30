# LLM Personality Knowledge Graph Builder

This project is a Python solution for an assessment, demonstrating the use of a Large Language Model (LLM) to build a knowledge graph (KG) from text. The key feature of this KG is its ability to model the personality of subjects based on behavioral evidence found in the text.

The solution is implemented as a 3-step LLM prompt chain.

## Features

* **Multi-Step LLM Workflow:** Uses a chain of 3 prompts to (1) Extract Subjects, (2) Extract Behaviors, and (3) Infer Personality Traits.
* **Evidence-Based Graph:** The KG links subjects to their *behaviors* (evidence) and then links those behaviors to inferred *traits*, ensuring verifiability.
* **Standardized Personality Model:** Uses the **Big Five (OCEAN)** model for consistent and queryable trait representation.
* **Graph Visualization:** Uses `networkx` and `matplotlib` to generate a visualization of the final KG, saved as a `.png` file.

## Setup and Installation

1.  Clone this repository to your local machine.
2.  Install the required Python libraries:

    ```bash
    pip install google-generativeai networkx matplotlib
    ```

## Configuration

This script uses the Google Gemini API. You must configure your API key.

1.  Open the `kg_builder.py` file.
2.  Find the line:
    `genai.configure(api_key="YOUR_API_KEY")`
3.  Replace `"YOUR_API_KEY"` with your actual Google AI Studio API key.

    (Alternatively, you can set it as an environment variable named `GEMINI_API_KEY`.)

## Execution

The script is designed to run from your terminal. The 5 synthetic test documents are hard-coded into the `main()` function.

1.  Navigate to the project directory in your terminal.
2.  Run the script:

    ```bash
    python kg_builder.py
    ```

## Results

When you run the script, it will:
1.  Print the processing steps for each of the 5 documents to the console.
2.  Generate a final knowledge graph image named `knowledge_graph_all_docs.png` in the same directory.

### Example Output Graph


---
*This project was completed with the assistance of an LLM, as per the assessment requirements.*
