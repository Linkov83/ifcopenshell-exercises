from pathlib import Path
import datetime

import ifcopenshell
import ifcopenshell.util.element as element_util
import ifcopenshell.util.placement as placement_util
import ifcopenshell.util.classification as classification_util
import ifcopenshell.util.unit as unit_util
import ifcopenshell.util.system as system_util

import ifcopenshell.api.root
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import ifcopenshell.api.sequence

# This function requires networkx.
from ifcopenshell.api.sequence.recalculate_schedule import (
    recalculate_schedule
)


# Load the original IFC model
model_path = Path(__file__).parent / "Building-Architecture (1).ifc"
model = ifcopenshell.open(str(model_path))


# 1. Get all entities
for inst in model:
    print("The STEP entity is:", inst)
    print(inst.get_info())
    print(inst.is_a())

    if hasattr(inst, "Name"):
        print(inst.Name)


# 2. Get all wall types
for wall_type in model.by_type("IfcWallType"):
    print("The wall type element is:", wall_type)
    print("The name of the wall type is:", wall_type.Name)


# 3. Get all door occurrences of each type
door_types = model.by_type("IfcDoorType")
print("Number of door types:", len(door_types))

for door_type in door_types:
    print("The door type is:", door_type.Name)
    doors = element_util.get_types(door_type)
    print("Number of doors of this type:", len(doors))

    for door in doors:
        print("The door name is:", door.Name)


# 4. Get the type of a wall
wall = model.by_type("IfcWall")[0]
wall_type = element_util.get_type(wall)

if wall_type:
    print("The wall type is:", wall_type.Name)
else:
    print("The wall has no assigned type.")


# 5. Get properties and quantities
print("Wall type properties and quantities:")
print(element_util.get_psets(wall_type) if wall_type else {})

print("Wall properties and quantities:")
print(element_util.get_psets(wall))

print("Properties only:")
print(element_util.get_psets(wall, psets_only=True))

print("Quantities only:")
print(element_util.get_psets(wall, qtos_only=True))


# 6. Find the spatial container
container = element_util.get_container(wall)
print(
    "The wall is located on:",
    container.Name if container else "No spatial container"
)


# 7. Get all elements in each storey
for storey in model.by_type("IfcBuildingStorey"):
    elements = element_util.get_decomposition(storey)
    print("Storey:", storey.Name)
    print("Number of elements:", len(elements))

    for element in elements:
        print(element.Name)


# 8. Get placement coordinates in project units
matrix = placement_util.get_local_placement(wall.ObjectPlacement)
print("Wall XYZ coordinates:", matrix[:3, 3])


# 9. Get classification references
references = classification_util.get_references(wall)
print("Classification references:", len(references))

for reference in references:
    print("Classification code:", reference.Identification)
    classification = classification_util.get_classification(reference)

    if classification:
        print("Classification system:", classification.Name)


# 10. Convert project length units to metres and back
unit_scale = unit_util.calculate_unit_scale(model)
quantities = element_util.get_psets(wall, qtos_only=True)
project_length = quantities["Qto_WallBaseQuantities"]["Length"]

si_metres = project_length * unit_scale
print("Length in project units:", project_length)
print("Length in metres:", si_metres)
print("Converted back:", si_metres / unit_scale)


# 11. Get distribution systems
pipes = model.by_type("IfcPipeSegment")
print("Number of pipe segments:", len(pipes))

for pipe in pipes:
    systems = system_util.get_element_systems(pipe)

    for system in systems:
        print("Pipe:", pipe.Name, "System:", system.Name)


# 12. Copy an entity
wall_copy_class = ifcopenshell.api.root.copy_class(
    model, product=wall
)
print("Class copy:", wall_copy_class.GlobalId)

wall_shallow_copy = element_util.copy(model, wall)
print("Shallow copy:", wall_shallow_copy.GlobalId)

wall_deepgraph_copy = element_util.copy_deep(
    model, wall, exclude=None
)
print("Deep copy:", wall_deepgraph_copy.GlobalId)

