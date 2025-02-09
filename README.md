# Automaton Project

A project created with Python to generate and validate automatons, supporting Deterministic Finite Automata (DFA), Pushdown Automata (PDA), and Turing Machines (TM). The project includes a FastAPI backend and a simple frontend interface.

## Technologies Used

- **FastAPI** - Web framework for building APIs.
- **Conda** - Package and environment management system.
- **Automata** - Library for handling DFA, PDA, and Turing Machines.
- **Uvicorn** - ASGI server for running FastAPI.
- **Python 3.10** - Programming language.
- **Graphviz** - Used for generating automaton diagrams.

---

## Project Structure

```
Automaton-Project/
│── backend/
│   ├── main.py  # FastAPI Backend
│── front-end/
│   ├── index.html  # Basic Frontend
│── postman-collection.json  # Postman API Collection
│── environment.yml  # Conda environment configuration
```

---

## Prerequisites

Ensure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Conda](https://docs.conda.io/en/latest/miniconda.html)
- [Graphviz](https://graphviz.gitlab.io/download/)

---

## Setup and Installation

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd Automaton-Project
   ```

2. **Set up the Conda environment:**

   ```sh
   conda env create -f environment.yml
   conda activate automaton-env
   ```

   This will install all required dependencies automatically.

3. **Ensure Graphviz is installed:**
   ```sh
   pip install graphviz
   ```
   If needed, install Graphviz system-wide via:
   - **Ubuntu/Debian:** `sudo apt install graphviz`
   - **MacOS:** `brew install graphviz`
   - **Windows:** [Download from Graphviz](https://graphviz.gitlab.io/download/)

---

## Running the Project

1. **Start the backend server:**

   ```sh
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - The API documentation will be available at:
     - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
     - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

2. **Run the frontend (Open `index.html` in a browser):**
   - The frontend allows you to interact with the API easily.

---

## API Usage

The API provides endpoints to:

- Create and validate DFA, PDA, and Turing Machines.
- Generate diagrams for each automaton type.

### Example Request (DFA Creation)

```sh
POST http://localhost:8000/dfa/
Content-Type: application/json
```

```json
{
  "states": ["q0", "q1", "q2"],
  "input_symbols": ["0", "1"],
  "transitions": {
    "q0": { "0": "q0", "1": "q1" },
    "q1": { "0": "q0", "1": "q2" },
    "q2": { "0": "q2", "1": "q1" }
  },
  "initial_state": "q0",
  "final_states": ["q1"],
  "word": "1001"
}
```

### Example Request (DFA Diagram Generation)

```sh
POST http://localhost:8000/dfa/diagram/
```

This returns an image representation of the DFA.

---

## Testing with Postman

A **Postman Collection** is included in the repository (`postman-collection.json`).

1. Open Postman.
2. Import `postman-collection.json`.
3. Use the predefined requests to test the API.

---

## Additional Notes

- The project supports **CORS** for cross-origin requests.
- Error handling is implemented for malformed automaton configurations.
- You can extend the frontend (`index.html`) to add more UI interactions.

---
