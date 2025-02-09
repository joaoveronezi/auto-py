from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from automata.fa.dfa import DFA
from automata.pda.npda import NPDA
from automata.tm.dtm import DTM
from pydantic import BaseModel
import graphviz
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


OUTPUT_DIR = "output/"
DFA_IMAGE = os.path.join(OUTPUT_DIR, "dfa_diagram.png")
PDA_IMAGE = os.path.join(OUTPUT_DIR, "pda_diagram.png")
TM_IMAGE = os.path.join(OUTPUT_DIR, "tm_diagram.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- Helper Functions ----------------
def parse_pda_transitions(transitions):
    """Converts JSON-friendly PDA transitions into the correct nested dictionary format."""
    parsed_transitions = {}

    for key, value in transitions.items():
        state, symbol, stack_top = key.split(",")  

        # Converting "E" to epsilon ""
        if symbol == "E":
            symbol = ""

        next_state, stack_action = value[0], value[1] if isinstance(value[1], list) else [value[1]]


        if state not in parsed_transitions:
            parsed_transitions[state] = {}


        if symbol not in parsed_transitions[state]:
            parsed_transitions[state][symbol] = {}

        parsed_transitions[state][symbol][stack_top] = (next_state, stack_action)

    return parsed_transitions

def parse_tm_transitions(transitions):
    """Converts JSON-friendly Turing Machine transitions into the correct nested dictionary format."""
    parsed_transitions = {}

    for key, value in transitions.items():
        state, symbol = key.split(",")  

        next_state, write_symbol, move_direction = value[0], value[1], value[2]

       
        if state not in parsed_transitions:
            parsed_transitions[state] = {}

      
        parsed_transitions[state][symbol] = (next_state, write_symbol, move_direction)

    return parsed_transitions

def validate_word(automaton, word):
    """Checks if the automaton accepts the given word."""
    try:
        return automaton.accepts_input(word) if word else None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating word: {str(e)}")


# ---------------- Request Models ----------------
class DFARequest(BaseModel):
    states: set[str]
    input_symbols: set[str]
    transitions: dict[str, dict[str, str]]
    initial_state: str
    final_states: set[str]
    word: str = None

class PDARequest(BaseModel):
    states: set[str]
    input_symbols: set[str]
    stack_symbols: set[str]
    transitions: dict[str, list]
    initial_state: str
    initial_stack_symbol: str
    final_states: set[str]
    word: str = None

class TuringMachineRequest(BaseModel):
    states: set[str]
    input_symbols: set[str]
    tape_symbols: set[str]
    transitions: dict[str, list]  
    initial_state: str
    blank_symbol: str
    final_states: set[str]
    word: str = None

# ---------------- DFA Endpoints ----------------
@app.post("/dfa/")
def create_dfa(dfa_info: DFARequest):
    """Creates a deterministic finite automata (DFA) and validates a word if provided."""

    try:
        dfa = DFA(
            states=dfa_info.states,
            input_symbols=dfa_info.input_symbols,
            transitions=dfa_info.transitions,
            initial_state=dfa_info.initial_state,
            final_states=dfa_info.final_states
        )

        word_accepted = validate_word(dfa, dfa_info.word)

        return JSONResponse(content={
            "message": "DFA created successfully",
            "automaton_type": "DFA",
            "num_states": len(dfa.states),
            "num_input_symbols": len(dfa.input_symbols),
            "num_final_states": len(dfa.final_states),
            "initial_state": dfa.initial_state,
            "transitions": dfa_info.transitions,
            "word_accepted": word_accepted,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/dfa/diagram/")
def generate_dfa_diagram(dfa_info: DFARequest):
    """Generates a deterministic finite automata (DFA) diagram and returns the image."""
    try:
        dfa = DFA(
            states=dfa_info.states,
            input_symbols=dfa_info.input_symbols,
            transitions=dfa_info.transitions,
            initial_state=dfa_info.initial_state,
            final_states=dfa_info.final_states
        )
        
        dfa.show_diagram(path=DFA_IMAGE)

        test = FileResponse(DFA_IMAGE, media_type="image/png", filename="dfa_diagram.png")
        print(test)
        return test
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating DFA diagram: {str(e)}")

# ---------------- PDA Endpoints ----------------
def generate_pda_diagram(pda_info: PDARequest, output_path: str):
    """Generates a diagram for a Pushdown Automaton (PDA)."""
    dot = graphviz.Digraph(format="png")
    
    for state in pda_info.states:
        if state in pda_info.final_states:
            dot.node(state, shape="doublecircle")
        else:
            dot.node(state, shape="circle")


    parsed_transitions = parse_pda_transitions(pda_info.transitions)
    for state, transitions in parsed_transitions.items():
        for symbol, stack_transitions in transitions.items():
            for stack_symbol, (next_state, stack_action) in stack_transitions.items():
                label = f"{symbol}, {stack_symbol} → {','.join(stack_action)}"
                dot.edge(state, next_state, label=label)

    dot.render(output_path[:-4], format="png", cleanup=True)

@app.post("/pda/")
def create_pda(pda_info: PDARequest):
    """Creates a Pushdown Automaton (PDA) and validates a word if provided."""
    try:
        parsed_transitions = parse_pda_transitions(pda_info.transitions)

        pda = NPDA(
            states=pda_info.states,
            input_symbols=pda_info.input_symbols,
            stack_symbols=pda_info.stack_symbols,
            transitions=parsed_transitions,
            initial_state=pda_info.initial_state,
            initial_stack_symbol=pda_info.initial_stack_symbol,
            final_states=pda_info.final_states
        )

        word_accepted = validate_word(pda, pda_info.word)


        return JSONResponse(content={
            "message": "PDA created successfully",
            "automaton_type": "PDA",
            "num_states": len(pda.states),
            "num_input_symbols": len(pda.input_symbols),
            "num_final_states": len(pda.final_states),
            "initial_state": pda.initial_state,
            "stack_alphabet": list(pda.stack_symbols),
            "transitions": pda_info.transitions,
            "word_accepted": word_accepted,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pda/diagram/")
def generate_pda_diagram_endpoint(pda_info: PDARequest):
    """Generates a Pushdown Automaton (PDA) diagram and returns the image."""
    try:
        generate_pda_diagram(pda_info, PDA_IMAGE)
        return FileResponse(PDA_IMAGE, media_type="image/png", filename="pda_diagram")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating PDA diagram: {str(e)}")

# ---------------- Turing Machine Endpoints ----------------
def generate_tm_diagram(tm_info: TuringMachineRequest, output_path: str):
    """Generates a diagram for a Turing Machine (TM)."""
    dot = graphviz.Digraph(format="png")


    for state in tm_info.states:
        if state in tm_info.final_states:
            dot.node(state, shape="doublecircle")
        else:
            dot.node(state, shape="circle")

    parsed_transitions = parse_tm_transitions(tm_info.transitions)
    for state, transitions in parsed_transitions.items():
        for symbol, (next_state, write_symbol, move) in transitions.items():
            label = f"{symbol} → {write_symbol}, {move}"
            dot.edge(state, next_state, label=label)

    
    dot.render(output_path[:-4], format="png", cleanup=True)

@app.post("/turing-machine/")
def create_turing_machine(tm_info: TuringMachineRequest):
    """Creates a Turing Machine and validates a word if provided."""
    try:
        parsed_transitions = parse_tm_transitions(tm_info.transitions)

        dtm = DTM(
            states=tm_info.states,
            input_symbols=tm_info.input_symbols,
            tape_symbols=tm_info.tape_symbols,
            transitions=parsed_transitions,
            initial_state=tm_info.initial_state,
            blank_symbol=tm_info.blank_symbol,
            final_states=tm_info.final_states
        )

        word_accepted = validate_word(dtm, tm_info.word)

        return JSONResponse(content={
            "message": "Turing Machine created successfully",
            "automaton_type": "DTM",
            "num_states": len(dtm.states),
            "num_input_symbols": len(dtm.input_symbols),
            "num_final_states": len(dtm.final_states),
            "initial_state": dtm.initial_state,
            "tape_alphabet": list(dtm.tape_symbols),
            "transitions": tm_info.transitions,
            "word_accepted": word_accepted,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/turing-machine/diagram/")
def generate_tm_diagram_endpoint(tm_info: TuringMachineRequest):
    """Generates a Turing Machine diagram using Graphviz and returns the image."""
    try:
        generate_tm_diagram(tm_info, TM_IMAGE)
        return FileResponse(TM_IMAGE, media_type="image/png", filename="turing_machine_diagram.png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating TM diagram: {str(e)}")


# ---------------- Root Endpoint ----------------
@app.get("/", include_in_schema=False)
def root():
    return {"message": "Bem Vindo ao Auto API Python! Criado para a disciplina de Teoria da Computação. Para documentação acesse /docs."}