new_model = ifcopenshell.file(schema=model.schema)
copied_wall = new_model.add(wall)
print("Wall copied into another model:", copied_wall.GlobalId)


# 13. Create a simple model from scratch
simple_model = ifcopenshell.api.project.create_file()

project = ifcopenshell.api.root.create_entity(
    simple_model, ifc_class="IfcProject", name="My Project"
)
ifcopenshell.api.unit.assign_unit(simple_model)

context = ifcopenshell.api.context.add_context(
    simple_model, context_type="Model"
)
body = ifcopenshell.api.context.add_context(
    simple_model,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=context
)

site = ifcopenshell.api.root.create_entity(
    simple_model, ifc_class="IfcSite", name="My Site"
)
building = ifcopenshell.api.root.create_entity(
    simple_model, ifc_class="IfcBuilding", name="Building A"
)
storey = ifcopenshell.api.root.create_entity(
    simple_model,
    ifc_class="IfcBuildingStorey",
    name="Ground Floor"
)

ifcopenshell.api.aggregate.assign_object(
    simple_model, relating_object=project, products=[site]
)
ifcopenshell.api.aggregate.assign_object(
    simple_model, relating_object=site, products=[building]
)
ifcopenshell.api.aggregate.assign_object(
    simple_model, relating_object=building, products=[storey]
)

new_wall = ifcopenshell.api.root.create_entity(
    simple_model, ifc_class="IfcWall", name="Example Wall"
)
ifcopenshell.api.geometry.edit_object_placement(
    simple_model, product=new_wall
)

# Geometry dimensions are in metres
representation = ifcopenshell.api.geometry.add_wall_representation(
    simple_model,
    context=body,
    length=5,
    height=3,
    thickness=0.2
)
ifcopenshell.api.geometry.assign_representation(
    simple_model,
    product=new_wall,
    representation=representation
)
ifcopenshell.api.spatial.assign_container(
    simple_model,
    relating_structure=storey,
    products=[new_wall]
)

simple_path = model_path.parent / "simple_model.ifc"
simple_model.write(str(simple_path))
print("Simple model saved:", simple_path)


# 14. Create a construction schedule
def add_task(model, name, predecessor, work_schedule):
    task = ifcopenshell.api.sequence.add_task(
        model,
        work_schedule=work_schedule,
        name=name,
        predefined_type="CONSTRUCTION"
    )

    task_time = ifcopenshell.api.sequence.add_task_time(
        model, task=task
    )
    ifcopenshell.api.sequence.edit_task_time(
        model,
        task_time=task_time,
        attributes={
            "ScheduleStart": datetime.date(2000, 1, 1),
            "ScheduleDuration": "P1W"
        }
    )

    if predecessor:
        ifcopenshell.api.sequence.assign_sequence(
            model,
            relating_process=predecessor,
            related_process=task
        )

    return task


# Reload the original model without the example wall copies
schedule_model = ifcopenshell.open(str(model_path))

schedule = ifcopenshell.api.sequence.add_work_schedule(
    schedule_model, name="Construction"
)
task = add_task(
    schedule_model, "Site establishment", None, schedule
)
start_task = task

storeys = sorted(
    schedule_model.by_type("IfcBuildingStorey"),
    key=placement_util.get_storey_elevation
)

for storey in storeys:
    task = add_task(
        schedule_model,
        f"Construct {storey.Name}",
        task,
        schedule
    )

    for product in element_util.get_decomposition(storey):
        ifcopenshell.api.sequence.assign_product(
            schedule_model,
            relating_product=product,
            related_object=task
        )

ifcopenshell.api.sequence.cascade_schedule(
    schedule_model, task=start_task
)

# Calculate the critical path using the directly imported function
recalculate_schedule(schedule_model, work_schedule=schedule)

schedule_path = model_path.parent / "construction_schedule.ifc"
schedule_model.write(str(schedule_path))
print("Construction schedule saved:", schedule_path)