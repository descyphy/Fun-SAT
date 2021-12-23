import subprocess
from collections import OrderedDict
import os

import Ntk_Parser
import Ntk_Simulator


###########################################################################
# Function name: circuit_to_module
# Note: Create the NuSMV module of a circuit
###########################################################################
def circuit_to_module(circuit_graph, initial_state, to_file, module_name):
    to_file.write('\nMODULE %s(' % module_name)
    for node in circuit_graph.PI:
        to_file.write('%s' % node.name)
        if circuit_graph.PI.index(node) == len(circuit_graph.PI) - 1 and len(circuit_graph.KI) == 0:
            break
        to_file.write(', ')
    for node in circuit_graph.KI:
        to_file.write('%s' % node.name)
        if circuit_graph.KI.index(node) == len(circuit_graph.KI) - 1:
            break
        to_file.write(', ')
    to_file.write(')\n')
    to_file.write('\tVAR\n')
    for node in circuit_graph.object_list:
        assert (len(node.fan_in_node) <= 2)
        if node.gate_type == circuit_graph.gateType['IPT']:
            pass
            # to_file.write('\t\t%s : boolean;\n' % node.name)
        elif node.gate_type == circuit_graph.gateType['NOT']:
            if node.fan_in_node[0].gate_type != circuit_graph.gateType['IPT']:
                to_file.write('\t\t%s : inv_gate(%s.output);\n' % (node.name, node.fan_in_node[0].name))
            else:
                to_file.write('\t\t%s : inv_gate(%s);\n' % (node.name, node.fan_in_node[0].name))
        elif node.gate_type == circuit_graph.gateType['BUFF']:
            if node.fan_in_node[0].gate_type != circuit_graph.gateType['IPT']:
                to_file.write('\t\t%s : buff_gate(%s.output);\n' % (node.name, node.fan_in_node[0].name))
            else:
                to_file.write('\t\t%s : buff_gate(%s);\n' % (node.name, node.fan_in_node[0].name))
        elif node.gate_type == circuit_graph.gateType['AND']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : and_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['NAND']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : nand_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['OR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : or_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['NOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : nor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['XOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : xor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['XNOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : xnor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['DFF']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if initial_state[circuit_graph.PPI.index(node)] == '1':
                to_file.write('\t\t%s : register_p(%s);\n' % (node.name, a))
            else:
                to_file.write('\t\t%s : register_n(%s);\n' % (node.name, a))


###########################################################################
# Function name: circuit_to_module_with_init_state
# Note: Create the NuSMV module of a circuit (states are module input)
###########################################################################
def circuit_to_module_with_init_state(circuit_graph, to_file, module_name):
    to_file.write('\nMODULE %s(' % module_name)
    for node in circuit_graph.PI:
        to_file.write('%s' % node.name)
        if circuit_graph.PI.index(node) == len(circuit_graph.PI) - 1 and len(circuit_graph.PPI) == 0:
            break
        to_file.write(', ')
    for node in circuit_graph.PPI:
        to_file.write('SMCis_%d' % circuit_graph.PPI.index(node))
        if circuit_graph.PPI.index(node) == len(circuit_graph.PPI) - 1:
            break
        to_file.write(', ')
    to_file.write(')\n')
    to_file.write('\tVAR\n')
    for node in circuit_graph.object_list:
        assert (len(node.fan_in_node) <= 2)
        if node.gate_type == circuit_graph.gateType['IPT']:
            pass
            # to_file.write('\t\t%s : boolean;\n' % node.name)
        elif node.gate_type == circuit_graph.gateType['NOT']:
            if node.fan_in_node[0].gate_type != circuit_graph.gateType['IPT']:
                to_file.write('\t\t%s : inv_gate(%s.output);\n' % (node.name, node.fan_in_node[0].name))
            else:
                to_file.write('\t\t%s : inv_gate(%s);\n' % (node.name, node.fan_in_node[0].name))
        elif node.gate_type == circuit_graph.gateType['BUFF']:
            if node.fan_in_node[0].gate_type != circuit_graph.gateType['IPT']:
                to_file.write('\t\t%s : buff_gate(%s.output);\n' % (node.name, node.fan_in_node[0].name))
            else:
                to_file.write('\t\t%s : buff_gate(%s);\n' % (node.name, node.fan_in_node[0].name))
        elif node.gate_type == circuit_graph.gateType['AND']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : and_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['NAND']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : nand_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['OR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : or_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['NOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : nor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['XOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : xor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['XNOR']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            if node.fan_in_node[1].gate_type == circuit_graph.gateType['IPT']:
                b = node.fan_in_node[1].name
            else:
                b = node.fan_in_node[1].name + '.output'
            to_file.write('\t\t%s : xnor_gate(%s, %s);\n' % (node.name, a, b))
        elif node.gate_type == circuit_graph.gateType['DFF']:
            if node.fan_in_node[0].gate_type == circuit_graph.gateType['IPT']:
                a = node.fan_in_node[0].name
            else:
                a = node.fan_in_node[0].name + '.output'
            to_file.write('\t\t%s : register(%s, SMCis_%d);\n' % (node.name, a, circuit_graph.PPI.index(node)))


###########################################################################
# Function name: comp_equiv_check_gen
# Note: Create the model for checking equivalence of two combinational
# circuits
###########################################################################
def comp_equiv_check_gen(original_circuit, encrypted_circuit, predicted_key):
    enc_graph = Ntk_Parser.ntk_parser(encrypted_circuit)
    ori_graph = Ntk_Parser.ntk_parser(original_circuit)

    lib_file = open('./src/nuxmv_gate.lib', 'r')
    lib_lines = lib_file.readlines()
    lib_file.close()

    to_file = open('circuit.smv', 'w')
    for line in lib_lines:
        to_file.write(line)

    circuit_to_module(enc_graph, '', to_file, 'enc_circuit')
    circuit_to_module(ori_graph, '', to_file, 'ori_circuit')

    to_file.write('\nMODULE main\n')
    to_file.write('\tVAR\n')
    for node in enc_graph.PI:
        to_file.write('\t\t%s : boolean;\n' % node.name)
    for node in enc_graph.KI:
        to_file.write('\t\t%s : boolean;\n' % node.name)

    to_file.write('\t\tenc : enc_circuit(')
    for node in enc_graph.PI:
        to_file.write('%s' % node.name)
        if enc_graph.PI.index(node) == len(enc_graph.PI) - 1 and len(enc_graph.KI) == 0:
            break
        to_file.write(', ')
    for node in enc_graph.KI:
        to_file.write('%s' % node.name)
        if enc_graph.KI.index(node) == len(enc_graph.KI) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')

    to_file.write('\t\tori : ori_circuit(')
    for node in ori_graph.PI:
        to_file.write('%s' % node.name)
        if ori_graph.PI.index(node) == len(ori_graph.PI) - 1 and len(ori_graph.KI) == 0:
            break
        to_file.write(', ')
    for node in ori_graph.KI:
        to_file.write('%s' % node.name)
        if ori_graph.KI.index(node) == len(ori_graph.KI) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')

    # Write Spec
    to_file.write('\nLTLSPEC G((')
    for node in enc_graph.KI:
        to_file.write('%s=bool(%s)' % (node.name, predicted_key[enc_graph.KI.index(node)]))
        if enc_graph.KI.index(node) == len(enc_graph.KI) - 1:
            break
        to_file.write(' & ')
    to_file.write(') -> (')
    for node in enc_graph.PO:
        to_file.write('enc.%s.output = ori.%s.output' % (node.name, node.name))
        if enc_graph.PO.index(node) == len(enc_graph.PO) - 1:
            break
        to_file.write(' & ')
    to_file.write('));\n')
    to_file.close()


###########################################################################
# Function name: seq_equiv_check_gen
# Note: Create the model for checking equivalence of two sequential
# circuits
###########################################################################
def seq_equiv_check_gen(original_circuit, encrypted_circuit, initial_state):
    enc_graph = Ntk_Parser.ntk_parser(encrypted_circuit)
    ori_graph = Ntk_Parser.ntk_parser(original_circuit)

    lib_file = open('./src/nuxmv_gate.lib', 'r')
    lib_lines = lib_file.readlines()
    lib_file.close()

    to_file = open('circuit.smv', 'w')
    for line in lib_lines:
        to_file.write(line)
    ori_init_state = initial_state[:len(ori_graph.PPI)]
    enc_init_state = initial_state[len(ori_graph.PPI):]
    # print(ori_init_state, enc_init_state)
    circuit_to_module(enc_graph, enc_init_state, to_file, 'enc_circuit')
    circuit_to_module(ori_graph, ori_init_state, to_file, 'ori_circuit')

    to_file.write('\nMODULE main\n')
    to_file.write('\tVAR\n')
    for node in enc_graph.PI:
        to_file.write('\t\t%s : boolean;\n' % node.name)
    for node in enc_graph.KI:
        to_file.write('\t\t%s : boolean;\n' % node.name)

    to_file.write('\t\tenc : enc_circuit(')
    for node in enc_graph.PI:
        to_file.write('%s' % node.name)
        if enc_graph.PI.index(node) == len(enc_graph.PI) - 1 and len(enc_graph.KI) == 0:
            break
        to_file.write(', ')
    for node in enc_graph.KI:
        to_file.write('%s' % node.name)
        if enc_graph.KI.index(node) == len(enc_graph.KI) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')

    to_file.write('\t\tori : ori_circuit(')
    for node in ori_graph.PI:
        to_file.write('%s' % node.name)
        if ori_graph.PI.index(node) == len(ori_graph.PI) - 1 and len(ori_graph.KI) == 0:
            break
        to_file.write(', ')
    for node in ori_graph.KI:
        to_file.write('%s' % node.name)
        if ori_graph.KI.index(node) == len(ori_graph.KI) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')

    # Write Spec
    to_file.write('\nLTLSPEC G(')
    for node in enc_graph.PO:
        to_file.write('enc.%s.output = ori.%s.output' % (node.name, node.name))
        if enc_graph.PO.index(node) == len(enc_graph.PO) - 1:
            break
        to_file.write(' & ')
    to_file.write(');\n')
    to_file.close()


def key_to_initial_state(encrypted_netlist, predicted_key, key_length):
    seq_graph = Ntk_Parser.ntk_parser(encrypted_netlist)
    Ntk_Parser.ntk_levelization_seq(seq_graph)
    # Prepare the input to the simulation
    ipt_pattern = []
    key_pattern = []
    for ind in range(key_length + 1):
        if ind == 0:
            temp_pattern = ''
            for node in seq_graph.PI:
                temp_pattern += '1'
            ipt_pattern.append(temp_pattern)
            key_pattern.append('')
        else:
            key_seq = predicted_key[(len(seq_graph.PI) - 1) * (ind - 1): (len(seq_graph.PI) - 1) * ind]
            reset_idx = seq_graph.PI.index(seq_graph.find_node_by_name('reset'))
            ipt_pattern.append(key_seq[:reset_idx] + '0' + key_seq[reset_idx:])
            key_pattern.append('')
    _ = Ntk_Simulator.simulate_seq(seq_graph, ipt_pattern, key_pattern, key_length + 1)  # TODO: Use VCS instead
    initial_state = OrderedDict()
    for node in seq_graph.PPO:
        # print(node.name, node.value)
        initial_state[node.name] = int(node.value)
    return seq_graph, initial_state


def umc(encrypted_circuit, encrypted_circuit_c, key_len, dip_list, odip_list, nuxmv_path, model_ready=False, folder_path=None):
    if not model_ready:  # If BMC is called before UMC, then skip the following block
        # Read the netlists before and after unrolling
        enc_graph = Ntk_Parser.ntk_parser(encrypted_circuit)
        enc_graph_c = Ntk_Parser.ntk_parser(encrypted_circuit_c)

        # Write the lib cells to model
        lib_file = open('./src/nuxmv_gate.lib', 'r')
        lib_lines = lib_file.readlines()
        lib_file.close()
        if folder_path is None:
            to_file = open('circuit.smv', 'w')
        else:
            to_file = open(os.path.join(folder_path, 'circuit.smv'), 'w')
        for line in lib_lines:
            to_file.write(line)

        # Write the circuit modules to models
        circuit_to_module(enc_graph_c, '', to_file, 'unrolled_circuit')
        circuit_to_module_with_init_state(enc_graph, to_file, 'enc_circuit')

        # Write the main module
        to_file.write('\nMODULE main\n')
        to_file.write('\tVAR\n')
        for node in enc_graph.PI:
            to_file.write('\t\t%s : boolean;\n' % node.name)
        for ind in range(len(enc_graph.PI) * key_len):
            to_file.write('\t\ta_keyinput%d : boolean;\n' % ind)
            to_file.write('\t\tb_keyinput%d : boolean;\n' % ind)
        # Create miter unrolled circuit copies to record the DIPs
        for ind in range(len(dip_list)):
            to_file.write('\t\tdip_a%d : unrolled_circuit(' % ind)
            for ind2 in range(len(enc_graph_c.PI)):
                to_file.write('bool(%s)' % dip_list[ind][ind2])
                if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph_c.KI) == 0:
                    break
                to_file.write(', ')
            for ind2 in range(len(enc_graph_c.KI)):
                to_file.write('a_keyinput%d' % ind2)
                if ind2 == len(enc_graph_c.KI) - 1:
                    break
                to_file.write(', ')
            to_file.write(');\n')

            to_file.write('\t\tdip_b%d : unrolled_circuit(' % ind)
            for ind2 in range(len(enc_graph_c.PI)):
                to_file.write('bool(%s)' % dip_list[ind][ind2])
                if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph_c.KI) == 0:
                    break
                to_file.write(', ')
            for ind2 in range(len(enc_graph_c.KI)):
                to_file.write('b_keyinput%d' % ind2)
                if ind2 == len(enc_graph_c.KI) - 1:
                    break
                to_file.write(', ')
            to_file.write(');\n')
        # Create two encrypted circuit copies
        to_file.write('\t\tenc_a : enc_circuit(')
        for ind2 in range(len(enc_graph.PI)):
            to_file.write('%s' % enc_graph.PI[ind2].name)
            if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph.PPI) == 0:
                break
            to_file.write(', ')
        for ind2 in range(len(enc_graph.PPO)):
            # print(enc_graph.PPO[ind2].name)
            to_file.write('dip_a0.DF_%s__%d.output' % (enc_graph.PPO[ind2].name, key_len))
            if ind2 == len(enc_graph.PPO) - 1:
                break
            to_file.write(', ')
        to_file.write(');\n')
        to_file.write('\t\tenc_b : enc_circuit(')
        for ind2 in range(len(enc_graph.PI)):
            to_file.write('%s' % enc_graph.PI[ind2].name)
            if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph.PPI) == 0:
                break
            to_file.write(', ')
        for ind2 in range(len(enc_graph.PPO)):
            to_file.write('dip_b0.DF_%s__%d.output' % (enc_graph.PPO[ind2].name, key_len))
            if ind2 == len(enc_graph.PPO) - 1:
                break
            to_file.write(', ')
        to_file.write(');\n')
        # Compare a_keyinput and b_keyinput
        to_file.write('\tINVAR ')

        for ind in range(len(dip_list)):
            for ind2 in range(len(enc_graph_c.PO)):
                if odip_list[ind][ind2] == '1':
                    to_file.write('dip_a%d.%s.output' % (ind, enc_graph_c.PO[ind2].name))
                else:
                    to_file.write('(!dip_a%d.%s.output)' % (ind, enc_graph_c.PO[ind2].name))
                to_file.write(' & ')
                if odip_list[ind][ind2] == '1':
                    to_file.write('dip_b%d.%s.output' % (ind, enc_graph_c.PO[ind2].name))
                else:
                    to_file.write('(!dip_b%d.%s.output)' % (ind, enc_graph_c.PO[ind2].name))
                if ind2 == len(enc_graph_c.PO) - 1 and ind == len(dip_list) - 1:
                    break
                to_file.write(' & ')
        to_file.write(';\n')

        # Write Spec
        to_file.write('\nINVARSPEC ')
        for node in enc_graph.PO:
            to_file.write('enc_a.%s.output = enc_b.%s.output' % (node.name, node.name))
            if enc_graph.PO.index(node) == len(enc_graph.PO) - 1:
                break
            to_file.write(' & ')
        to_file.write(';\n')
        to_file.close()

    if folder_path is None:
        command = [nuxmv_path, '-int', 'circuit.smv']
    else:
        command = [nuxmv_path, '-int', os.path.join(folder_path, 'circuit.smv')]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate(input=('go_bmc\ncheck_invar_bmc_itp -a mcmillan2 -k 0\nquit').encode())[0].decode("utf-8")
    # print(output)
    if 'is true.' in output:
        return True
    elif 'is false' in output:
        return False
    else:
        return None


