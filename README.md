# Thapar Campus Navigation System

An interactive path-finding assistant for the Thapar University campus using Dijkstra’s algorithm combined with natural language understanding via Google's Gemini API.

This project demonstrates how traditional graph algorithms can be integrated with large language models to create an intuitive navigation tool. Users input natural language queries such as "How to go from Gate 1 to Library avoiding Hostel B and Canteen?" and the system extracts the start, end, and blocked locations using Gemini API, then computes the shortest path accordingly.

The result is a smart, user-friendly campus navigation assistant ideal for students and visitors.

---

## Features

- Natural language parsing using **Google Gemini API**  
- Shortest path calculation with **Dijkstra’s algorithm**  
- Support for blocked locations in route planning  
- Simple interactive UI built with **Streamlit**  
- Lightweight and easy to extend with standard Python libraries

---

## Files

| File               | Description                                      |
|--------------------|-------------------------------------------------|
| `app.py`           | Main Streamlit application and routing logic    |
| `requirements.txt` | Dependencies needed to run the app               |
| `input.txt`        | Sample input query for testing                    |
| `output.txt`       | Sample output result corresponding to input.txt  |
| `README.md`        | This file                                        |
