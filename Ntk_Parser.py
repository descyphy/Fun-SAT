# Executed in Python 3.6
import re

from Ntk_Struct import *


###########################################################################
# Function name: ntk_parser
# Note: Parse the .bench format netlist into Python
#       This function assumes NO repetition on the I/O ports in the bench file
###########################################################################
def ntk_parser(ipt_file):
    Circuit_graph = Ntk()
    # Read a .BENCH netlist file
    ipt = open(ipt_file)
    Circuit_graph.circuit_name = ipt_file  # Give name to a netlist graph
    counter = 0
    for line in ipt:  # Go through the netlist and log all nodes (input ports and gate output ports)
        counter += 1
        line = line.strip()
        # Remove some unsupported characters in the netlist file
        line = line.replace('[', 'q')
        line = line.replace(']', 'p')

        if line != "":
            if re.match(r'^#', line):  # Comment line
                pass
            else:
                if '#' in line:
                    line = line[:line.index('#')]
                # Check for pattern "INPUT(...)" and "OUTPUT(...)"
                line_syntax = re.match(r'^([A-Za-z_\$\[\]]+) ?\((.+)\)', line)
                if line_syntax:
                    if re.match(r'INPUT', line_syntax.group(1), re.IGNORECASE):
                        ipt_node = line_syntax.group(2)
                        # If the node name does not start with a alphabetical letter, add a letter 'G' before it.
                        if not ipt_node[0].isalpha():
                            ipt_node = 'G' + ipt_node
                        new_node = NtkObject(ipt_node)
                        Circuit_graph.add_object(new_node, 'IPT')
                        # if 'keyinput' not in ipt_node:
                        if 'keyinput' not in ipt_node:
                            Circuit_graph.PI.append(new_node)
                        else:
                            # TODO: Use add_KI() instead.
                            Circuit_graph.KI.append(new_node)
                            Circuit_graph.available_key_index += 1
                else:
                    # Process the gate connection line
                    line_syntax = re.match(r' *([a-zA-Z0-9_\$\[\]]+) *= *([a-zA-Z0-9_\[\]]+) *\( *(.+) *\)', line)
                    left_node = line_syntax.group(1)
                    # If the node name does not start with a alphabetical letter, add a letter 'G' before it.
                    if not left_node[0].isalpha():
                        left_node = 'G' + left_node
                    new_node = NtkObject(left_node)
                    Circuit_graph.add_object(new_node)

    ipt.close()
    ipt = open(ipt_file)
    counter = 0
    for line in ipt:  # Go through the netlist and log all netlist connections
        counter += 1
        line = line.strip()
        # Remove some unsupported characters in the netlist file
        line = line.replace('[', 'q')
        line = line.replace(']', 'p')

        if line != "":
            if re.match(r'^#', line):
                pass
            else:
                if '#' in line:
                    line = line[:line.index('#')]
                # Check for pattern "INPUT(...)" and "OUTPUT(...)"
                line_syntax = re.match(r'^([A-Za-z_\$\[\]]+) ?\((.+)\)', line)
                if line_syntax:
                    if re.match(r'OUTPUT', line_syntax.group(1), re.IGNORECASE):
                        opt_node = line_syntax.group(2)
                        # If the node name does not start with a alphabetical letter, add a letter 'G' before it.
                        if not opt_node[0].isalpha():
                            opt_node = 'G' + opt_node
                        Circuit_graph.PO.append(Circuit_graph.name_to_node[opt_node])
                else:
                    # Process the gate connection line
                    line_syntax = re.match(r' *([a-zA-Z0-9_\$\[\]]+) *= *([a-zA-Z0-9_\[\]]+) *\( *(.+) *\)', line)
                    left_node = line_syntax.group(1)
                    # If the node name does not start with a alphabetical letter, add a letter 'G' before it.
                    if not left_node[0].isalpha():
                        left_node = 'G' + left_node

                    if re.match(r'NOT', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['NOT']
                    elif re.match(r'NAND', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['NAND']
                    elif re.match(r'AND', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['AND']
                    elif re.match(r'XNOR', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['XNOR']
                    elif re.match(r'NOR', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['NOR']
                    elif re.match(r'XOR', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['XOR']
                    elif re.match(r'OR', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['OR']
                    elif re.match(r'DFF', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['DFF']
                        Circuit_graph.PPI.append(Circuit_graph.find_node_by_name(left_node))
                    elif re.match(r'BUFF?', line_syntax.group(2), re.IGNORECASE):
                        Circuit_graph.find_node_by_name(left_node).gate_type = Circuit_graph.gateType['BUFF']
                    else:
                        print("New Logic Element in the following line!!!")
                        print(line)
                        exit(1)

                    right_nodes = re.split(r' *, *', line_syntax.group(3))
                    for node in right_nodes:
                        # If the node name does not start with a alphabetical letter, add a letter 'G' before it.
                        if not node[0].isalpha():
                            node = 'G' + node
                        Circuit_graph.connect_objectives_by_name(node, left_node)
    ipt.close()
    # Create the PPO list
    for node in Circuit_graph.PPI:
        assert len(node.fan_in_node) == 1
        Circuit_graph.PPO.append(node.fan_in_node[0])
    return Circuit_graph


###########################################################################
# Function name: ntk_levelization
# Note: Levelize the netlist. This function must be after parsing a netlist
# or after any modification to the Ntk class object
###########################################################################
def ntk_levelization(Circuit_graph, fic_enable=False):
    Circuit_graph.simulation_starting_obj = None
    Circuit_graph.simulation_ending_obj = None
    for node in Circuit_graph.object_list:
        # if node.topo_sort_index is None:
        node.topo_sort_index = len(node.fan_in_node)

    queue = [node for node in Circuit_graph.PI + Circuit_graph.KI]

    while len(queue):
        current_node = queue[0]
        for fan_out_node in current_node.fan_out_node:
            fan_out_node.topo_sort_index -= 1
            if fan_out_node.topo_sort_index == 0:
                queue.append(fan_out_node)
        if Circuit_graph.simulation_starting_obj is None:  # Set the starting node for simulation
            Circuit_graph.simulation_starting_obj = current_node
        if len(queue) == 1:  # Set the ending node for simulation
            assert (Circuit_graph.simulation_ending_obj is None)
            Circuit_graph.simulation_ending_obj = current_node
        else:  # Point the next node to the current one
            current_node.next_node = queue[1]
            queue[1].previous_node = current_node
        queue = queue[1:]
    for node in Circuit_graph.object_list:
        # assert(node.topo_sort_index == 0)
        if node.topo_sort_index != 0:
            print("Levelization error: %s" % node.name)
    if fic_enable:
        find_fan_in_cone(Circuit_graph)


###########################################################################
# Function name: ntk_to_bench
# Note: Output the Ntk class object to a .bench format netlist
###########################################################################
def ntk_to_bench(Circuit_graph, opt_file_path):  # Write circuit_graph to .bench file
    opt_file = open(opt_file_path, "w")
    zipped = zip([node.name for node in Circuit_graph.PI], Circuit_graph.PI)
    zipped = sorted(zipped)
    if len(zipped):  # This a circuit has any PI
        sorted_PI = list(zip(*zipped))[1]
        for node in sorted_PI:
            opt_file.write("INPUT(%s)\n" % node.name)
        for node in Circuit_graph.KI:
            opt_file.write("INPUT(%s)\n" % node.name)
        opt_file.write("\n")
    zipped = zip([node.name for node in Circuit_graph.PO], Circuit_graph.PO)
    zipped = sorted(zipped)
    if len(zipped):  # This a circuit has any PO
        sorted_PO = list(zip(*zipped))[1]
        for node in sorted_PO:
            opt_file.write("OUTPUT(%s)\n" % node.name)
        opt_file.write("\n")
    for node in Circuit_graph.object_list:
        if node.gate_type != Circuit_graph.gateType['IPT']:
            opt_file.write("%s = %s(" % (node.name, Circuit_graph.gateType_reverse[node.gate_type])),
            ipt_num = len(node.fan_in_node)
            for ipt_node in node.fan_in_node:
                ipt_num -= 1
                if ipt_num == 0:
                    opt_file.write("%s" % ipt_node.name),
                else:
                    opt_file.write("%s, " % ipt_node.name),
            opt_file.write(") \n")

    opt_file.close()


###########################################################################
# Function name: find_fan_in_cone
# Note: For each node, find all other nodes that are in the fan-in cone of
#       this node.
###########################################################################
def find_fan_in_cone(circuit_graph):  # Given a netlist, obtain the fan-in cone of each node in the netlist
    current_node = circuit_graph.simulation_starting_obj
    while current_node is not None:
        if current_node.gate_type != circuit_graph.gateType['DFF']:
            for ipt_node in current_node.fan_in_node:
                for temp in ipt_node.fan_in_cone:
                    if temp not in current_node.fan_in_cone:
                        current_node.fan_in_cone.append(temp)
                if ipt_node not in current_node.fan_in_cone:
                    current_node.fan_in_cone.append(ipt_node)
                if ipt_node.influence_by_key is True:
                    current_node.influence_by_key = True
        if current_node.influence_by_key is None:
            if current_node in circuit_graph.KI:
                current_node.influence_by_key = True
            else:
                current_node.influence_by_key = False
        current_node = current_node.next_node


###########################################################################
# Function name: seq_to_comb
# Note: Remove the DFFs in the netlist and output as a new file.
###########################################################################
def seq_to_comb(input_path, output_path):
    circuit_graph = ntk_parser(input_path)
    opt_file = open(output_path, "w")
    # Sort the PI list with alphabetical orders
    zipped = zip([node.name for node in circuit_graph.PI], circuit_graph.PI)
    zipped = sorted(zipped)
    if len(zipped):  # This a circuit has any PI
        sorted_PI = list(zip(*zipped))[1]
        for node in sorted_PI:
            opt_file.write("INPUT(%s)\n" % node.name)
        for node in circuit_graph.KI:
            opt_file.write("INPUT(%s)\n" % node.name)
    # If the I/O of the DFF is directly the PI/PO, add buffers
    pi_node_of_concern = []
    po_node_of_concern = []
    for node in circuit_graph.object_list:
        if node.gate_type == circuit_graph.gateType['DFF']:
            if node in circuit_graph.PO:
                po_node_of_concern.append(node)
            if node.fan_in_node[0] in circuit_graph.PI:
                pi_node_of_concern.append(node.fan_in_node[0])
    for node in po_node_of_concern:
        # Create the buffer
        temp = NtkObject(node.name)
        circuit_graph.add_object(temp, 'BUFF')
        # Replace I/O with this buffer
        circuit_graph.remove_node_from_PO(node)
        circuit_graph.add_PO(temp)
        # Update object_name_list
        circuit_graph.object_name_list[circuit_graph.object_list.index(temp)] = node.name
        circuit_graph.object_name_list[circuit_graph.object_list.index(node)] = node.name + 't'
        # Update the node name of the original I/O node
        node.name = node.name + 't'
        # Update the dict
        # From: node -> 'ori', temp -> 'ori', 'ori' -> temp
        # To: node -> 'ori_t', temp -> 'ori', 'ori' -> temp, 'ori_t' -> node
        circuit_graph.node_to_name[node] = node.name
        circuit_graph.name_to_node[node.name] = node
        # Re-route the fan-in and fan-out to the buffer
        temp_list = []
        for opt_node in node.fan_out_node:
            temp_list.append(opt_node)
        for opt_node in temp_list:
            circuit_graph.disconnect_objectives(node, opt_node)
            circuit_graph.connect_objectives(temp, opt_node)
        circuit_graph.connect_objectives(node, temp)

    for node in pi_node_of_concern:
        # Create the buffer
        temp = NtkObject(node.name)
        circuit_graph.add_object(temp, 'IPT')
        node.gate_type = circuit_graph.gateType['BUFF']
        # Replace I/O with this buffer
        circuit_graph.remove_node_from_PI(node)
        circuit_graph.add_PI(temp)
        # Update object_name_list
        circuit_graph.object_name_list[circuit_graph.object_list.index(temp)] = node.name
        circuit_graph.object_name_list[circuit_graph.object_list.index(node)] = node.name + 't'
        # Update the node name of the original I/O node
        node.name = node.name + 't'
        # Update the dict
        # From: node -> 'ori', temp -> 'ori', 'ori' -> temp
        # To: node -> 'ori_t', temp -> 'ori', 'ori' -> temp, 'ori_t' -> node
        circuit_graph.node_to_name[node] = node.name
        circuit_graph.name_to_node[node.name] = node
        # Re-route the fan-in and fan-out to the buffer
        temp_list = []
        for ipt_node in node.fan_in_node:
            temp_list.append(ipt_node)
        for ipt_node in temp_list:
            circuit_graph.disconnect_objectives(ipt_node, node)
            circuit_graph.connect_objectives(ipt_node, temp)
        circuit_graph.connect_objectives(temp, node)

    dff_ipt = []
    name_changed = []
    # Write the DFF-related input ports to file
    for node in circuit_graph.object_list:  # TODO: Create a DFF list in the circuit_graph class to save time
        if node.gate_type == circuit_graph.gateType['DFF']:
            opt_file.write("INPUT(%s)\n" % ('DF_' + node.name))
            name_changed.append(node)
            dff_ipt.append(node.fan_in_node[0].name)
            name_changed.append(node.fan_in_node[0])
    opt_file.write("\n")

    # Order the PO list and write the PO ports to file
    zipped = zip([node.name for node in circuit_graph.PO], circuit_graph.PO)
    zipped = sorted(zipped)
    if len(zipped):  # This a circuit has any PO
        sorted_PO = list(zip(*zipped))[1]
        for node in sorted_PO:
            opt_file.write("OUTPUT(%s)\n" % node.name)
    # Write the DFF-related output ports to file
    for node in dff_ipt:
        opt_file.write("OUTPUT(%s)\n" % ('DF_' + node))
    opt_file.write("\n")
    # Write the gate connection lines to file
    for node in circuit_graph.object_list:
        if node.gate_type != circuit_graph.gateType['IPT'] and node.gate_type != circuit_graph.gateType['DFF']:
            # print(node.name, node.gate_type)
            if node in name_changed:
                opt_file.write("%s = %s(" % ('DF_' + node.name, circuit_graph.gateType_reverse[node.gate_type])),
            else:
                opt_file.write("%s = %s(" % (node.name, circuit_graph.gateType_reverse[node.gate_type])),
            ipt_num = len(node.fan_in_node)
            for ipt_node in node.fan_in_node:
                ipt_num -= 1
                if ipt_num == 0:
                    if ipt_node in name_changed:
                        opt_file.write("%s" % ('DF_' + ipt_node.name)),
                    else:
                        opt_file.write("%s" % ipt_node.name),
                else:
                    if ipt_node in name_changed:
                        opt_file.write("%s, " % ('DF_' + ipt_node.name)),
                    else:
                        opt_file.write("%s, " % ipt_node.name),
            opt_file.write(") \n")

    opt_file.close()


###########################################################################
# Function name: ntk_levelization_seq
# Note: Levelize the sequential netlist. This function must be after
# parsing a netlist or after any modification to the Ntk class object
###########################################################################
def ntk_levelization_seq(Circuit_graph, fic_enable=False):
    Circuit_graph.simulation_starting_obj = None
    Circuit_graph.simulation_ending_obj = None
    for node in Circuit_graph.object_list:
        # if node.topo_sort_index is None:
        if node.gate_type == Circuit_graph.gateType['DFF']:
            node.topo_sort_index = 0
        else:
            node.topo_sort_index = len(node.fan_in_node)

    queue = [node for node in Circuit_graph.PI + Circuit_graph.KI + Circuit_graph.PPI]

    while len(queue):
        current_node = queue[0]
        for fan_out_node in current_node.fan_out_node:
            if fan_out_node.gate_type != Circuit_graph.gateType['DFF']:
                fan_out_node.topo_sort_index -= 1
                if fan_out_node.topo_sort_index == 0:
                    queue.append(fan_out_node)
        if Circuit_graph.simulation_starting_obj is None:  # Set the starting node for simulation
            Circuit_graph.simulation_starting_obj = current_node
        if len(queue) == 1:  # Set the ending node for simulation
            assert (Circuit_graph.simulation_ending_obj is None)
            Circuit_graph.simulation_ending_obj = current_node
        else:  # Point the next node to the current one
            current_node.next_node = queue[1]
            queue[1].previous_node = current_node
        queue = queue[1:]
    for node in Circuit_graph.object_list:
        # assert(node.topo_sort_index == 0)
        if node.topo_sort_index != 0:
            print("Levelization error: %s" % node.name)
    if fic_enable:
        find_fan_in_cone(Circuit_graph)
