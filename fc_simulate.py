import vcs_interface


def fc_sweep(i_ports, o_ports, key_len, sim_count, lb, ub, delta_fc, max_hold, vcs_path, vcs_folder_path):
    unroll_count = lb
    counter = 0
    previous_fc = None
    fc = None
    while 1:
        print('Simulating... (Unroll_count=%d) ' % unroll_count, end='')
        previous_fc = fc
        # fc = fc_calculate(ori_seq_graph, seq_graph, key_len, unroll_count, sim_count)
        vcs_interface.simulate(key_len, sim_count, unroll_count, i_ports, o_ports, vcs_path, vcs_folder_path)
        fc = vcs_interface.corruptibility(unroll_count, key_len, sim_count, vcs_folder_path)
        print(fc)
        if previous_fc is not None:
            if fc - previous_fc <= delta_fc:
                counter += 1
            else:
                counter = 0
        if counter == max_hold:
            unroll_count -= max_hold
            return max(unroll_count + 1, lb)
        if unroll_count >= ub:
            break
        unroll_count += 1
    return unroll_count
