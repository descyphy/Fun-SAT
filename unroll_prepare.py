import Ntk_Parser
import Ntk_Struct


###########################################################################
# Function name: prepare_ori
# Note: Prepare the original netlist for the SAT attack.
###########################################################################
def prepare_ori(input_path, output_path, level):
    new_graph = Ntk_Struct.Ntk()
    temp_graph = []
    for i in range(level):
        temp_graph.append(Ntk_Parser.ntk_parser(input_path))
        # print(input_path)
        to_be_deleted = []
        for ipt_node in temp_graph[i].PI:
            if len(ipt_node.fan_out_node) == 0:
                to_be_deleted.append(ipt_node)
        for opt_node in temp_graph[i].PO:
            # print(opt_node.name)
            if len(opt_node.fan_in_node) == 0:
                to_be_deleted.append(opt_node)
        for node in to_be_deleted:
            temp_graph[i].remove_object(node)
        # Find a PI node to use as constant source
        for ipt_node in temp_graph[i].PI:
            if 'reset' != ipt_node.name and 'DF_' not in ipt_node.name:
                the_PI = ipt_node
                break
        # Create the inverse of this PI
        the_PI_not = Ntk_Struct.NtkObject(the_PI.name + '_not')
        temp_graph[i].add_object(the_PI_not, 'NOT')
        temp_graph[i].connect_objectives(the_PI, the_PI_not)
        if i == 0:
            # Create XOR(the_PI, the_PI_not) to make a constant 1
            xnor = Ntk_Struct.NtkObject(the_PI.name + '_xnor')
            temp_graph[i].add_object(xnor, 'XNOR')
            temp_graph[i].connect_objectives(the_PI, xnor)
            temp_graph[i].connect_objectives(the_PI_not, xnor)
            xor = Ntk_Struct.NtkObject(xnor.name + '_not')
            temp_graph[i].add_object(xor, 'NOT')
            temp_graph[i].connect_objectives(xnor, xor)
            # Replace reset with a constant 1
            if 'reset' in temp_graph[i].object_name_list:
                reset_ind = temp_graph[i].object_name_list.index('reset')
                reset = temp_graph[i].object_list[reset_ind]
                temp_node_list = []
                for opt_node in reset.fan_out_node:
                    temp_node_list.append(opt_node)
                for opt_node in temp_node_list:
                    temp_graph[i].disconnect_objectives(reset, opt_node)
                    temp_graph[i].connect_objectives(xor, opt_node)
                temp_graph[i].remove_object(reset)
        else:
            # Create XNOR(the_PI, the_PI_not) to make a constant 0
            xnor = Ntk_Struct.NtkObject(the_PI.name + '_xnor')
            temp_graph[i].add_object(xnor, 'XNOR')
            temp_graph[i].connect_objectives(the_PI, xnor)
            temp_graph[i].connect_objectives(the_PI_not, xnor)
            # Replace reset with a constant 0
            if 'reset' in temp_graph[i].object_name_list:
                reset_ind = temp_graph[i].object_name_list.index('reset')
                reset = temp_graph[i].object_list[reset_ind]
                temp_node_list = []
                for opt_node in reset.fan_out_node:
                    temp_node_list.append(opt_node)
                for opt_node in temp_node_list:
                    temp_graph[i].disconnect_objectives(reset, opt_node)
                    temp_graph[i].connect_objectives(xnor, opt_node)
                temp_graph[i].remove_object(reset)
        if i == 0:  # If this is the first copy
            # Connect the pseudo PI to zero
            to_be_deleted = []
            for ipt_node in temp_graph[i].PI:
                if 'DF_' in ipt_node.name:
                    to_be_deleted.append(ipt_node)
                    opt_list = []
                    for opt in ipt_node.fan_out_node:
                        opt_list.append(opt)
                    for opt in opt_list:
                        temp_graph[i].disconnect_objectives(ipt_node, opt)
                        temp_graph[i].connect_objectives(xnor, opt)
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PI(node)
                temp_graph[i].remove_object(node)

        else:
            # Connect the pseudo PI to the previous level
            ind = 0
            to_be_deleted = []
            for ipt_node in temp_graph[i].PI:
                if 'DF_' in ipt_node.name:
                    to_be_deleted.append(ipt_node)
                    opt_list = []
                    for opt in ipt_node.fan_out_node:
                        opt_list.append(opt)
                    # print(ind, len(ppo))
                    for opt in opt_list:
                        temp_graph[i].disconnect_objectives(ipt_node, opt)
                        temp_graph[i].connect_objectives(ppo[ind], opt)
                    ind += 1
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PI(node)
                temp_graph[i].remove_object(node)
        ppo = []
        if i == level - 1:  # If this is the last copy
            to_be_deleted = []
            for opt_node in temp_graph[i].PO:
                if 'DF_' in opt_node.name:
                    to_be_deleted.append(opt_node)
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PO(node)
        else:
            # Connect the pseudo PO to the next level (will be implemented in the next iteration)
            to_be_deleted = []
            for opt_node in temp_graph[i].PO:
                if 'DF_' in opt_node.name:
                    ppo.append(opt_node)
                    # print(i, len(temp_graph[i].PO), len(ppo))
                    # print('From PO: %d, %s' % (len(ppo), opt_node.name))
                    to_be_deleted.append(opt_node)
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PO(node)
        # Connect the PIs in the first stage to the second state which is the functional stage
        if i == 0:
            reroute_pi = []
            # Hide the PO and reroute the PI
            temp_graph[i].PO = []
            for ipt_node in temp_graph[i].PI:
                reroute_pi.append(ipt_node)
            temp_graph[i].PI = []
        # Change node names and copy this copy to the whole top level graph
        for node_ind in range(len(temp_graph[i].object_list)):
            if i != 0:
                temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name + '_' + str(i - 1)
                temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_name_list[node_ind] + '_' + str(i - 1)
                # if '[' in temp_graph[i].object_name_list[node_ind] or ']' in temp_graph[i].object_name_list[node_ind]:
                #     temp_graph[i].object_name_list[node_ind] = 'yh_' + str(new_graph.available_node_index)
                #     temp_graph[i].object_list[node_ind].name = 'yh_' + str(new_graph.available_node_index)
                #     new_graph.available_node_index += 1
                if '[' in temp_graph[i].object_name_list[node_ind]:
                    temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace('[',
                                                                                                                'q')
                    temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace('[',
                                                                                                                'q')
                if ']' in temp_graph[i].object_name_list[node_ind]:
                    temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace(']',
                                                                                                                'p')
                    temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace(']',
                                                                                                                'p')
                new_graph.object_list.append(temp_graph[i].object_list[node_ind])
                new_graph.object_name_list.append(temp_graph[i].object_name_list[node_ind])
            else:
                temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name + '_t'
                temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_name_list[node_ind] + '_t'
                # if '[' in temp_graph[i].object_name_list[node_ind] or ']' in temp_graph[i].object_name_list[node_ind]:
                #     temp_graph[i].object_name_list[node_ind] = 'yh_' + str(new_graph.available_node_index)
                #     temp_graph[i].object_list[node_ind].name = 'yh_' + str(new_graph.available_node_index)
                #     new_graph.available_node_index += 1
                if '[' in temp_graph[i].object_name_list[node_ind]:
                    temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace('[',
                                                                                                                'q')
                    temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace('[',
                                                                                                                'q')
                if ']' in temp_graph[i].object_name_list[node_ind]:
                    temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace(']',
                                                                                                                'p')
                    temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace(']',
                                                                                                                'p')
                new_graph.object_list.append(temp_graph[i].object_list[node_ind])
                new_graph.object_name_list.append(temp_graph[i].object_name_list[node_ind])
        for node in temp_graph[i].PI:
            new_graph.PI.append(node)
        for node in temp_graph[i].PO:
            new_graph.PO.append(node)
        for node in temp_graph[i].KI:
            new_graph.KI.append(node)
        # Connect the PIs in the first stage to the second state which is the functional stage (cont.)
        if i == 1:
            # print(len(reroute_pi), len(temp_graph[i].PI))
            assert len(reroute_pi) == len(temp_graph[i].PI)
            for j in range(len(reroute_pi)):
                reroute_pi[j].gate_type = temp_graph[i].gateType['BUFF']
                new_graph.connect_objectives(temp_graph[i].PI[j], reroute_pi[j])
    Ntk_Parser.ntk_to_bench(new_graph, output_path)


