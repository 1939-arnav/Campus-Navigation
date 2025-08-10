import streamlit as st
import heapq
import os
import requests
import json
import copy

graph = {
    "Gate 1": {"Main Road": 150, "Gate 2": 300},
    "Main Road": {"Gate 1": 150, "CS Block": 220, "B Block": 200},
    "CS Block": {"Main Road": 220, "LT": 80, "D Block": 100},
    "LT": {"CS Block": 80, "TAN Block": 180},
    "TAN Block": {"LT": 180, "Nirvana": 120},
    "Nirvana": {"TAN Block": 120, "COS Complex": 250},
    "COS Complex": {"Nirvana": 250, "Tennis Court": 100},
    "Tennis Court": {"COS Complex": 100, "Playground": 90},
    "Playground": {"Tennis Court": 90, "Football Ground": 200},
    "Football Ground": {"Playground": 200, "Sports Center": 150},
    "Sports Center": {"Football Ground": 150, "Pool": 100},
    "Pool": {"Sports Center": 100, "Hostel M": 250},
    "Hostel M": {"Pool": 250, "Hostel C": 80},
    "Hostel C": {"Hostel M": 80, "Hostel A": 70},
    "Hostel A": {"Hostel C": 70, "Hostel B": 60},
    "Hostel B": {"Hostel A": 60, "Hostel H": 100},
    "Hostel H": {"Hostel B": 100, "Hostel I": 80},
    "Hostel I": {"Hostel H": 80, "Polytechnic College": 200},
    "Polytechnic College": {"Hostel I": 200, "Gate 4": 300},
    "Gate 4": {"Polytechnic College": 300, "Gate 3": 250},
    "Gate 3": {"Gate 4": 250, "Faculty Residence": 100},
    "Faculty Residence": {"Gate 3": 100, "SBOP": 150},
    "SBOP": {"Faculty Residence": 150, "B Block": 100},
    "B Block": {"SBOP": 100, "C Block": 80, "Main Road": 200},
    "C Block": {"B Block": 80, "D Block": 80},
    "D Block": {"C Block": 80, "CS Block": 100},
    "Old Library": {"PG Block": 180},
    "PG Block": {"Old Library": 180, "Gate 2": 250},
    "Gate 2": {"PG Block": 250, "Gate 1": 300, "Sports Complex": 70},
    "Sports Complex": {"Gate 2": 70, "Auditorium": 50},
    "Auditorium": {"Sports Complex": 50, "Admin Block": 40},
    "Admin Block": {"Auditorium": 40, "Canteen": 20},
    "Canteen": {"Admin Block": 20, "Hostel C": 60}
}



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


# API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY = st.secrets["GEMINI_API_KEY"]
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


