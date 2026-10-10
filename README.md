# IfcOpenShell Exercises

Author: Lyubomir Linkov  
Course: Computational Representations of Built Environments  
Metropolia University of Applied Sciences

## Files

- `hello_world.py`: basic IFC queries, attribute editing, entity creation, copying and removal.
- `code_examples.py`: examples using IfcOpenShell utilities and APIs, including model creation and construction scheduling.
- `exercise_2.py`: extracts wall and roof quantities and calculates their total areas.
- `requirements.txt`: package versions used to run the exercises.

## Environment

The exercises were run on Windows using Python 3.14 with:

- IfcOpenShell 0.8.5
- NumPy 2.5.3
- NetworkX 3.7

## Installation

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## Input Model

Place `Building-Architecture (1).ifc` in the same folder as the Python files.

The original IFC model uses the IFC4X3 schema and is not included in this repository.

## Exercise 1: Tutorial

The scripts cover the Hello, world! and Code examples sections of the IfcOpenShell Python tutorial.

Run them separately:

```bash
python hello_world.py
```

```bash
python code_examples.py
```

The scripts create these output files:

- `hello_world_modified.ifc`
- `simple_model.ifc`
- `construction_schedule.ifc`

The original input file is preserved.

## Exercise 2: Wall and Roof Quantities

Run:

```bash
python exercise_2.py
```

The code is divided into functions:

- `load_model(model_path)`: opens the IFC file.
- `get_walls(model)`: returns wall GUIDs, net volumes and net side areas.
- `get_roofs(model)`: returns roof slab GUIDs, net volumes and net areas.
- `calculate_total_area(elements, area_key)`: sums the selected area values.
- `main(model_path)`: prints the lists and total areas, then returns `walls, roofs`.

The main function can also be called with another file path:

```python
from exercise_2 import main

walls, roofs = main("Building-Architecture (1).ifc")
```

### Identifying Roof Elements

The model contains one `IfcRoof` without its own quantity sets. It is composed of two `IfcSlab` elements whose effective predefined type is `ROOF`.

The script selects these roof slabs using `get_predefined_type()`, which also checks the assigned element type. The floor slab, with type `FLOOR`, is excluded.

Wall quantities are read from `Qto_WallBaseQuantities`. Roof slab quantities are read from `Qto_SlabBaseQuantities`.

The script expects the quantity sets and quantity names found in the supplied model.

### Output Format

The function returns two lists of dictionaries.

Wall entries contain:

```python
{
    "NetSideArea": 6.346324676317877,
    "NetVolume": 1.26926493526358,
    "GlobalId": "1AQAupaRP1txwK1AGiN61V"
}
```

Roof entries contain:

```python
{
    "NetArea": 22.40114282797721,
    "NetVolume": 6.7203428483966,
    "GlobalId": "0ZTBBPo6f6bxqV2K7Oelrq"
}
```

### Results

| Elements | Count | Total net area |
| --- | ---: | ---: |
| Walls | 4 | 43.291413 m² |
| Roof slabs | 2 | 53.612836 m² |

Areas in this model are stored in square metres and volumes in cubic metres. The totals use the stored quantities rather than recalculating geometry.

## Tutorial References

- [Hello, world!](https://docs.ifcopenshell.org/ifcopenshell-python/hello_world.html)
- [Code examples](https://docs.ifcopenshell.org/ifcopenshell-python/code_examples.html)
