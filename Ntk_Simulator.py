# Executed in Python 3.6
import random
import time
from typing import List

import Ntk_Parser
import Ntk_Struct


###########################################################################
# Function name: simulate
# Note: Simulate the combinational circuit with input and keyinput values
###########################################################################
def simulate(circuit_graph: Ntk_Struct.Ntk, ipt_pattern: str, key_pattern: str):
    if len(ipt_pattern) != len(circuit_graph.PI):  # Check the lenghth of the input pattern
        print("Less number of bits in the pattern")
        quit()

    i = 0
    for ipt_node in circuit_graph.PI:  # Assign PI node values. Input pattern format: LSB(left) to MSB (right)
        if ipt_pattern[i] not in ['0', '1']:
            print("Improper pattern ")
            quit()
        ipt_node.value = int(ipt_pattern[i])
        i = i + 1
    i = 0
    while len(key_pattern) < len(circuit_graph.KI):  # FIXME: Temporary for uc_obf
        key_pattern += '0'
    for key_node in circuit_graph.KI:  # Assign KI node values. Key pattern format: LSB(left) to MSB (right)
        if key_pattern[i] not in ['0', '1']:
            print("Improper pattern ")
            quit()
        key_node.value = int(key_pattern[i])
        i = i + 1
    # Check if the circuit is levelized before simulation
    if circuit_graph.simulation_starting_obj is not None:
        current_obj = circuit_graph.simulation_starting_obj
    else:
        print("Network has not been levelized yet. Levelizing now... ")
        Ntk_Parser.ntk_levelization(circuit_graph)
        print("Network has not been levelized yet. ")
        current_obj = circuit_graph.simulation_starting_obj

    # Simulate the logic baseed on the simulation order
    while current_obj is not None:
        if current_obj.gate_type == circuit_graph.gateType['NOT']:
            assert (len(current_obj.fan_in_node) == 1)
            current_obj.value = 1 - int(current_obj.fan_in_node[0].value)
        elif current_obj.gate_type == circuit_graph.gateType['BUFF']:
            assert (len(current_obj.fan_in_node) == 1)
            current_obj.value = int(current_obj.fan_in_node[0].value)
        else:
            gateIn = []
            for fan_in_obj in current_obj.fan_in_node:
                gateIn.append(fan_in_obj.value)
            if current_obj.gate_type == circuit_graph.gateType['NAND']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value &= gateIn[i]
                current_obj.value = 1 - current_obj.value
            elif current_obj.gate_type == circuit_graph.gateType['AND']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value &= gateIn[i]
            elif current_obj.gate_type == circuit_graph.gateType['NOR']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value |= gateIn[i]
                current_obj.value = 1 - current_obj.value
            elif current_obj.gate_type == circuit_graph.gateType['OR']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value |= gateIn[i]
            elif current_obj.gate_type == circuit_graph.gateType['XNOR']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value ^= gateIn[i]
                current_obj.value = 1 - current_obj.value
            elif current_obj.gate_type == circuit_graph.gateType['XOR']:
                current_obj.value = gateIn[0]
                if len(gateIn) > 1:
                    for i in range(1, len(gateIn)):
                        current_obj.value ^= gateIn[i]
        current_obj = current_obj.next_node


###########################################################################
# Function name: fc_calculator
# Note: Calculate the Functional Corruptibility of an encrypted circuit
###########################################################################
def fc_calculator(Circuit_graph, correct_key: str, simulation_count):  # The functional corruptibility calculator
    random.seed(time.time())
    count = 0
    for iteration in range(simulation_count):
        ipt_pattern = ''
        for i in range(len(Circuit_graph.PI)):
            token = random.randint(0, 1)
            if token:
                ipt_pattern += '1'
            else:
                ipt_pattern += '0'
        if len(Circuit_graph.KI) <= 0:
            return 0.0
        while 1:
            key_pattern = ''
            for i in range(len(Circuit_graph.KI)):
                token = random.randint(0, 1)
                if token:
                    key_pattern += '1'
                else:
                    key_pattern += '0'
            if key_pattern != correct_key:
                break

        simulate(Circuit_graph, ipt_pattern, correct_key)
        correct_output = ''
        current_output = ''
        for node in Circuit_graph.PO:
            correct_output += str(node.value)

        simulate(Circuit_graph, ipt_pattern, key_pattern)
        for node in Circuit_graph.PO:
            current_output += str(node.value)
        if correct_output != current_output:
            count += 1

    return 1.0 * count / simulation_count


