from pathlib import Path

import ifcopenshell
import ifcopenshell.util.element


# Load the IFC model
def load_model(model_path):
    return ifcopenshell.open(str(model_path))


# Collect wall quantities and GUIDs
def get_walls(model):
    walls = []

    for wall in model.by_type("IfcWall"):
        quantities = ifcopenshell.util.element.get_psets(
            wall, qtos_only=True
        )
        wall_quantities = quantities["Qto_WallBaseQuantities"]

        walls.append({
            "NetSideArea": wall_quantities["NetSideArea"],
            "NetVolume": wall_quantities["NetVolume"],
            "GlobalId": wall.GlobalId
        })

    return walls


# Collect quantities and GUIDs of the roof slabs
def get_roofs(model):
    roofs = []

    for slab in model.by_type("IfcSlab"):
        slab_type = ifcopenshell.util.element.get_predefined_type(slab)

        if slab_type != "ROOF":
            continue

        quantities = ifcopenshell.util.element.get_psets(
            slab, qtos_only=True
        )
        roof_quantities = quantities["Qto_SlabBaseQuantities"]

        roofs.append({
            "NetArea": roof_quantities["NetArea"],
            "NetVolume": roof_quantities["NetVolume"],
            "GlobalId": slab.GlobalId
        })

    return roofs


# Calculate the total area of the selected elements
def calculate_total_area(elements, area_key):
    return sum(element[area_key] for element in elements)


# Run the assignment and return the two lists
def main(model_path):
    model = load_model(model_path)

    walls = get_walls(model)
    roofs = get_roofs(model)

    area_wall = calculate_total_area(walls, "NetSideArea")
    area_roof = calculate_total_area(roofs, "NetArea")

    print("Walls:")
    print(walls)

    print("\nRoofs:")
    print(roofs)

    print(f"\nTotal area of the roofs is {area_roof:.6f} sqm.")
    print(f"Total area of the walls is {area_wall:.6f} sqm.")

    return walls, roofs


if __name__ == "__main__":
    model_path = Path(__file__).parent / "Building-Architecture (1).ifc"
    walls, roofs = main(model_path)