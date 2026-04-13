from typing import Literal
import numpy as np

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def to_dict(self):
        return {"id": self.id, "x": self.x, "y": self.y}

class Frame:
    def __init__(self, id, node_i, node_j, pin_i:bool = False, pin_j:bool = False):
        self.id = id
        self.node_i = node_i
        self.node_j = node_j
        self.pin_i = pin_i
        self.pin_j = pin_j

    def to_dict(self):
        return {"id": self.id, "node_i": self.node_i, "node_j": self.node_j, "pin_i": self.pin_i, "pin_j": self.pin_j}

class Beam:
    def __init__(self, id,  span:float, section = 10, material = 10):
        self.id = id
        self.section = section
        self.material = material
        self.span = span
        self.limit = [float(0.0), float(span)]

    def to_dict(self):
        return {"id": self.id, "section": self.section, "material": self.material, "span": self.span}

class PointLoad:
    def __init__(self, id, xRef, value, type: Literal['Force', 'Moment'], dir: Literal['X', 'Y', 'Z']):
        self.id = id
        self.xRef = xRef
        self.value = value
        self.type = type
        self.dir = dir
        self.limit = float(xRef)

    def to_dict(self):
        return {"id": self.id, "xRef": self.xRef, "value": self.value, "type": self.type, "dir": self.dir}

class UniformLoad:
    def __init__(self, id, xRefi, xRefj, value, type: Literal['Force', 'Moment'], dir: Literal['X', 'Y', 'Z']):
        self.id = id
        self.xRefi = xRefi
        self.xRefj = xRefj
        self.value = value
        self.type = type
        self.dir = dir
        self.limit = [float(xRefi), float(xRefj)]

    def to_dict(self):
        return {"id": self.id, "xRefi": self.xRefi, "xRefj": self.xRefj, "value": self.value, "type": self.type, "dir": self.dir}

class Support:
    def __init__(self, id, xRef, type: Literal['Pin', 'Sliding']):
        self.id = id
        self.xRef = xRef
        self.type = type
        self.limit = float(xRef)

beam001 = Beam(1,4300)
p1 = PointLoad(1, 100, -1200, 'Force', 'Z')
p2 = PointLoad(2, 1800, -1200, 'Force', 'Z')
w1 = UniformLoad(1, 1000, 2600, -280, 'Force', 'Z')
sl = Support(1, 120, "Pin")
sr = Support(2, 4300, "Sliding")

eleData = [beam001, p1, p2, w1, sl, sr]
print(w1.to_dict())
def collectNodes(elements):
    nodes = []
    for item in elements:
        # Check if 'limit' is a list
        if isinstance(item.limit, list):
            # Iterate through the sub-list to handle each value
            for val in item.limit:
                if val not in nodes:
                    nodes.append(val)
        else:
            # Handle single values (int, float, etc.)
            if item.limit not in nodes:
                nodes.append(item.limit)

    nodes.sort()
    return nodes

def subdivide_segments(points, num_divs_per_segment):
    """
    points: List of existing coordinates [0, 5, 10]
    num_divs_per_segment: Number of sub-divisions between each point
    """
    # Sort points to ensure we move logically from start to end
    sorted_points = sorted(list(set(points)))
    refined_nodes = []

    for i in range(len(sorted_points) - 1):
        start = sorted_points[i]
        end = sorted_points[i + 1]

        # Generate linear space between the two points
        # We use num_divs_per_segment + 1 to include the endpoints
        segment_nodes = np.linspace(start, end, num_divs_per_segment + 1)

        # Append all but the last node (to avoid duplicates at the next start)
        refined_nodes.extend(segment_nodes[:-1])

    # Add the very last point of the beam
    refined_nodes.append(sorted_points[-1])

    return [float(round(n, 8)) for n in refined_nodes]

major_nodes = collectNodes(eleData)
inter_nodes = subdivide_segments(major_nodes, 7)

print(major_nodes)
print(inter_nodes)

beam_nodes = []
for index, x_coord in enumerate(inter_nodes):
    beam_nodes.append(Node(index, x_coord, 0.0))

print(beam_nodes)
