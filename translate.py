# Note: This function can handle multiple lines of the same gate.


import re
import sys
import os


def translate(filePath, folder_path=None):
    f = open(filePath, "r")
    if folder_path is None:
        newFilePath = filePath.replace(".v", ".bench")
    else:
        filePath = os.path.basename(filePath)
        newFilePath = os.path.join(folder_path, filePath.replace(".v", ".bench"))
    of = open(newFilePath, "w+")
    parsed_f = (f.read()).split(";")
    constant_gate = ""
    flipflop_D_ports = []
    flipflop_Q_ports = []
    flipflop_QN_ports = []
    input_list = []
    input_visit = []

    for i in range(len(parsed_f)):
        parsed_f[i] += ";"
        parsed_f[i] = parsed_f[i].replace("\n", " ")
        # parsed_f[i] = parsed_f[i].replace(" ", "")
        # print(parsed_f[i])  # For debug
        #####################################
        # Match Input
        #####################################
        if re.match(r"^(\s*)input\s+(\[[0-9:]+\][\w\d\s,]+)+;$", parsed_f[i]):
            x = re.findall(r"\[[0-9:]+\][\w\d\s]+[,;]", parsed_f[i])
            for j in range(len(x)):
                y = re.split(r"\[|:|\]| |,|;", x[j])
                for k in range(int(y[2]), int(y[1]) + 1):
                    of.write("INPUT(" + y[-2] + "[" + str(k) + "])\n")
                    input_list.append(str(y[-2]) + "[" + str(k) + "]")
                    input_visit.append(0)
                    #####################################
                    # Construct Constant Gates
                    #####################################
                    if constant_gate == "":
                        constant_gate = str(y[-2]) + "[" + str(k) + "]"
                        # print(constant_gate)
                        of.write(str(constant_gate) + "_bar = NOT(" + str(constant_gate) + ")\n")
                        of.write("constant_1 = XOR(" + str(constant_gate) + ", " + str(constant_gate) + "_bar)\n")
                        of.write("constant_0 = NOT(constant_1)\n")
            continue

        if re.match(r"^(\s*)input\s+([\w\d\s,\[\]]+);$", parsed_f[i]):
            x = re.findall(r"[\w\d\[\]]+[,;]", parsed_f[i])
            for j in range(len(x)):
                y = re.sub(r",|;", "", x[j])
                if (y == "clk") or (y == "VDD") or (y == "GND"):
                    continue
                of.write("INPUT(" + y + ")\n")
                input_list.append(str(y))
                input_visit.append(0)
                #####################################
                # Construct Constant Gates
                #####################################
                if constant_gate == "" and 'reset' not in str(y):
                    constant_gate = str(y)
                    # print(constant_gate)
                    of.write(str(constant_gate) + "_bar = NOT(" + str(constant_gate) + ")\n")
                    of.write("constant_1 = XOR(" + str(constant_gate) + ", " + str(constant_gate) + "_bar)\n")
                    of.write("constant_0 = NOT(constant_1)\n")
            continue

        #####################################
        # Match Output
        # Qeustion: Is it possible that some outputs are in the form of bus?
        #####################################
        if re.match(r"^(\s*)output\s+(\[[0-9:]+\][\/\\\w\d\s,]+)+;$", parsed_f[i]):
            x = re.findall(r"\[[0-9:]+\][\/\\\w\d\s]+[,;]", parsed_f[i])
            for j in range(len(x)):
                y = re.split(r"\[|:|\]| |,|;", x[j])
                for k in range(int(y[2]), int(y[1]) + 1):
                    of.write("OUTPUT(" + y[-2] + "[" + str(k) + "])\n")
                    # input_list.append(str(y[-2]) + "[" + str(k) + "]")
                    # input_visit.append(0)
            continue

        if re.match(r"^(\s*)output\s+([\[\]\/\\\w\d\s,]+);$", parsed_f[i]):
            x = re.findall(r"[\/\\\w\d\[\]]+[,;]", parsed_f[i])
            for j in range(len(x)):
                y = re.sub(r",|;", "", x[j])
                of.write("OUTPUT(" + y + ")\n")
            continue

        #####################################
        # Match Assign
        #####################################
        if re.match(r"^(\s*)assign\s+[\w\d\[\]]+\s+=\s+[\w\d\'\[\]]+;$", parsed_f[i]):
            x = re.split(r"\s+|=|;", parsed_f[i])
            # print(x)
            if x[-2] == "1'b1":
                of.write(x[2] + " = BUFF(constant_1)\n")
            elif x[-2] == "1'b0":
                of.write(x[2] + " = BUFF(constant_0)\n")
            else:
                of.write(x[2] + " = BUFF(" + x[-2] + ")\n")
                if (x[-2]) in input_list:
                    input_visit[input_list.index(x[-2])] = 1
            continue

        #####################################
        # Match DFF
        #####################################
        if re.match(r"^(\s*)DFF_[\w\d\s]*\([\w\d\s,\(\)\[\]\.]+\);$", parsed_f[i]):
            #####################################
            # Match D Port
            #####################################
            D = re.search(r"\.D\([\w\d\s\[\]]+\)", parsed_f[i])
            if (D):
                D_port = re.split(r"\(|\)", D.group())[1]
                if (D_port) in input_list:
                    input_visit[input_list.index(D_port)] = 1
            else:
                exit("D port doesn't exist!")
            #####################################
            # Match Q Port
            #####################################
            Q = re.search(r"\.Q\([\w\d\s\[\]]+\)", parsed_f[i])
            Q_port = ""
            if (Q):
                Q_port = re.split(r"\(|\)", Q.group())[1].replace(" ", "")
                if (D_port in flipflop_D_ports):
                    # print(D_port)
                    DFF_index = flipflop_D_ports.index(D_port)
                    if (flipflop_Q_ports[DFF_index] != ""):
                        of.write(Q_port + " = BUFF(" + flipflop_Q_ports[DFF_index] + ")\n")
                    elif (flipflop_QN_ports[DFF_index] != ""):
                        # else:
                        of.write(Q_port + " = NOT(" + flipflop_QN_ports[DFF_index] + ")\n")
                else:
                    of.write(Q_port + " = DFF(" + D_port + ")\n")
            #####################################
            # Match QN Port
            #####################################
            QN = re.search(r"\.QN\([\w\d\s\[\]]+\)", parsed_f[i])
            QN_port = ""
            if (QN):
                QN_port = re.split(r"\(|\)", QN.group())[1].replace(" ", "")
                if (Q):
                    of.write(QN_port + " = NOT(" + Q_port + ")\n")
                else:
                    if (D_port in flipflop_D_ports):
                        DFF_index = flipflop_D_ports.index(D_port)
                        if (flipflop_QN_ports[DFF_index] != ""):
                            of.write(QN_port + " = BUFF(" + flipflop_QN_ports[DFF_index] + ")\n")
                        elif (flipflop_Q_ports[DFF_index] != ""):
                            # else:
                            of.write(QN_port + " = NOT(" + flipflop_Q_ports[DFF_index] + ")\n")
                    else:
                        of.write(QN_port + "_bar = DFF(" + D_port + ")\n")
                        of.write(QN_port + " = NOT(" + QN_port + "_bar)\n")
            flipflop_D_ports.append(D_port)
            flipflop_Q_ports.append(Q_port)
            flipflop_QN_ports.append(QN_port)
            continue

        #####################################
        # Match Gates (NAND, AND, NOR, OR, XOR, XNOR, INV, BUF)
        #####################################
        if re.match(r"^(\s*)([\w\d]+)(\s+)([\w\d]+)(\s+)\([\w\d\s,\(\)\[\]\.]+\);$", parsed_f[i]):
            gate = re.match(r"^\s*[\w\d]+\s+[\w\d]+", parsed_f[i])
            gate_type = re.split(r"\s+", gate.group())[1]

            #####################################
            # For INV and BUF
            #####################################
            if ("INV_" in gate_type) or ("BUF_" in gate_type):
                #####################################
                # Match A Port
                #####################################
                A = re.search(r"\.A\([\w\d\s\[\]]+\)", parsed_f[i])
                if (A):
                    A_port = re.split(r"\(|\)", A.group())[1].replace(" ", "")
                    if (A_port) in input_list:
                        input_visit[input_list.index(A_port)] = 1
                else:
                    exit("A port doesn't exist!")
                #####################################
                # Match Z/ZN Port
                #####################################
                Z = re.search(r"\.Z(N?)\([\w\d\s\[\]]+\)", parsed_f[i])
                if (Z):
                    Z_port = re.split(r"\(|\)", Z.group())[1].replace(" ", "")
                    if ("BUF_" in gate_type):
                        of.write(Z_port + " = BUFF(" + A_port + ")\n")
                    else:
                        of.write(Z_port + " = NOT(" + A_port + ")\n")
                else:
                    exit("Z/ZN port doesn't exist!")
            #####################################
            # For XOR and XNOR
            #####################################
            elif ("XOR2_" in gate_type) or ("XNOR2_" in gate_type):
                #####################################
                # Match A Port
                #####################################
                A = re.search(r"\.A\([\w\d\s\[\]]+\)", parsed_f[i])
                if (A):
                    A_port = re.split(r"\(|\)", A.group())[1].replace(" ", "")
                    if (A_port) in input_list:
                        input_visit[input_list.index(A_port)] = 1
                else:
                    exit("A port doesn't exist!")
                #####################################
                # Match B Port
                #####################################
                B = re.search(r"\.B\([\w\d\s\[\]]+\)", parsed_f[i])
                if (B):
                    B_port = re.split(r"\(|\)", B.group())[1].replace(" ", "")
                    if (B_port) in input_list:
                        input_visit[input_list.index(B_port)] = 1
                else:
                    exit("B port doesn't exist!")
                #####################################
                # Match Z/ZN Port
                #####################################
                Z = re.search(r"\.Z(N?)\([\w\d\s\[\]]+\)", parsed_f[i])
                if (Z):
                    Z_port = re.split(r"\(|\)", Z.group())[1].replace(" ", "")
                    of.write(Z_port + " = " + gate_type.split("2_")[0] + "(" + A_port + ", " + B_port + ")\n")
                else:
                    exit("Z/ZN port doesn't exist!")
            #####################################
            # For NAND, AND, NOR and OR
            #####################################
            else:
                #####################################
                # Match A1 Port
                #####################################
                A1 = re.search(r"\.A1\([\w\d\s\[\]]+\)", parsed_f[i])
                if (A1):
                    A1_port = re.split(r"\(|\)", A1.group())[1].replace(" ", "")
                    if (A1_port) in input_list:
                        input_visit[input_list.index(A1_port)] = 1
                else:
                    exit("A1 port doesn't exist!")
                #####################################
                # Match A2 Port
                #####################################
                A2 = re.search(r"\.A2\([\w\d\s\[\]]+\)", parsed_f[i])
                if (A2):
                    A2_port = re.split(r"\(|\)", A2.group())[1].replace(" ", "")
                    if (A2_port) in input_list:
                        input_visit[input_list.index(A2_port)] = 1
                else:
                    exit("A2 port doesn't exist!")
                #####################################
                # Match Z/ZN Port
                #####################################
                Z = re.search(r"\.Z(N?)\([\w\d\s\[\]]+\)", parsed_f[i])
                if (Z):
                    Z_port = re.split(r"\(|\)", Z.group())[1].replace(" ", "")
                    of.write(Z_port + " = " + gate_type.split("2_")[0] + "(" + A1_port + ", " + A2_port + ")\n")
                else:
                    exit("Z/ZN port doesn't exist!")

    # print(input_list)
    # print(input_visit)

    of.close()
    f.close()