def bmc(encrypted_circuit, encrypted_circuit_c, key_len, dip_list, odip_list, depth, nuxmv_path, folder_path=None):
    # Read the netlists before and after unrolling
    enc_graph = Ntk_Parser.ntk_parser(encrypted_circuit)
    enc_graph_c = Ntk_Parser.ntk_parser(encrypted_circuit_c)

    # Write the lib cells to model
    lib_file = open('./src/nuxmv_gate.lib', 'r')
    lib_lines = lib_file.readlines()
    lib_file.close()
    if folder_path is None:
        to_file = open('circuit.smv', 'w')
    else:
        to_file = open(os.path.join(folder_path, 'circuit.smv'), 'w')
    for line in lib_lines:
        to_file.write(line)

    # Write the circuit modules to models
    circuit_to_module(enc_graph_c, '', to_file, 'unrolled_circuit')
    circuit_to_module_with_init_state(enc_graph, to_file, 'enc_circuit')

    # Write the main module
    to_file.write('\nMODULE main\n')
    to_file.write('\tVAR\n')
    for node in enc_graph.PI:
        to_file.write('\t\t%s : boolean;\n' % node.name)
    for ind in range(len(enc_graph.PI) * key_len):
        to_file.write('\t\ta_keyinput%d : boolean;\n' % ind)
        to_file.write('\t\tb_keyinput%d : boolean;\n' % ind)
    # Create miter unrolled circuit copies to record the DIPs
    for ind in range(len(dip_list)):
        to_file.write('\t\tdip_a%d : unrolled_circuit(' % ind)
        for ind2 in range(len(enc_graph_c.PI)):
            to_file.write('bool(%s)' % dip_list[ind][ind2])
            if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph_c.KI) == 0:
                break
            to_file.write(', ')
        for ind2 in range(len(enc_graph_c.KI)):
            to_file.write('a_keyinput%d' % ind2)
            if ind2 == len(enc_graph_c.KI) - 1:
                break
            to_file.write(', ')
        to_file.write(');\n')

        to_file.write('\t\tdip_b%d : unrolled_circuit(' % ind)
        for ind2 in range(len(enc_graph_c.PI)):
            to_file.write('bool(%s)' % dip_list[ind][ind2])
            if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph_c.KI) == 0:
                break
            to_file.write(', ')
        for ind2 in range(len(enc_graph_c.KI)):
            to_file.write('b_keyinput%d' % ind2)
            if ind2 == len(enc_graph_c.KI) - 1:
                break
            to_file.write(', ')
        to_file.write(');\n')
    # Create two encrypted circuit copies
    to_file.write('\t\tenc_a : enc_circuit(')
    for ind2 in range(len(enc_graph.PI)):
        to_file.write('%s' % enc_graph.PI[ind2].name)
        if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph.PPI) == 0:
            break
        to_file.write(', ')
    for ind2 in range(len(enc_graph.PPO)):
        # print(enc_graph.PPO[ind2].name)
        to_file.write('dip_a0.DF_%s__%d.output' % (enc_graph.PPO[ind2].name, key_len))
        if ind2 == len(enc_graph.PPO) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')
    to_file.write('\t\tenc_b : enc_circuit(')
    for ind2 in range(len(enc_graph.PI)):
        to_file.write('%s' % enc_graph.PI[ind2].name)
        if ind2 == len(enc_graph_c.PI) - 1 and len(enc_graph.PPI) == 0:
            break
        to_file.write(', ')
    for ind2 in range(len(enc_graph.PPO)):
        to_file.write('dip_b0.DF_%s__%d.output' % (enc_graph.PPO[ind2].name, key_len))
        if ind2 == len(enc_graph.PPO) - 1:
            break
        to_file.write(', ')
    to_file.write(');\n')
    # Compare a_keyinput and b_keyinput
    to_file.write('\tINVAR ')

    for ind in range(len(dip_list)):
        for ind2 in range(len(enc_graph_c.PO)):
            if odip_list[ind][ind2] == '1':
                to_file.write('dip_a%d.%s.output' % (ind, enc_graph_c.PO[ind2].name))
            else:
                to_file.write('(!dip_a%d.%s.output)' % (ind, enc_graph_c.PO[ind2].name))
            to_file.write(' & ')
            if odip_list[ind][ind2] == '1':
                to_file.write('dip_b%d.%s.output' % (ind, enc_graph_c.PO[ind2].name))
            else:
                to_file.write('(!dip_b%d.%s.output)' % (ind, enc_graph_c.PO[ind2].name))
            if ind2 == len(enc_graph_c.PO) - 1 and ind == len(dip_list) - 1:
                break
            to_file.write(' & ')
    to_file.write(';\n')

    # Write Spec
    to_file.write('\nINVARSPEC ')
    for node in enc_graph.PO:
        to_file.write('enc_a.%s.output = enc_b.%s.output' % (node.name, node.name))
        if enc_graph.PO.index(node) == len(enc_graph.PO) - 1:
            break
        to_file.write(' & ')
    to_file.write(';\n')
    to_file.close()

    if folder_path is None:
        command = [nuxmv_path, '-int', 'circuit.smv']
    else:
        command = [nuxmv_path, '-int', os.path.join(folder_path, 'circuit.smv')]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate(input=('go_bmc\ncheck_invar_bmc_itp -a mcmillan2 -k ' + str(depth) + '\nquit').encode())[
        0].decode("utf-8")
    # print(output)
    if 'is true.' in output:
        return True
    elif 'is false' in output:
        return False
    else:
        return False
