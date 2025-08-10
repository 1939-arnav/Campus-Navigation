# Thapar Campus Navigation System

An interactive path-finding assistant for the Thapar University campus using Dijkstra’s algorithm combined with natural language understanding via Google's Gemini API.

This project demonstrates how traditional graph algorithms can be integrated with large language models to create an intuitive navigation tool. Users input natural language queries such as "How to go from Gate 1 to Library avoiding Hostel B and Canteen?" and the system extracts the start, end, and blocked locations using Gemini API, then computes the shortest path accordingly.

The result is a smart, user-friendly campus navigation assistant ideal for students and visitors.

---

## Deployment

The application is deployed and accessible online at:  
[https://campus-navigation.streamlit.app/](https://campus-navigation.streamlit.app/)

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

---

### Node Index
1. Gate 1  
2. Main Road  
3. TAN Block  
4. Nirvana  
5. CS Block  
6. LT (Lecture Theater)  
7. Mechanical Workshops  
8. Sports Center  
9. Pool  
10. Playground  
11. Tennis Court  
12. COS Complex  
13. Football Ground  
14. Hostel M  
15. Hostel C  
16. Hostel A  
17. Hostel B  
18. Hostel H  
19. Hostel I  
20. Polytechnic College  
21. Gate 4  
22. Old Library  
23. Gate 2  
24. PG Block  
25. SBOP  
26. Faculty Residence  
27. Gate 3  
28. B Block  
29. C Block  
30. D Block 
