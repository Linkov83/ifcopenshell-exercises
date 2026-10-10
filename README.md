# IfcOpenShell Exercises

Author: Lyubomir Linkov  
Course: Computational Representations of Built Environments  
Metropolia University of Applied Sciences

## Files

- `hello_world.py`: basic IFC queries, editing and entity creation.
- `code_examples.py`: examples using IfcOpenShell utilities and APIs.
- `exercise_2.py`: extracts wall and roof quantities and calculates total areas.

## Installation

```bash
python -m pip install ifcopenshell numpy networkx
```

## Running Exercise 2

Place `Building-Architecture (1).ifc` in the same folder as the Python files, then run:

```bash
python exercise_2.py
```

The input IFC model is not included in this repository.

The `main(model_path)` function accepts the IFC file path and returns two lists: walls and roof elements. Each list contains dictionaries with the element GUID, net volume and net area.

## Results

- Walls: 4
- Roof slabs: 2
- Total wall net side area: 43.291413 m²
- Total roof net area: 53.612836 m²

The model contains one `IfcRoof` with no quantity sets. Its two component slabs have the effective predefined type `ROOF`. Their quantities are extracted from `Qto_SlabBaseQuantities`. The floor slab is excluded.