def main(argv):
    translate(argv[1])


def bench_to_v(bench_net, module_name, out_file, dff_flag):
    gateType_reverse = {1: "IPT", 2: "NOT", 3: "NAND", 4: "AND", 5: "NOR", 6: "OR", 7: "XOR", 8: "XNOR", 9: "DFF",
                        10: "BUF"}
    fout = open(out_file, 'w')
    if dff_flag:
        fout.write('module dff (clk, Q, D);\n'
                   'input wire clk, D;\n'
                   'output reg Q;\n'
                   'always @(posedge clk) begin\n'
                   'Q <= D;\n'
                   'end\n'
                   'endmodule\n\n')
    fout.write('module ' + module_name + ' (clk, reset, ')
    i_ports = []
    o_ports = []
    # for node in bench_net.PI:
    #     i_ports.append(node.name)
    # for node in bench_net.PO:
    #     o_ports.append(node.name)
    # i_ports.sort()
    # o_ports.sort()
    for node in bench_net.PI:
        if 'reset' != node.name:
            fout.write('%s, ' % node.name)
    for node in bench_net.PO:
        if bench_net.PO.index(node) == len(bench_net.PO) - 1:
            fout.write('%s' % node.name)
        else:
            fout.write('%s, ' % node.name)
    fout.write(');\n')
    fout.write('input clk, reset, ')
    comma_flag = False
    for node in bench_net.PI:
        if 'reset' != node.name:
            if comma_flag:
                fout.write(', ')
            fout.write('%s' % node.name)
            i_ports.append(node.name)
            comma_flag = True
    fout.write(';\n')
    fout.write('output ')
    for node in bench_net.PO:
        if bench_net.PO.index(node) == len(bench_net.PO) - 1:
            fout.write('%s;\n' % node.name)
        else:
            fout.write('%s, ' % node.name)
        o_ports.append(node.name)

    # fout.write('reg ')
    # comma_flag = False
    # for node in bench_net.object_list:
    #     if node not in bench_net.PI and node not in bench_net.PO:
    #         if node.gate_type != bench_net.gateType['DFF']:
    #             pass
    #         else:
    #             if comma_flag:
    #                 fout.write(', ')
    #             fout.write('%s' % node.name)
    #             comma_flag = True
    # fout.write(';\n')

    gate_count = 0
    # dff_q = []
    # dff_d = []
    for node in bench_net.object_list:
        if node.gate_type != bench_net.gateType['IPT']:
            if node.gate_type != bench_net.gateType['DFF']:
                fout.write('%s AbC_%d(%s, ' % (gateType_reverse[node.gate_type].lower(), gate_count, node.name))
                for ipt_node in range(len(node.fan_in_node)):
                    if ipt_node == len(node.fan_in_node) - 1:
                        fout.write('%s);\n' % node.fan_in_node[ipt_node].name)
                    else:
                        fout.write('%s, ' % node.fan_in_node[ipt_node].name)
                # for ipt_node in node.fan_in_node:
                #     if node.fan_in_node.index(ipt_node) == len(node.fan_in_node) - 1:
                #         fout.write('%s);\n' % ipt_node.name)
                #     else:
                #         fout.write('%s, ' % ipt_node.name)
            else:
                fout.write('dff AbC_%d(clk, %s, %s);\n' % (gate_count, node.name, node.fan_in_node[0].name))
                # dff_q.append(node.name)
                # dff_d.append(node.fan_in_node[0].name)
            gate_count += 1
    # fout.write('\nalways @(posedge clk) begin\n')
    # for ind in range(len(dff_d)):
    #     fout.write('%s <= %s;\n' % (dff_q[ind], dff_d[ind]))
    # fout.write('end\n\n')
    fout.write('endmodule\n')
    fout.close()

    return i_ports, o_ports


if __name__ == "__main__":
    main(sys.argv)
