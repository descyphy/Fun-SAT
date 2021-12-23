# Executed in Python 3.6
# This is the class construction file. Please do not modify existing class functions and only add new one if you need.


class NtkObject:
    def __init__(self, name: str):
        self.name = name  # Node name
        self.gate_type = 0  # Indicate which logic gate type this node is
        self.fan_in_node = []  # The list of immediate fan-in nodes
        self.fan_out_node = []  # The list of immediate fan-out nodes
        self.value = None  # Simulated value
        self.next_node = None  # Used for logic simulation, obtained by calling levelization()
        self.previous_node = None
        self.fan_in_cone = []  # The list of nodes in the logic fan-in cone of this node
        self.topo_sort_index = None
        self.influence_by_key = None  # Used by logic cone analysis
        self.length_pos = 0  # Used by Universal Circuit
        self.depth_index = None  # Used by Universal Circuit
        self.width_index = None  # Used by Universal Circuit
        self.reverse_level = None

    def __del__(self):
        pass

    def gate_type_config(self, x: int):  # Set the gate type of object/node.
        self.gate_type = x

    def add_fan_in(self, x):  # Add object x to the fan_in_node list
        self.fan_in_node.append(x)

    def add_fan_out(self, x):  # Add object x to the fan_out_node list
        self.fan_out_node.append(x)

    def remove_fan_in(self, x):  # Remove object x from the fan_in_node list
        self.fan_in_node.remove(x)

    def remove_fan_out(self, x):  # Remove object x from the fan_out_node list
        self.fan_out_node.remove(x)


class Ntk:
    def __init__(self):
        self.gateType = {"IPT": 1, "NOT": 2, "NAND": 3, "AND": 4, "NOR": 5, "OR": 6, "XOR": 7, "XNOR": 8, "DFF": 9,
                         "BUFF": 10}  # From string to integer
        self.gateType_reverse = {1: "IPT", 2: "NOT", 3: "NAND", 4: "AND", 5: "NOR", 6: "OR", 7: "XOR", 8: "XNOR",
                                 9: "DFF", 10: "BUFF"}  # From integer to string
        self.circuit_name = None  # The circuit name is stored
        self.object_list = []  # The list to store all the objects in the netlist/network
        self.object_name_list = []  # The list to store all the objects' names in the netlist/network.
        self.PI = []  # Primary input
        self.PO = []  # Primayry output
        self.KI = []  # Key input
        self.PPI = []  # Pseudo Primary input
        self.PPO = []  # Pseudo Primayry output
        self.available_key_index = 0  # Used to assist creating new key nodes without using existing key node names
        self.simulation_starting_obj = None  # Obtained by calling levelization(), used for logic simulation
        self.simulation_ending_obj = None  # Obtained by calling levelization(), used for logic simulation
        self.TL = []  # Transition Lis
        self.available_node_index = 0
        self.node_to_name = {}
        self.name_to_node = {}

    def __del__(self):
        pass

    def add_object(self, obj, func=None):
        if func is not None:
            obj.gate_type = self.gateType[func]
        # else: # FIXME: Fix this when parsing PO nodes
        # 	if obj.gate_type == 0:
        # 		print('Warning: Node %s has not yet been assigned a gate type. \n' % obj.name)
        self.object_list.append(obj)
        self.object_name_list.append(obj.name)
        self.node_to_name[obj] = obj.name
        self.name_to_node[obj.name] = obj
        self.available_node_index += 1

    def remove_object(self, obj):  # Remove an object from the netlist/network
        if obj in self.PI:
            self.PI.remove(obj)
        if obj in self.PO:
            self.PO.remove(obj)
        if obj in self.KI:
            self.KI.remove(obj)
            print('Warning: The available key index should be reset! \n')
        self.object_name_list.remove(self.find_name_by_node(obj))
        self.object_list.remove(obj)
        del self.name_to_node[self.node_to_name[obj]]
        del self.node_to_name[obj]
        del obj

    def connect_objectives_by_name(self, name_a: str, name_b: str):
        a = self.name_to_node[name_a]
        b = self.name_to_node[name_b]
        a.add_fan_out(b)
        b.add_fan_in(a)

    def connect_objectives(self, obj_a, obj_b):
        obj_a.add_fan_out(obj_b)
        obj_b.add_fan_in(obj_a)

    def disconnect_objectives_by_name(self, name_a: str, name_b: str):
        a = self.name_to_node[name_a]
        b = self.name_to_node[name_b]
        a.remove_fan_out(b)
        b.remove_fan_in(a)

    def disconnect_objectives(self, obj_a, obj_b):
        obj_a.remove_fan_out(obj_b)
        obj_b.remove_fan_in(obj_a)

    def find_node_by_name(self, name: str):
        return self.name_to_node[name]

    def find_name_by_node(self, obj):
        return self.node_to_name[obj]

    def change_node_name(self, obj, new_name: str):
        self.object_name_list[self.object_list.index(obj)] = new_name
        obj.name = new_name

    def add_PI(self, obj):  # Add an object to the PI list
        if obj not in self.PI:
            self.PI.append(obj)

    def add_PO(self, obj):  # Add an object to the PO list
        if obj not in self.PO:
            self.PO.append(obj)

    def add_KI(self, obj):  # Add an object to the KI list
        if obj not in self.KI:
            self.KI.append(obj)
            self.available_key_index += 1

    def remove_node_from_PI(self, obj):
        self.PI.remove(obj)

    def remove_node_from_PO(self, obj):
        self.PO.remove(obj)

    def remove_node_from_KI(self, obj):
        self.KI.remove(obj)
