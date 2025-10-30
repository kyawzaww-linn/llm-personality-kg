import google.generativeai as genai
import json
import os
import re
from typing import List, Dict, Any

# --- NEW IMPORTS ---
import networkx as nx
import matplotlib.pyplot as plt

# --- Configuration ---
# TODO: REPLACE "YOUR_API_KEY" WITH YOUR ACTUAL API KEY
# (You can also set it as an environment variable)
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except TypeError:
    print("API Key not found as environment variable. Using placeholder.")
    # Fallback for testing - replace this
    genai.configure(api_key="YOUR_API_KEY") 

try:
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error initializing model. Is your API key set correctly? Error: {e}")
    exit()

def clean_json_response(raw_text: str) -> Any:
    """Helper function to clean LLM response and extract JSON."""
    # Find the JSON block, even if wrapped in markdown
    json_match = re.search(r"```json\n(.*?)\n```", raw_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Fallback if no markdown is found, assumes raw JSON
        json_str = raw_text.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw text that failed parsing: {raw_text}")
        return None

# --- PROMPT 1 FUNCTION ---
def extract_subjects(text_document: str) -> List[str]:
    """Extracts human names (subjects) from a text document."""
    system_prompt = "You are an expert entity extraction system. Your task is to identify and list all human names (subjects) from the given text."
    user_prompt = f"""
    Text:
    '''
    {text_document}
    '''
    Extract all subjects. Format your response as a JSON object with a single key `subjects`, 
    which contains a list of the names. If no subjects are found, return an empty list.
    """
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        response = model.generate_content(full_prompt)
        data = clean_json_response(response.text)
        return data.get('subjects', []) if data else []
    except Exception as e:
        print(f"Error in extract_subjects: {e}")
        return []

# --- PROMPT 2 FUNCTION ---
def extract_behaviors(text_document: str, subject_name: str) -> List[str]:
    """Extracts observable behaviors for a specific subject."""
    system_prompt = "You are a psychological analyst and text expert. Your task is to extract observable behaviors or actions for a specific person from a text."
    user_prompt = f"""
    Full Text:
    '''
    {text_document}
    '''
    Subject: **{subject_name}**
    Extract all specific, observable behaviors or actions attributed *only* to **{subject_name}**. 
    Focus on *what they did*, *said*, or *how they acted*. These will be used as evidence.
    Format your response as a JSON object with a single key `behaviors`, 
    which contains a list of strings.
    """
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        response = model.generate_content(full_prompt)
        data = clean_json_response(response.text)
        return data.get('behaviors', []) if data else []
    except Exception as e:
        print(f"Error in extract_behaviors: {e}")
        return []

# --- PROMPT 3 FUNCTION ---
def infer_trait_from_behavior(behavior_text: str) -> Dict[str, str]:
    """Infers a Big Five personality trait from a single behavior."""
    system_prompt = (
        "You are an expert psychological analyst. Your task is to infer a primary "
        "personality trait from a specific behavior, based on the Big Five (OCEAN) model "
        "(Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)."
    )
    user_prompt = f"""
    Behavior: "**{behavior_text}**"
    Analyze this behavior and classify it into one of the Big Five personality traits.
    Format your response as a single JSON object with two keys:
    1. `trait`: The single most relevant Big Five trait (e.g., "Conscientiousness").
    2. `justification`: A brief explanation of why this behavior implies that trait.
    """
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        response = model.generate_content(full_prompt)
        data = clean_json_response(response.text)
        return data if data else {}
    except Exception as e:
        print(f"Error in infer_trait_from_behavior: {e}")
        return {}

# --- KNOWLEDGE GRAPH FUNCTION ---
def build_and_visualize_kg(triples: list, filename="knowledge_graph.png"):
    """Creates, visualizes, and saves a knowledge graph from triples."""
    G = nx.DiGraph()  # Use a Directed Graph
    
    # We need to identify node types for coloring
    subjects = set()
    traits = set()
    behaviors = set()

    for s, p, o in triples:
        G.add_edge(s, o, label=p) # Add the edge (s -> o) with a label 'p'
        if p == "exhibits":
            subjects.add(s)
            behaviors.add(o)
        elif p == "implies":
            behaviors.add(s)
            traits.add(o)
            
    # Prepare for visualization
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.9, iterations=50) # 'k' controls spacing

    # Define colors for node types
    color_map = []
    for node in G:
        if node in subjects:
            color_map.append('skyblue')  # Subject nodes
        elif node in traits:
            color_map.append('lightgreen') # Trait nodes
        elif node in behaviors:
            color_map.append('lightcoral') # Behavior nodes
        else:
            color_map.append('gray')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=2500, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrowsize=20)
    
    # Draw node labels
    # Use a 'shortened' label for long behavior strings
    labels = {node: (node[:30] + '...') if len(node) > 30 else node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    plt.title("Personality Knowledge Graph")
    plt.axis('off') # Hide axes
    
    # Save the graph to a file
    plt.savefig(filename)
    print(f"\n--- Knowledge Graph saved to {filename} ---")

# --- MAIN EXECUTION ---
def main():
    """
    Main function to run the full KG extraction and building pipeline.
    """
    
    # Our 5 synthetic documents
    documents = [
        # Doc 1: Kyaw (Conscientiousness)
        "Kyaw is a meticulous planner. For the team's Germany trip, he created a detailed spreadsheet organizing every flight, hotel booking, and meeting, which he triple-checked for errors. He prefers to work with headphones on to maintain deep focus and consistently delivers his reports two days before the deadline.",
        
        # Doc 2: Linn (Extraversion, Openness)
        "Linn thrives on spontaneity. She finds rigid schedules stifling and often comes up with her best ideas during last-minute brainstorming sessions. She's highly sociable and recharges by being around other people, often organizing team lunches and after-work events.",
        
        # Doc 3: David (Agreeableness)
        "David is the office mediator. When the marketing and sales teams had a disagreement, he calmly listened to both sides, acknowledged their valid points, and helped them find a compromise. He is always the first to notice when a colleague seems stressed and will ask them, 'Is everything okay?'.",
        
        # Doc 4: Sarah (Low Openness / High Conscientiousness)
        "Sarah is a creature of habit. She arrives at the office at 8:55 AM every day, eats the same lunch from the same cafe, and files her work using a color-coding system she has not changed in five years. She is resistant to new software updates and prefers the 'old way' of doing things.",
        
        # Doc 5: Michael (High Openness)
        "Michael leads the R&D team. He is constantly reading academic papers and encourages his team to experiment with new, unproven technologies. He is known for asking 'what if?' and is comfortable with ambiguity, often saying that failure is just part of the innovation process."
    ]

    all_triples = []
    
    # Process each document
    for i, doc in enumerate(documents):
        print(f"\n--- Processing Document {i+1} ---")
        kg_triples = []

        # Step 1: Extract Subjects
        subjects = extract_subjects(doc)
        print(f"Found Subjects: {subjects}")

        # Step 2 & 3: Extract Behaviors and Infer Traits
        for subject in subjects:
            print(f"Analyzing Subject: {subject}")
            behaviors = extract_behaviors(doc, subject)
            
            for behavior in behaviors:
                print(f"  Behavior: {behavior}")
                trait_info = infer_trait_from_behavior(behavior)
                
                if trait_info and 'trait' in trait_info:
                    trait = trait_info.get('trait')
                    print(f"    -> Implied Trait: {trait}")
                    
                    kg_triples.append((subject, "exhibits", behavior))
                    kg_triples.append((behavior, "implies", trait))
                else:
                    print(f"    -> Could not infer trait for this behavior.")
        
        all_triples.extend(kg_triples)

    print("\n\n--- Final Knowledge Graph Triples (All Documents) ---")
    for triple in all_triples:
        print(triple)

    # Step 4: Build and Visualize the Graph
    if all_triples:
        build_and_visualize_kg(all_triples, filename="knowledge_graph_all_docs.png")
    else:
        print("\nNo triples were generated, skipping graph visualization.")

if __name__ == "__main__":
    main()