###########################################################################
# Function name: prepare_enc
# Note: Prepare the encrypted netlist for the SAT attack.
###########################################################################
def prepare_enc(input_path, output_path, level_enc, level_func):
    new_graph = Ntk_Struct.Ntk()
    temp_graph = []
    PI_len = None  # This is the number of PI ports for each circuit copy except for the reset port
    for i in range(level_enc):
        temp_graph.append(Ntk_Parser.ntk_parser(input_path))
        if i == 0:
            PI_len = 0
            for node in temp_graph[0].PI:
                if 'reset' not in node.name and 'DF_' not in node.name:
                    PI_len += 1
        to_be_deleted = []
        for ipt_node in temp_graph[i].PI:
            if len(ipt_node.fan_out_node) == 0:
                to_be_deleted.append(ipt_node)
        for opt_node in temp_graph[i].PO:
            if len(opt_node.fan_in_node) == 0:
                to_be_deleted.append(opt_node)
        for node in to_be_deleted:
            temp_graph[i].remove_object(node)
        # Find a PI node to use as constant source
        for ipt_node in temp_graph[i].PI:
            if 'reset' not in ipt_node.name and 'DF_' not in ipt_node.name:
                the_PI = ipt_node
                break
        # Create the inverse of this PI
        the_PI_not = Ntk_Struct.NtkObject(the_PI.name + '_not')
        temp_graph[i].add_object(the_PI_not, 'NOT')
        temp_graph[i].connect_objectives(the_PI, the_PI_not)
        if i == 0:
            # Create XNOR(the_PI, the_PI_not) to make a constant 0
            xnor = Ntk_Struct.NtkObject(the_PI.name + '_xnor')
            temp_graph[i].add_object(xnor, 'XNOR')
            temp_graph[i].connect_objectives(the_PI, xnor)
            temp_graph[i].connect_objectives(the_PI_not, xnor)
            xor = Ntk_Struct.NtkObject(xnor.name + '_not')
            temp_graph[i].add_object(xor, 'NOT')
            temp_graph[i].connect_objectives(xnor, xor)
            # Replace reset with a constant 1
            reset_ind = temp_graph[i].object_name_list.index('reset')
            reset = temp_graph[i].object_list[reset_ind]
            temp_node_list = []
            for opt_node in reset.fan_out_node:
                temp_node_list.append(opt_node)
            for opt_node in temp_node_list:
                temp_graph[i].disconnect_objectives(reset, opt_node)
                temp_graph[i].connect_objectives(xor, opt_node)
            temp_graph[i].remove_object(reset)
        else:
            # Create XNOR(the_PI, the_PI_not) to make a constant 0
            xnor = Ntk_Struct.NtkObject(the_PI.name + '_xnor')
            temp_graph[i].add_object(xnor, 'XNOR')
            temp_graph[i].connect_objectives(the_PI, xnor)
            temp_graph[i].connect_objectives(the_PI_not, xnor)
            # Replace reset with a constant 0
            reset_ind = temp_graph[i].object_name_list.index('reset')
            reset = temp_graph[i].object_list[reset_ind]
            temp_node_list = []
            for opt_node in reset.fan_out_node:
                temp_node_list.append(opt_node)
            for opt_node in temp_node_list:
                temp_graph[i].disconnect_objectives(reset, opt_node)
                temp_graph[i].connect_objectives(xnor, opt_node)
            temp_graph[i].remove_object(reset)
        # # Replace the seed input with constant values
        # if '1' in seed:
        #     # Create const 1
        #     xor = Ntk_Struct.NtkObject(the_PI.name + '_xor')
        #     temp_graph[i].add_object(xor, 'NOT')
        #     temp_graph[i].connect_objectives(xnor, xor)
        # to_be_deleted = []
        # for ipt_node in temp_graph[i].PI:
        #     if 'seed[' in ipt_node.name and 'bar' not in ipt_node.name:
        #         to_be_deleted.append(ipt_node)
        #         temp_node_list = []
        #         for opt_node in ipt_node.fan_out_node:
        #             temp_node_list.append(opt_node)
        #         for opt_node in temp_node_list:
        #             temp_graph[i].disconnect_objectives(ipt_node, opt_node)
        #             if seed[-1 - int(ipt_node.name[ipt_node.name.index('[') + 1: ipt_node.name.index(']')])] == '0':
        #                 temp_graph[i].connect_objectives(xnor, opt_node)
        #             else:
        #                 temp_graph[i].connect_objectives(xor, opt_node)
        # for ipt_node in to_be_deleted:
        #     temp_graph[i].remove_object(ipt_node)

        if i == 0:  # If this is the first copy
            # Connect the pseudo PI to zero
            to_be_deleted = []
            for ipt_node in temp_graph[i].PI:
                if 'DF_' in ipt_node.name:
                    to_be_deleted.append(ipt_node)
                    opt_list = []
                    for opt in ipt_node.fan_out_node:
                        opt_list.append(opt)
                    for opt in opt_list:
                        temp_graph[i].disconnect_objectives(ipt_node, opt)
                        temp_graph[i].connect_objectives(xnor, opt)
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PI(node)
                temp_graph[i].remove_object(node)
        else:
            # Connect the pseudo PI to the previous level
            ind = 0
            to_be_deleted = []
            for ipt_node in temp_graph[i].PI:
                if 'DF_' in ipt_node.name:
                    to_be_deleted.append(ipt_node)
                    opt_list = []
                    for opt in ipt_node.fan_out_node:
                        opt_list.append(opt)
                    for opt in opt_list:
                        temp_graph[i].disconnect_objectives(ipt_node, opt)
                        temp_graph[i].connect_objectives(ppo[ind], opt)
                    ind += 1
            for node in to_be_deleted:
                temp_graph[i].remove_node_from_PI(node)
                temp_graph[i].remove_object(node)
        ppo = []
        # Connect the pseudo PO to the next level (will be implemented in the next iteration)
        to_be_deleted = []
        for opt_node in temp_graph[i].PO:
            if 'DF_' in opt_node.name:
                ppo.append(opt_node)
                to_be_deleted.append(opt_node)
        for node in to_be_deleted:
            # print(node.name)
            # print(len(temp_graph.PO))
            temp_graph[i].remove_node_from_PO(node)
        # Hide the POs in this copy (It's OK to just remove then in the PO list. No need to connect them to other nodes)
        temp_graph[i].PO = []

        # Change PI to KI as well as their names
        for ipt_node in temp_graph[i].PI:
            ipt_node.name = 'keyinput' + str(new_graph.available_key_index)
            temp_graph[i].object_name_list[temp_graph[i].object_list.index(ipt_node)] = 'keyinput' + str(
                new_graph.available_key_index)
            temp_graph[i].KI.append(ipt_node)
            new_graph.available_key_index += 1
        temp_graph[i].PI = []
        # Change node names and copy this copy to the whole top level graph
        for node_ind in range(len(temp_graph[i].object_list)):
            if 'keyinput' not in temp_graph[i].object_list[node_ind].name:
                temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name + '__' + str(i)
                temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_name_list[node_ind] + '__' + str(i)
            # if '[' in temp_graph[i].object_name_list[node_ind] or ']' in temp_graph[i].object_name_list[node_ind]:
            #     temp_graph[i].object_name_list[node_ind] = 'yh_' + str(new_graph.available_node_index)
            #     temp_graph[i].object_list[node_ind].name = 'yh_' + str(new_graph.available_node_index)
            #     new_graph.available_node_index += 1
            if '[' in temp_graph[i].object_name_list[node_ind]:
                temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace('[', 'q')
                temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace('[', 'q')
            if ']' in temp_graph[i].object_name_list[node_ind]:
                temp_graph[i].object_name_list[node_ind] = temp_graph[i].object_list[node_ind].name.replace(']', 'p')
                temp_graph[i].object_list[node_ind].name = temp_graph[i].object_list[node_ind].name.replace(']', 'p')
            new_graph.object_list.append(temp_graph[i].object_list[node_ind])
            new_graph.object_name_list.append(temp_graph[i].object_name_list[node_ind])
        for node in temp_graph[i].PI:
            new_graph.PI.append(node)
        for node in temp_graph[i].PO:
            new_graph.PO.append(node)
        for node in temp_graph[i].KI:
            new_graph.KI.append(node)
    for i in range(level_func):
        temp_graph.append(Ntk_Parser.ntk_parser(input_path))
        to_be_deleted = []
        for ipt_node in temp_graph[i + level_enc].PI:
            if len(ipt_node.fan_out_node) == 0:
                to_be_deleted.append(ipt_node)
        for opt_node in temp_graph[i + level_enc].PO:
            if len(opt_node.fan_in_node) == 0:
                to_be_deleted.append(opt_node)
        for node in to_be_deleted:
            temp_graph[i + level_enc].remove_object(node)
        # Find a PI node to use as constant source
        for ipt_node in temp_graph[i + level_enc].PI:
            if 'reset' not in ipt_node.name and 'DF_' not in ipt_node.name:
                the_PI = ipt_node
                break
        # Create the inverse of this PI
        the_PI_not = Ntk_Struct.NtkObject(the_PI.name + '_not')
        temp_graph[i + level_enc].add_object(the_PI_not, 'NOT')
        temp_graph[i + level_enc].connect_objectives(the_PI, the_PI_not)
        # Create XNOR(the_PI, the_PI_not) to make a constant 0
        xnor = Ntk_Struct.NtkObject(the_PI.name + '_xnor')
        temp_graph[i + level_enc].add_object(xnor, 'XNOR')
        temp_graph[i + level_enc].connect_objectives(the_PI, xnor)
        temp_graph[i + level_enc].connect_objectives(the_PI_not, xnor)
        # Replace reset with a constant 0
        reset_ind = temp_graph[i + level_enc].object_name_list.index('reset')
        reset = temp_graph[i + level_enc].object_list[reset_ind]
        temp_node_list = []
        for opt_node in reset.fan_out_node:
            temp_node_list.append(opt_node)
        for opt_node in temp_node_list:
            temp_graph[i + level_enc].disconnect_objectives(reset, opt_node)
            temp_graph[i + level_enc].connect_objectives(xnor, opt_node)
        temp_graph[i + level_enc].remove_object(reset)
        # # Replace the seed input with constant values
        # if '1' in seed:
        #     # Create const 1
        #     xor = Ntk_Struct.NtkObject(the_PI.name + '_xor')
        #     temp_graph[i + level_enc].add_object(xor, 'NOT')
        #     temp_graph[i + level_enc].connect_objectives(xnor, xor)
        # to_be_deleted = []
        # for ipt_node in temp_graph[i + level_enc].PI:
        #     if 'seed[' in ipt_node.name and 'bar' not in ipt_node.name:
        #         to_be_deleted.append(ipt_node)
        #         temp_node_list = []
        #         for opt_node in ipt_node.fan_out_node:
        #             temp_node_list.append(opt_node)
        #         for opt_node in temp_node_list:
        #             temp_graph[i + level_enc].disconnect_objectives(ipt_node, opt_node)
        #             if seed[-1 - int(ipt_node.name[ipt_node.name.index('[') + 1: ipt_node.name.index(']')])] == '0':
        #                 temp_graph[i + level_enc].connect_objectives(xnor, opt_node)
        #             else:
        #                 temp_graph[i + level_enc].connect_objectives(xor, opt_node)
        # for ipt_node in to_be_deleted:
        #     temp_graph[i + level_enc].remove_object(ipt_node)

        # Connect the pseudo PI to the previous level
        ind = 0
        to_be_deleted = []
        for ipt_node in temp_graph[i + level_enc].PI:
            if 'DF_' in ipt_node.name:
                to_be_deleted.append(ipt_node)
                opt_list = []
                for opt in ipt_node.fan_out_node:
                    opt_list.append(opt)
                for opt in opt_list:
                    temp_graph[i + level_enc].disconnect_objectives(ipt_node, opt)
                    temp_graph[i + level_enc].connect_objectives(ppo[ind], opt)
                ind += 1
        for node in to_be_deleted:
            temp_graph[i + level_enc].remove_node_from_PI(node)
            temp_graph[i + level_enc].remove_object(node)
        ppo = []
        if i == level_func - 1:  # If this is the last copy
            to_be_deleted = []
            for opt_node in temp_graph[i + level_enc].PO:
                if 'DF_' in opt_node.name:
                    to_be_deleted.append(opt_node)
            for node in to_be_deleted:
                temp_graph[i + level_enc].remove_node_from_PO(node)
        else:
            # Connect the pseudo PO to the next level (will be implemented in the next iteration)
            to_be_deleted = []
            for opt_node in temp_graph[i + level_enc].PO:
                if 'DF_' in opt_node.name:
                    ppo.append(opt_node)
                    to_be_deleted.append(opt_node)
            for node in to_be_deleted:
                temp_graph[i + level_enc].remove_node_from_PO(node)
        # Change node names and copy this copy to the whole top level graph
        for node_ind in range(len(temp_graph[i + level_enc].object_list)):
            temp_graph[i + level_enc].object_list[node_ind].name = temp_graph[i + level_enc].object_list[
                                                                       node_ind].name + '_' + str(i)
            temp_graph[i + level_enc].object_name_list[node_ind] = temp_graph[i + level_enc].object_name_list[
                                                                       node_ind] + '_' + str(i)
            # if '[' in temp_graph[i + level_enc].object_name_list[node_ind] or ']' in temp_graph[i + level_enc].object_name_list[node_ind]:
            #     temp_graph[i + level_enc].object_name_list[node_ind] = 'yh_' + str(new_graph.available_node_index)
            #     temp_graph[i + level_enc].object_list[node_ind].name = 'yh_' + str(new_graph.available_node_index)
            #     new_graph.available_node_index += 1
            if '[' in temp_graph[i + level_enc].object_name_list[node_ind]:
                temp_graph[i + level_enc].object_name_list[node_ind] = temp_graph[i + level_enc].object_list[
                    node_ind].name.replace('[', 'q')
                temp_graph[i + level_enc].object_list[node_ind].name = temp_graph[i + level_enc].object_list[
                    node_ind].name.replace('[', 'q')
            if ']' in temp_graph[i + level_enc].object_name_list[node_ind]:
                temp_graph[i + level_enc].object_name_list[node_ind] = temp_graph[i + level_enc].object_list[
                    node_ind].name.replace(']', 'p')
                temp_graph[i + level_enc].object_list[node_ind].name = temp_graph[i + level_enc].object_list[
                    node_ind].name.replace(']', 'p')
            new_graph.object_list.append(temp_graph[i + level_enc].object_list[node_ind])
            new_graph.object_name_list.append(temp_graph[i + level_enc].object_name_list[node_ind])
        for node in temp_graph[i + level_enc].PI:
            new_graph.PI.append(node)
        for node in temp_graph[i + level_enc].PO:
            new_graph.PO.append(node)
        for node in temp_graph[i + level_enc].KI:
            new_graph.KI.append(node)

    assert (PI_len is not None)
    # Remove the input ports for the first circuit copy as they do not matter during reset
    for ind in range(PI_len):
        new_graph.change_node_name(new_graph.KI[ind], 'dk_' + str(ind))
    for ind in range(PI_len, len(new_graph.KI)):
        new_graph.change_node_name(new_graph.KI[ind], 'keyinput' + str(ind - PI_len))
    the_KI = new_graph.KI[PI_len]
    for ind in range(PI_len):
        new_graph.KI[ind].gate_type_config(new_graph.gateType['BUFF'])
        new_graph.connect_objectives(the_KI, new_graph.KI[ind])
    new_graph.KI = new_graph.KI[PI_len:]

    Ntk_Parser.ntk_to_bench(new_graph, output_path)
