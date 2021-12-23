import os
import numpy as np
import os


####################################################################################
# generate reset and inputs
# each 'unit' tests the output for one key sequence.
# Nseq keys will be tested. Therefore, there are Nseq units in the file.
# The reset list in one unit is: 1, 0, ..., 0
# The input list for oracle in one unit is : 0, in_under_test, 0,...,0
# The input list for locked netlist in one unit is : 0, key_under_test, in_under_test, 0
# The three lists are with the same length.
####################################################################################

def gen_input(cycle, Nseqs, inbit, keyseqlen):
    keybit = inbit
    # if cycle < keyseqlen:
    #     print("Cycle is smaller than the key sequence length!")

    unitLen = 2 + cycle + keyseqlen
    reset = [1] + [0] * (unitLen - 1)
    reset = reset * Nseqs
    uIN = [0] * unitLen
    uIN_enc = [0] * unitLen

    IN = []
    IN_enc = []

    for i in range(Nseqs):
        # generate a random input and a random key.
        cur_in = np.random.randint(0, pow(2, inbit), cycle)
        cur_key = np.random.randint(0, pow(2, keybit), keyseqlen)

        # The input list for oracle in one unit is : 0, in_under_test, 0,...,0
        uIN[1:cycle + 1] = cur_in

        # The input list for locked netlist in one unit is : 0, key_under_test, in_under_test, 0
        uIN_enc[1:keyseqlen + 1] = cur_key
        uIN_enc[keyseqlen + 1: -1] = cur_in

        IN = IN + uIN
        IN_enc = IN_enc + uIN_enc

    return IN, IN_enc, reset


####################################################################################
# generate testbench
####################################################################################
def gen_tb(input, output, cycle, path):
    tb_name = 'tb_cycle' + str(cycle) + '.v'
    infile = './tb/cycle' + str(cycle) + '/in.txt'
    outfile = './fout/fout_cycle' + str(cycle) + '.txt'

    input_ori = [item + '_ori' for item in input]
    output_ori = [item + '_ori' for item in output]

    tb = []
    tb.append('`timescale 1ns/ 100ps\n')
    tb.append('module tb_cycle' + str(cycle) + ';\n')

    tb.append('reg clk, reset;\n')
    tb.append('reg ' + ', '.join(input) + ';\n')
    tb.append('reg ' + ', '.join(input_ori) + ';\n')

    tb.append('ori dut1(clk, reset, ' + ', '.join(input_ori) + ', ' + ', '.join(output_ori) + ');\n')
    tb.append('enc dut2(clk, reset, ' + ', '.join(input) + ', ' + ', '.join(output) + ');\n')
    tb.append('\n')
    tb.append('initial begin\n')
    tb.append('clk=0;\n')
    tb.append('forever #2.5 clk=~clk;\n')
    tb.append('end\n')
    tb.append('\n')

    tb.append('integer fp, status;\n')
    tb.append('initial begin\n')
    tb.append('   fp =$fopen("' + infile + '", "r");\n')
    tb.append('   if(!fp)\n')
    tb.append('   begin\n')
    tb.append('      $display("File cannot be opened!");\n')
    tb.append('      $finish;\n')
    tb.append('   end\n')
    tb.append('end\n')
    tb.append('\n')
    tb.append('always @ (negedge clk)\n')
    tb.append('begin\n')
    tb.append('   if($feof(fp))\n')
    tb.append('      $finish;\n')
    tb.append('  status=$fscanf(fp, "%d %d %b ' + r'\n' + '", {' + ', '.join(input_ori) + '}, { ' + ', '.join(
        input) + '}, reset);\n')
    tb.append('end\n')

    tb.append('integer fout;\n')
    tb.append('initial begin\n')
    tb.append('    fout=$fopen("' + outfile + '");\n')
    tb.append('    if (!fout) begin\n')
    tb.append('         $display("Can\'t open file!");\n')
    tb.append('         $finish;\n')
    tb.append('    end\n')
    tb.append('end\n')
    tb.append('\n')
    tb.append('always @ (posedge clk)\n')
    tb.append('    $fdisplay(fout, "%d %d %d", {' + ', '.join(output_ori) + '}, {' + ', '.join(output) + '}, reset);\n')
    tb.append('endmodule\n')

    with open(path + tb_name, 'w') as ftb:
        for item in tb:
            ftb.write(item)
    return tb


