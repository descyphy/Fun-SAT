import os
import sys
import time
import random

import Ntk_Parser
import translate
from fc_simulate import fc_sweep
from model_checking import bmc, umc, key_to_initial_state
from monitor_sat import run_sat_basic
from unroll_prepare import prepare_ori, prepare_enc


if __name__ == '__main__':
    # TODO: Make the path reference correctly by using path functions

    # Remove these two lines for debug purpose.
    # f = open('attack_log.txt', 'w')  # FIXME: add back if you want to output to log
    # sys.stdout = f  # FIXME: add back if you want to output to log

    if len(sys.argv) < 10:
        print('Not enough argument! The correct format should be: ')
        print('python unroll_sat.py\n       '
              '<original netlist>\n       '
              '<encrypted netlist>\n       '
              '<key length>\n       '
              '<bounded time window size>\n       '
              '<FC difference threshold>\n       '
              '<FC hold threshold>\n       '
              '<Simulation count>\n       '
              '<Time-out in seconds>\n       '
              '<Fun-SAT enable (1 or 0)>')
        exit()
    ori_v = sys.argv[1]
    enc_v = sys.argv[2]
    key_len = int(sys.argv[3])
    max_unroll = int(sys.argv[4])
    delta_fc = float(sys.argv[5])
    max_hold = int(sys.argv[6])
    sim_count = int(sys.argv[7])  # Default: 1000

    # Create a temporary folder to store intermmediate files
    while 1:
        temp_path = time.strftime(".%m%d%Y%H%M%S", time.gmtime()) + '_' + str(random.randint(0, 10000))
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)
            temp_path = os.path.abspath(temp_path)
            break

    time_start_with_preprocess = time.time()
    print('\n*****************************************\n')
    print('Original netlist: %s' % ori_v)
    print('Encrypted netlist: %s' % enc_v)
    print('Key length in cycle count: %d' % key_len)

    # Verilog to Bench
    translate.translate(ori_v, temp_path)
    print('Original netlist: Verilog to Bench finished.')
    translate.translate(enc_v, temp_path)
    print('Encrypted netlist: Verilog to Bench finished.')
    os.rename(os.path.join(temp_path, os.path.basename(ori_v[:ori_v.index('.v')] + '.bench')), os.path.join(temp_path, 'this_ori.bench'))
    os.rename(os.path.join(temp_path, os.path.basename(enc_v[:enc_v.index('.v')] + '.bench')), os.path.join(temp_path, 'this_enc.bench'))

    # Unroll Prepare - Transfer the sequential netlist to combinational
    circuit = 'this'
    Ntk_Parser.seq_to_comb(temp_path + '/' + circuit + '_ori.bench', temp_path + '/' + circuit + '_c.bench')
    print('Original netlist: Sequential to Combinational finished.')
    # exit()
    Ntk_Parser.seq_to_comb(temp_path + '/' + circuit + '_enc.bench', temp_path + '/' + circuit + '_enc_c.bench')
    print('Encrypted netlist: Sequential to Combinational finished.')

    ori_seq_graph_ro = Ntk_Parser.ntk_parser(os.path.join(temp_path, 'this_ori.bench'))
    Ntk_Parser.ntk_levelization_seq(ori_seq_graph_ro)
    i_ports, o_ports = translate.bench_to_v(ori_seq_graph_ro, 'ori', os.path.join(temp_path, 'this_ori.v'), True)
    seq_graph_ro = Ntk_Parser.ntk_parser(os.path.join(temp_path, 'this_enc.bench'))
    Ntk_Parser.ntk_levelization_seq(seq_graph_ro)
    _, _ = translate.bench_to_v(seq_graph_ro, 'enc', os.path.join(temp_path, 'this_enc.v'), False)

    # Set up the initial parameters for the attack loop
    func_level = 1
    fun_sat_flag = int(sys.argv[9])
    func_level_lb = 1
    func_level_ub = max_unroll
    time_out = False
    time_out_limit = int(sys.argv[8])  # Default: 24 * 60 * 60
    time_elapse = 0

    ori_seq_graph_ro = None
    seq_graph_ro = None

    # print('Starting SAT attacks...\n')
    time_start_with_attack = time.time()
    uc_count = 0
    bmc_count = 0
    umc_count = 0

    if fun_sat_flag:
        config_f = open('src/vcs_config.txt', 'r')
        for line in config_f.readlines():
            vcs_path = line.strip()
            break
        config_f.close()
    config_f = open('src/nuxmv_config.txt', 'r')
    for line in config_f.readlines():
        nuxmv_path = line.strip()
        break
    config_f.close()

    while 1:
        if fun_sat_flag:
            print('\n********** FC analysis phase ************\n')
            if ori_seq_graph_ro is None:
                ori_seq_graph_ro = Ntk_Parser.ntk_parser(os.path.join(temp_path, 'this_ori.bench'))
                Ntk_Parser.ntk_levelization_seq(ori_seq_graph_ro)
            if seq_graph_ro is None:
                seq_graph_ro = Ntk_Parser.ntk_parser(os.path.join(temp_path, 'this_enc.bench'))
                Ntk_Parser.ntk_levelization_seq(seq_graph_ro)
            time_a = time.time()
            func_level = fc_sweep(i_ports, o_ports, key_len=key_len, sim_count=sim_count, lb=func_level_lb,
                                  ub=func_level_ub, delta_fc=delta_fc, max_hold=max_hold, vcs_path=vcs_path,
                                  vcs_folder_path=temp_path)
            time_b = time.time()
            time_elapse += time_b - time_a
            if time_elapse > time_out_limit:  # Timeout
                time_out = True
                break

        print('\n********** SAT attack phase *************\n')
        print('Feasible unroll cycles: %d' % (func_level))
        # Prepare the original netlist for SAT attacks
        prepare_ori(temp_path + '/' + circuit + '_c.bench', temp_path + '/' + circuit + '_c_ready.bench', func_level + 1)
        # Prepare the encrypted netlist for SAT attacks
        prepare_enc(temp_path + '/' + circuit + '_enc_c.bench', temp_path + '/' + circuit + '_enc_c_ready.bench', key_len + 1, func_level)
        # Execute SAT attack
        time_a = time.time()
        success_flag, unique_key_flag, predicted_key, dip_list, odip_list = run_sat_basic(temp_path + '/' + circuit + '_enc_c_ready.bench', temp_path + '/' + circuit + '_c_ready.bench', False)
        time_b = time.time()
        time_elapse += time_b - time_a
        print('#DIPs = %d' % len(dip_list))
        if time_elapse > time_out_limit:  # Timeout
            time_out = True
            break
        uc_count += 1
        if not success_flag:
            print('Key length is not correct!')
            break
        print('Key prediction: %s' % predicted_key[0])

        if unique_key_flag:
            print('Unique key passed!')
            print('key=%s' % predicted_key[0])
            break
        else:
            print('Unique key failed!')
            # Process the modified netlists required for constructing model checking instance
            ori_seq_graph, ori_initial_state = key_to_initial_state(os.path.join(temp_path, 'this_ori.bench'), predicted_key[0], 0)
            seq_graph, predicted_initial_state = key_to_initial_state(os.path.join(temp_path, 'this_enc.bench'), predicted_key[0], key_len)
            ori_seq_graph.remove_node_from_PI(ori_seq_graph.find_node_by_name('reset'))
            ori_seq_graph.find_node_by_name('reset').gate_type_config(ori_seq_graph.gateType['BUFF'])
            ori_seq_graph.connect_objectives_by_name('constant_0', 'reset')
            Ntk_Parser.ntk_to_bench(ori_seq_graph, os.path.join(temp_path, 'this_ori_nr.bench'))
            seq_graph.remove_node_from_PI(seq_graph.find_node_by_name('reset'))
            seq_graph.find_node_by_name('reset').gate_type_config(seq_graph.gateType['BUFF'])
            seq_graph.connect_objectives_by_name('constant_0', 'reset')
            Ntk_Parser.ntk_to_bench(seq_graph, os.path.join(temp_path, 'this_enc_dec_nr.bench'))
            encrypted_circuit = os.path.join(temp_path, 'this_enc_dec_nr.bench')
            encrypted_circuit_c = os.path.join(temp_path, 'this_enc_c_ready.bench')
            time_a = time.time()
            bmc_flag = bmc(encrypted_circuit, encrypted_circuit_c, key_len, dip_list, odip_list, func_level + 1,
                           nuxmv_path, folder_path=temp_path)
            time_b = time.time()
            time_elapse += time_b - time_a
            bmc_count += 1
            if time_elapse > time_out_limit:  # Timeout
                time_out = True
                break
            if bmc_flag:
                print('BMC passed!')
                time_a = time.time()
                umc_flag = umc(encrypted_circuit, encrypted_circuit_c, key_len, dip_list, odip_list, nuxmv_path,
                               model_ready=True, folder_path=temp_path)
                time_b = time.time()
                time_elapse += time_b - time_a
                umc_count += 1
                assert (umc_flag is not None)
                if umc_flag:
                    print('UMC passed!')
                    print('key=%s' % predicted_key[0])
                    break
                else:
                    print('UMC failed!')
                # print('key=%s' % predicted_key[0])
            else:
                print('BMC failed!')
        if not fun_sat_flag:
            func_level += 1
        else:
            func_level_lb = func_level + 1
            func_level_ub = func_level_lb + max_unroll
        if time_elapse > time_out_limit:  # Timeout
            time_out = True
            break

    time_end = time.time()
    print('\n********** Attack Summary ***************\n')
    print('TotalRuntime: %s sec.' % (time_end - time_start_with_preprocess))
    # if fun_sat_flag:
    #     print('Runtime (FC simulation + SAT): %s sec.' % (time_end - time_start_with_fc_sim))
    # print('Runtime (Attack): %s sec.' % (time_end - time_start_with_attack))
    print('Runtime (Attack): %s sec.' % time_elapse)
    print('UC:%d, BMC:%d, UMC:%d' % (uc_count, bmc_count, umc_count))
    if not time_out:
        print('Succeeded at unroll cycles b=%d' % func_level)
        print('key=%s' % predicted_key[0])
        print('')
    else:
        print('Timeout!!! ')
        print('')
    # Clean up the working directory
    # if os.path.exists('circuit.smv'):
    # TODO: Refactor this once all the intermediate files are in the temp path
    os.system('rm -rf this_*.bench')
    os.system('rm -rf this_*.v')
    if os.path.exists('circuit.smv'):
        os.system('rm -rf circuit.smv')
    os.system('rm -rf simv*')
    if os.path.exists('tb'):
        os.system('rm -rf tb')
    if os.path.exists('fout'):
        os.system('rm -rf fout')
    if os.path.exists('run.tcl'):
        os.system('rm -rf run.tcl')
    if os.path.exists('ucli.key'):
        os.system('rm -rf ucli.key')
    if os.path.exists('csrc'):
        os.system('rm -rf csrc')
    if os.path.exists(temp_path):
        os.system('rm -rf ' + temp_path)