###########################################################################
# Function name: simulate_seq
# Note: Simulate the sequential circuit with input and keyinput values
###########################################################################
def simulate_seq(circuit_graph: Ntk_Struct.Ntk, ipt_pattern: List[str], key_pattern: List[str], cycle_count: int,
                 verbose: bool = False):
    po_sequence = ''
    for iter_idx in range(cycle_count):
        if verbose:
            print('Clock %d: ' % iter_idx)
        if len(ipt_pattern[iter_idx]) != len(circuit_graph.PI):  # Check the lenghth of the input pattern
            print("Less number of bits in the pattern")
            quit()
        if iter_idx == 0:  # Reset the DFF output at the first cycle
            for ipt_node in circuit_graph.PPI:
                ipt_node.value = int(0)
        else:  # Pass from D to Q for all DFFs
            i = 0
            for ipt_node in circuit_graph.PPI:
                ipt_node.value = int(circuit_graph.PPO[i].value)
                i += 1
        i = 0
        for ipt_node in circuit_graph.PI:  # Assign PI node values. Input pattern format: LSB(left) to MSB (right)
            # if ipt_pattern[iter_idx][i] not in ['0', '1']:
            # 	print("Improper pattern ")
            # 	quit()
            ipt_node.value = int(ipt_pattern[iter_idx][i])
            i += 1
        i = 0
        while len(key_pattern[iter_idx]) < len(circuit_graph.KI):  # FIXME: Temporary for uc_obf
            key_pattern[iter_idx] += '0'
        for key_node in circuit_graph.KI:  # Assign KI node values. Key pattern format: LSB(left) to MSB (right)
            # if key_pattern[iter_idx][i] not in ['0', '1']:
            # 	print("Improper pattern ")
            # 	quit()
            key_node.value = int(key_pattern[iter_idx][i])
            i += 1
        # Check if the circuit is levelized before simulation
        if circuit_graph.simulation_starting_obj is not None:
            current_obj = circuit_graph.simulation_starting_obj
        else:
            print("Network has not been levelized yet. Levelizing now... ")
            Ntk_Parser.ntk_levelization(circuit_graph)
            print("Network has not been levelized yet. ")
            current_obj = circuit_graph.simulation_starting_obj

        # Simulate the logic baseed on the simulation order
        while current_obj is not None:
            if current_obj.gate_type == circuit_graph.gateType['NOT']:
                assert (len(current_obj.fan_in_node) == 1)
                current_obj.value = 1 - int(current_obj.fan_in_node[0].value)
            elif current_obj.gate_type == circuit_graph.gateType['BUFF']:
                assert (len(current_obj.fan_in_node) == 1)
                current_obj.value = int(current_obj.fan_in_node[0].value)
            else:
                gateIn = []
                for fan_in_obj in current_obj.fan_in_node:
                    gateIn.append(fan_in_obj.value)
                if current_obj.gate_type == circuit_graph.gateType['NAND']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value &= gateIn[i]
                    current_obj.value = 1 - current_obj.value
                elif current_obj.gate_type == circuit_graph.gateType['AND']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value &= gateIn[i]
                elif current_obj.gate_type == circuit_graph.gateType['NOR']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value |= gateIn[i]
                    current_obj.value = 1 - current_obj.value
                elif current_obj.gate_type == circuit_graph.gateType['OR']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value |= gateIn[i]
                elif current_obj.gate_type == circuit_graph.gateType['XNOR']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value ^= gateIn[i]
                    current_obj.value = 1 - current_obj.value
                elif current_obj.gate_type == circuit_graph.gateType['XOR']:
                    current_obj.value = gateIn[0]
                    if len(gateIn) > 1:
                        for i in range(1, len(gateIn)):
                            current_obj.value ^= gateIn[i]
            current_obj = current_obj.next_node
        if verbose:
            print('PI: ', end='')
            for node in circuit_graph.PI:
                print('%d' % node.value, end='')
            print(' ', end='')
            print('PO: ', end='')
            for node in circuit_graph.PO:
                print('%d' % node.value, end='')
            print(' ', end='')
            print('PPI: ', end='')
            for node in circuit_graph.PPI:
                print('%d' % node.value, end='')
            print(' ', end='')
            print('PPO: ', end='')
            for node in circuit_graph.PPO:
                print('%d' % node.value, end='')
            print(' ')
        for node in circuit_graph.PO:
            po_sequence += str(node.value)
    return po_sequence