####################################################################################
# master generation: master lists all the files needed for vcs.
####################################################################################
def gen_master(cycle, path):
    master = [None] * 3
    master[0] = './tb/cycle' + str(cycle) + '/tb_cycle' + str(cycle) + '.v'
    master[1] = './this_enc.v'
    master[2] = './this_ori.v'

    with open(path + '/master', 'w') as fmaster:
        for item in master:
            fmaster.write(item + '\n')

    return master


####################################################################################
# calculate corruptibility
####################################################################################
def corruptibility(cycle, keyseqlen, Nseqs, vcs_folder_path):
    file = os.path.join(vcs_folder_path, 'fout/fout_cycle' + str(cycle) + '.txt')

    out_ori = []
    out_intlck = []
    reset = []

    # the fout_cycle.txt stores the simulation outputs in the order of:
    # output of oracle, output of locked netlist, reset

    with open(file, 'r') as fout:
        for line in fout:
            line = line.split()
            out_ori.append(line[0])
            out_intlck.append(line[1])
            reset.append(line[2])

    # compare the outputs of oracle and locked netlist and count the number of errors.
    n_false = 0
    unitLen = 2 + cycle + keyseqlen
    for i in range(Nseqs):
        # skip the output when the circuit is being resetted.
        st = 2 + i * unitLen
        end = 2 + i * unitLen + cycle
        st_intlck = st + keyseqlen
        end_intlck = end + keyseqlen

        # extrac the output of the oracle and the output of the encrypted netlist in the current unit.
        cur_out_ori = out_ori[st:end]
        cur_out_intlck = out_intlck[st_intlck:end_intlck]
        if cur_out_ori != cur_out_intlck:
            n_false = n_false + 1

    FC = n_false / Nseqs

    return FC


####################################################################################
# Write simulation files
####################################################################################


def gen_tb_cycle(cycle, Nseqs, inbit, path, keyseqlen, input, output, vcs_path, vcs_folder_path):
    # generate in.txt
    IN, IN_intlck, reset = gen_input(cycle, Nseqs, inbit, keyseqlen)
    with open(path + '/in.txt', 'w') as fin:
        for i in range(0, len(reset)):
            fin.write(str(IN[i]) + ' ' + str(IN_intlck[i]) + ' ' + str(reset[i]) + '\n')

    # generate master for vcs
    gen_master(cycle, path)

    # generate testbench for vcs
    gen_tb(input, output, cycle, path)

    # write tcl for vcs -- do not need this anymore
    # with open(vcs_folder_path+'run.tcl', 'w') as ftcl:
    #    ftcl.write(vcs_path + ' -full64 -debug_acc+all -f ./tb/cycle' + str(cycle) + '/master -R\n')

    fout_path = os.path.join(vcs_folder_path, 'fout')

    # make fout folder
    if not os.path.exists(fout_path):
        os.makedirs(fout_path)
    return


####################################################################################
# Run simulation for a single cycle.
####################################################################################

def simulate(KeyLength, Nseqs, cycle, input, output, vcs_path, vcs_folder_path):
    tb_cycle_path = os.path.join(vcs_folder_path, 'tb/cycle' + str(cycle) + '/')

    if not os.path.exists(tb_cycle_path):
        os.makedirs(tb_cycle_path)

    # write simulation files: master, tb_cycle.v, in.txt
    inbit = len(input)
    gen_tb_cycle(cycle, Nseqs, inbit, tb_cycle_path, KeyLength, input, output, vcs_path, vcs_folder_path)

    # run simulation
    cur_path = os.getcwd()
    os.chdir(vcs_folder_path)
    # os.system(vcs_path + ' -full64 +rad -f '+ vcs_folder_path+'tb/cycle' + str(cycle) + '/master -R >/dev/null')
    os.system(vcs_path + ' -full64 +rad -f ./tb/cycle' + str(cycle) + '/master -R >/dev/null')
    os.chdir(cur_path)

    return
