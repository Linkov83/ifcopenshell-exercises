from pathlib import Path
import ifcopenshell

# Load the model
model_path = Path(__file__).parent / "Building-Architecture (1).ifc"
model = ifcopenshell.open(str(model_path))

# Show the IFC schema
print(model.schema)

# Get an entity by STEP ID
print(model.by_id(1))

# Find and count all walls
walls = model.by_type("IfcWall")
print("Number of walls:", len(walls))

# Get the first wall
wall = walls[0]

# Find it by its actual GUID
print(model.by_guid(wall.GlobalId))

# Check the IFC class
print(wall.is_a())
print(wall.is_a("IfcWall"))
print(wall.is_a("IfcElement"))
print(wall.is_a("IfcWindow"))

# Show the STEP ID
print(wall.id())

# Read attributes by position
print(wall[0])
print(wall[2])

# Read attributes by name
print(wall.GlobalId)
print(wall.Name)

# Show all attributes
print(wall.get_info())

# Show properties and quantities
import ifcopenshell.util.element
print(ifcopenshell.util.element.get_psets(wall))

# Show relationships defining the wall
print(wall.IsDefinedBy)

# Show entities that reference the wall
print(model.get_inverse(wall))

# Show entities referenced by the wall
print(model.traverse(wall))

# Limit the traversal depth
print(model.traverse(wall, max_levels=1))

# Change the wall name
wall.Name = "My new wall name"
print("New name:", wall.Name)

# Generate a new GlobalId
wall.GlobalId = ifcopenshell.guid.new()
print("New GUID:", wall.GlobalId)

# Save the modified model to a new file
output_path = model_path.parent / "hello_world_modified.ifc"
model.write(str(output_path))
print("Saved:", output_path)

# Create blank IFC models
ifc = ifcopenshell.file()
print("Default schema:", ifc.schema)

ifc = ifcopenshell.file(schema="IFC4")
print("Selected schema:", ifc.schema)

# Create a wall using the shorthand method
new_wall = model.createIfcWall()
print(new_wall)
print(model.by_type("IfcWall"))

# Create a wall using create_entity()
print(model.create_entity("IfcWall"))

# Set the GlobalId using a positional argument
print(model.create_entity("IfcWall", ifcopenshell.guid.new()))

# Set attributes using keyword arguments
print(model.create_entity(
    "IfcWall",
    GlobalId=ifcopenshell.guid.new(),
    Name="Wall Name"
))

# Set attributes using a dictionary
data = {
    "GlobalId": ifcopenshell.guid.new(),
    "Name": "Wall Name"
}
print(model.create_entity("IfcWall", **data))

# Reference another entity
wall = model.createIfcWall()
wall.OwnerHistory = model.createIfcOwnerHistory()
print(wall.OwnerHistory)

# Copy a wall into a model with the same schema
wall = model.by_type("IfcWall")[0]
new_model = ifcopenshell.file(schema=model.schema)
print(new_model.add(wall))

# Delete the wall from the working model
print("Walls before removal:", len(model.by_type("IfcWall")))
model.remove(wall)
print("Walls after removal:", len(model.by_type("IfcWall")))