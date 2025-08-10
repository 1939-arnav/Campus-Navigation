import streamlit as st
import heapq
import os
import requests
import json
import copy

# -------------------------
# Full Thapar campus graph (assumed distances)
# -------------------------
graph = {
    "Gate 1": {"Main Road": 2, "SBOP": 5},
    "Main Road": {"TAN Block": 4, "Gate 1": 2, "Library": 6},
    "TAN Block": {"CS Block": 3, "Main Road": 4, "Hostel A": 5},
    "CS Block": {"SBOP": 6, "TAN Block": 3, "Library": 4},
    "SBOP": {"Gate 1": 5, "CS Block": 6, "Admin Block": 3},
    "Library": {"Main Road": 6, "CS Block": 4, "Hostel B": 5},
    "Hostel A": {"TAN Block": 5, "Hostel B": 3},
    "Hostel B": {"Library": 5, "Hostel A": 3, "Hostel C": 4},
    "Hostel C": {"Hostel B": 4, "Canteen": 6},
    "Canteen": {"Hostel C": 6, "Admin Block": 2},
    "Admin Block": {"SBOP": 3, "Canteen": 2, "Auditorium": 4},
    "Auditorium": {"Admin Block": 4, "Sports Complex": 5},
    "Sports Complex": {"Auditorium": 5, "Gate 2": 7},
    "Gate 2": {"Sports Complex": 7}
}

# -------------------------
# Dijkstra's Algorithm (with blocked nodes)
# -------------------------
def dijkstra(graph, start, end, blocked_nodes=None):
    if blocked_nodes is None:
        blocked_nodes = []

    # Create a copy of the graph without blocked nodes
    mod_graph = copy.deepcopy(graph)
    for blocked in blocked_nodes:
        if blocked in mod_graph:
            mod_graph.pop(blocked)
        for node in list(mod_graph.keys()):
            if blocked in mod_graph[node]:
                mod_graph[node].pop(blocked)

    if start not in mod_graph or end not in mod_graph:
        return float("inf"), []

    pq = [(0, start, [])]
    visited = set()

    while pq:
        dist, node, path = heapq.heappop(pq)
        if node in visited:
            continue
        path = path + [node]
        visited.add(node)

        if node == end:
            return dist, path

        for neighbor, cost in mod_graph[node].items():
            if neighbor not in visited:
                heapq.heappush(pq, (dist + cost, neighbor, path))

    return float("inf"), []

# -------------------------
# Gemini API call
# -------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def gemini_extract_locations(user_query):
    prompt = f"""
Extract the start location, end location, and any blocked locations from this sentence: "{user_query}".
Respond strictly in JSON format as:
{{ "start": "<start_location>", "end": "<end_location>", "blocked_nodes": ["<node1>", "<node2>"] }}
If there are no blocked nodes, respond with an empty list for "blocked_nodes".
"""

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY,
    }

    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(URL, headers=headers, json=data)
    response.raise_for_status()
    response_json = response.json()

    try:
        text = response_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return None, None, []

    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-len("```")].strip()

    try:
        extracted = json.loads(text)
    except json.JSONDecodeError:
        return None, None, []

    return extracted.get("start"), extracted.get("end"), extracted.get("blocked_nodes", [])

# -------------------------
# Normalize extracted node names to valid keys in graph
# -------------------------
def find_node(name, valid_nodes):
    if not name:
        return None
    name_lower = name.lower().strip()
    for node in valid_nodes:
        if node.lower() == name_lower:
            return node
    return None

def find_nodes(node_list, valid_nodes):
    normalized = []
    for name in node_list:
        node = find_node(name, valid_nodes)
        if node:
            normalized.append(node)
    return normalized

# -------------------------
# Streamlit UI
# -------------------------
st.title("Thapar Campus Navigation")
st.write("Enter your query in natural language (e.g. 'How to go from Gate 1 to Library avoiding Hostel B and Canteen?')")

query = st.text_input("Enter your query:")

if st.button("Find Path"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        start_raw, end_raw, blocked_raw = gemini_extract_locations(query)
        # st.write(f"Raw Gemini extraction: start='{start_raw}', end='{end_raw}', blocked={blocked_raw}")

        start_node = find_node(start_raw, graph.keys())
        end_node = find_node(end_raw, graph.keys())
        blocked_nodes = find_nodes(blocked_raw, graph.keys())

        # st.write(f"Normalized: start='{start_node}', end='{end_node}', blocked={blocked_nodes}")

        if not start_node or not end_node:
            st.error(f"Could not understand start or end location. Valid locations: {list(graph.keys())}")
        elif start_node == end_node:
            st.warning("Start and End locations cannot be the same.")
        else:
            distance, path = dijkstra(graph, start_node, end_node, blocked_nodes)
            if distance == float("inf"):
                st.error("No path found!")
            else:
                st.success(f"Shortest distance: {distance}")
                st.write("Path:", " → ".join(path))
