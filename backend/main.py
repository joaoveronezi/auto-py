from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from automata.fa.dfa import DFA
import os
from pydantic import BaseModel


IMAGE_PATH = "output/dfa_diagram.png"

    # my_dfa = DFA(
    #   states={'q0', 'q1', 'q2'},
    #   input_symbols={'0', '1'},
    #   transitions={
    #       'q0': {'0': 'q0', '1': 'q1'},
    #       'q1': {'0': 'q0', '1': 'q2'},
    #       'q2': {'0': 'q2', '1': 'q1'}
    #   },
    #   initial_state='q0',
    #   final_states={'q1'}
    # )

class DFARequest(BaseModel):
    states: set[str]
    input_symbols: set[str]
    transitions: dict
    initial_state: str 
    final_states: set[str]


# Generate a Deterministic Finite Automaton (DFA) diagram 
def generate_dfa_diagram(dfa_info: DFARequest):
    try:
      new_dfa = DFA(
        states=dfa_info.states,
        input_symbols=dfa_info.input_symbols,
        transitions=dfa_info.transitions,
        initial_state=dfa_info.initial_state,
        final_states=dfa_info.final_states
      )
      os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)
      new_dfa.show_diagram(path=IMAGE_PATH)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating NFA: {str(e)}")


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "description": f"Item {item_id} details"}



@app.post("/dfa-diagram")
def generate_dfa_diagram(dfa_info: DFARequest):
    generate_dfa_diagram(dfa_info)
    
    return FileResponse(IMAGE_PATH, media_type="image/png", filename="dfa_diagram.png")
