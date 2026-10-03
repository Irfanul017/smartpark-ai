# SmartPark AI – Project Context

## Project purpose

SmartPark AI is an academic Intelligent Information Systems mini project. Its primary objective is an intelligent parking management system that uses a Python fuzzy-logic inference engine to determine the most suitable available parking slot.

This is not a conventional parking CRUD project. The future core flow is fuzzification, fuzzy-rule inference, aggregation, centroid defuzzification, suitability scoring (0–100), ranking, and explainable selection of the best slot. It must not use external AI APIs or random scores.

## Approved stack

- Backend: Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, SQLite.
- Intelligent system: scikit-fuzzy, NumPy, Pandas.
- Frontend: React, Vite, TypeScript, Tailwind CSS, Axios, Recharts.
- Testing: Pytest and FastAPI TestClient.

## Future intelligent-system requirements

The independent fuzzy engine will accept distance from entrance, congestion, slot compatibility, walking distance, and user priority. It will return a score, category, membership values, activated rules, and a human-readable explanation. FastAPI will expose that engine only; it must also run independently as `calculate_parking_suitability(...)`.

Use overlapping triangular or trapezoidal membership functions and centroid defuzzification. Inputs include distance (near/medium/far), congestion (low/medium/high), compatibility (poor/acceptable/excellent), walking distance (short/medium/long), and priority (low/medium/high). Output categories are very low, low, medium, high, and very high.

Allocation must retrieve slots, filter occupied/incompatible/EV/accessibility-ineligible options, score eligible slots, rank them, return the top three with explanations, and allow confirmation. The system should demonstrate cases where a better low-congestion slot beats the closest high-congestion one.

## Architecture and quality rules

Keep the design simple, explainable, modular, visual, demo-friendly, and easy to test. Keep fuzzy logic separate from FastAPI, database logic out of controllers, and fuzzy logic out of React. Use clean names, type hints, Pydantic validation, exception handling, unit/API tests, and documentation. Do not add the fuzzy engine in Module 0.

Planned database entities include users, vehicles, parking slots, parking sessions, parking allocations, fuzzy rules, and parking history. SQLite is used initially, with a straightforward path to PostgreSQL. Planned UI includes landing, dashboard, parking request, AI recommendation, map, simulator, fuzzy visualization, admin, history, analytics, explainability, and traditional-vs-intelligent comparison views.
