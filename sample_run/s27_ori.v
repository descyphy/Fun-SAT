/////////////////////////////////////////////////////////////
// Created by: Synopsys DC Expert(TM) in wire load mode
// Version   : R-2020.09-SP3
// Date      : Wed Mar 31 09:52:58 2021
/////////////////////////////////////////////////////////////


module s27_ori ( clk, reset, IN, OUT );
  input [3:0] IN;
  output [0:0] OUT;
  input clk, reset;
  wire   state_reg_0__N3, state_reg_2__N3, state_reg_1__N3, state_reg_3__N3,
         state_reg_4__N3, state_reg_5__N3, n1, n2, n3, n4, n5, n6, n7, n8, n10,
         n11, n16, n17, n18, n19, n20, n21, n22, n23, n24, n25, n26, n27, n28,
         n29, n30, n31, n32, n33, n34, n35, n36, n37, n38, n39, n40, n41, n42,
         n43, n44, n45, n46, n47, n48, n49, n50, n51, n52, n53, n54, n55, n56,
         n58, n59, n60, n61, n62, n63, n64, n65, n66, n67, n68, n69, n70, n71,
         n72, n73, n74, n75, n76, n77, n78, n79, n80, n81, n82, n83, n84, n85,
         n86, n87, n88, n89, n90, n91, n92, n93, n94, n95, n96, n97, n98, n99,
         n100, n101, n102, n104, n105, n106, n107, n108;
  wire   [5:0] state;

  DFF_X1 state_reg_5__Q_reg ( .D(state_reg_5__N3), .CK(clk), .Q(state[5]), 
        .QN() );
  DFF_X1 state_reg_2__Q_reg ( .D(state_reg_2__N3), .CK(clk), .Q(state[2]), 
        .QN(n105) );
  DFF_X1 state_reg_0__Q_reg ( .D(state_reg_0__N3), .CK(clk), .Q(state[0]), 
        .QN(n104) );
  DFF_X1 state_reg_3__Q_reg ( .D(state_reg_3__N3), .CK(clk), .Q(state[3]), 
        .QN(n107) );
  DFF_X1 state_reg_4__Q_reg ( .D(state_reg_4__N3), .CK(clk), .Q(state[4]), 
        .QN() );
  DFF_X1 state_reg_1__Q_reg ( .D(state_reg_1__N3), .CK(clk), .Q(state[1]), 
        .QN(n106) );
  NOR2_X1 U110 ( .A1(n5), .A2(n4), .ZN(n62) );
  NAND2_X1 U111 ( .A1(n54), .A2(n55), .ZN(n53) );
  NOR2_X1 U112 ( .A1(n37), .A2(n56), .ZN(n54) );
  NOR2_X1 U113 ( .A1(n6), .A2(n5), .ZN(n55) );
  NAND2_X1 U114 ( .A1(n10), .A2(n4), .ZN(n67) );
  NAND2_X1 U115 ( .A1(n3), .A2(n45), .ZN(n49) );
  NAND2_X1 U116 ( .A1(n3), .A2(n74), .ZN(n69) );
  NOR2_X1 U117 ( .A1(n10), .A2(n11), .ZN(n38) );
  INV_X1 U118 ( .A(n37), .ZN(n11) );
  NAND2_X1 U119 ( .A1(n19), .A2(n21), .ZN(n50) );
  INV_X1 U120 ( .A(n22), .ZN(n6) );
  NAND2_X1 U121 ( .A1(n76), .A2(n77), .ZN(OUT[0]) );
  NOR2_X1 U122 ( .A1(n89), .A2(n74), .ZN(n76) );
  NOR2_X1 U123 ( .A1(n78), .A2(n79), .ZN(n77) );
  NOR2_X1 U124 ( .A1(n32), .A2(n37), .ZN(n89) );
  INV_X1 U125 ( .A(n61), .ZN(n5) );
  NAND2_X1 U126 ( .A1(n62), .A2(n75), .ZN(n27) );
  NOR2_X1 U127 ( .A1(n27), .A2(n43), .ZN(n79) );
  INV_X1 U128 ( .A(n44), .ZN(n4) );
  NAND2_X1 U129 ( .A1(n1), .A2(n39), .ZN(n56) );
  INV_X1 U130 ( .A(n72), .ZN(n1) );
  NOR2_X1 U131 ( .A1(n28), .A2(n29), .ZN(n26) );
  NOR2_X1 U132 ( .A1(n20), .A2(n19), .ZN(n29) );
  NOR2_X1 U133 ( .A1(n6), .A2(n30), .ZN(n28) );
  NOR2_X1 U134 ( .A1(n31), .A2(n10), .ZN(n30) );
  NAND2_X1 U135 ( .A1(n51), .A2(n73), .ZN(n74) );
  NOR2_X1 U136 ( .A1(n32), .A2(n33), .ZN(n31) );
  NAND2_X1 U137 ( .A1(n101), .A2(n96), .ZN(n37) );
  NOR2_X1 U138 ( .A1(n82), .A2(n104), .ZN(n101) );
  NOR2_X1 U139 ( .A1(n106), .A2(n100), .ZN(n97) );
  NAND2_X1 U140 ( .A1(n104), .A2(n105), .ZN(n100) );
  OR2_X1 U141 ( .A1(n33), .A2(n108), .ZN(n52) );
  NOR2_X1 U142 ( .A1(n4), .A2(n32), .ZN(n108) );
  NOR2_X1 U143 ( .A1(n35), .A2(n36), .ZN(n34) );
  NOR2_X1 U144 ( .A1(n38), .A2(n39), .ZN(n35) );
  NOR2_X1 U145 ( .A1(n1), .A2(n37), .ZN(n36) );
  INV_X1 U146 ( .A(n20), .ZN(n7) );
  INV_X1 U147 ( .A(n75), .ZN(n3) );
  INV_X1 U148 ( .A(n73), .ZN(n10) );
  AND2_X1 U149 ( .A1(n51), .A2(n43), .ZN(n19) );
  AND2_X1 U150 ( .A1(n38), .A2(n33), .ZN(n21) );
  NAND2_X1 U151 ( .A1(n33), .A2(n43), .ZN(n45) );
  INV_X1 U152 ( .A(IN[0]), .ZN(n8) );
  NOR2_X1 U153 ( .A1(n8), .A2(IN[2]), .ZN(n20) );
  NAND2_X1 U154 ( .A1(IN[1]), .A2(n20), .ZN(n22) );
  NOR2_X1 U155 ( .A1(n85), .A2(n33), .ZN(n78) );
  NOR2_X1 U156 ( .A1(n88), .A2(n6), .ZN(n85) );
  AND2_X1 U157 ( .A1(n56), .A2(IN[0]), .ZN(n88) );
  NAND2_X1 U158 ( .A1(n84), .A2(IN[1]), .ZN(n61) );
  NOR2_X1 U159 ( .A1(IN[2]), .A2(IN[0]), .ZN(n84) );
  NAND2_X1 U160 ( .A1(n83), .A2(n8), .ZN(n44) );
  NOR2_X1 U161 ( .A1(IN[2]), .A2(IN[1]), .ZN(n83) );
  NOR2_X1 U162 ( .A1(IN[1]), .A2(IN[3]), .ZN(n72) );
  NAND2_X1 U163 ( .A1(IN[2]), .A2(IN[1]), .ZN(n39) );
  NAND2_X1 U164 ( .A1(IN[2]), .A2(n8), .ZN(n75) );
  NOR2_X1 U165 ( .A1(n2), .A2(IN[1]), .ZN(n32) );
  INV_X1 U166 ( .A(IN[3]), .ZN(n2) );
  NOR2_X1 U167 ( .A1(reset), .A2(n23), .ZN(state_reg_4__N3) );
  NOR2_X1 U168 ( .A1(n24), .A2(n25), .ZN(n23) );
  NOR2_X1 U169 ( .A1(n34), .A2(n8), .ZN(n24) );
  NOR2_X1 U170 ( .A1(n26), .A2(n27), .ZN(n25) );
  NAND2_X1 U171 ( .A1(n95), .A2(n96), .ZN(n91) );
  NOR2_X1 U172 ( .A1(state[1]), .A2(state[0]), .ZN(n95) );
  NOR2_X1 U173 ( .A1(state[3]), .A2(state[2]), .ZN(n96) );
  NOR2_X1 U174 ( .A1(state[4]), .A2(n91), .ZN(n94) );
  AND2_X1 U175 ( .A1(n92), .A2(n93), .ZN(n51) );
  NAND2_X1 U176 ( .A1(n97), .A2(n98), .ZN(n92) );
  NAND2_X1 U177 ( .A1(n94), .A2(state[5]), .ZN(n93) );
  NOR2_X1 U178 ( .A1(state[3]), .A2(n99), .ZN(n98) );
  NAND2_X1 U179 ( .A1(n80), .A2(n81), .ZN(n43) );
  NOR2_X1 U180 ( .A1(state[2]), .A2(state[0]), .ZN(n81) );
  NOR2_X1 U181 ( .A1(n82), .A2(n107), .ZN(n80) );
  NAND2_X1 U182 ( .A1(n102), .A2(n106), .ZN(n82) );
  NOR2_X1 U183 ( .A1(state[5]), .A2(state[4]), .ZN(n102) );
  NAND2_X1 U184 ( .A1(n86), .A2(n87), .ZN(n33) );
  NOR2_X1 U185 ( .A1(state[3]), .A2(state[0]), .ZN(n87) );
  NOR2_X1 U186 ( .A1(n82), .A2(n105), .ZN(n86) );
  NOR2_X1 U187 ( .A1(reset), .A2(n46), .ZN(state_reg_2__N3) );
  NOR2_X1 U188 ( .A1(n47), .A2(n48), .ZN(n46) );
  NAND2_X1 U189 ( .A1(n49), .A2(n50), .ZN(n48) );
  NAND2_X1 U190 ( .A1(n52), .A2(n53), .ZN(n47) );
  NAND2_X1 U191 ( .A1(n90), .A2(state[4]), .ZN(n73) );
  NOR2_X1 U192 ( .A1(state[5]), .A2(n91), .ZN(n90) );
  OR2_X1 U193 ( .A1(state[4]), .A2(state[5]), .ZN(n99) );
  NOR2_X1 U194 ( .A1(reset), .A2(n58), .ZN(state_reg_1__N3) );
  NOR2_X1 U195 ( .A1(n59), .A2(n60), .ZN(n58) );
  NOR2_X1 U196 ( .A1(n38), .A2(n61), .ZN(n60) );
  NOR2_X1 U197 ( .A1(n51), .A2(n62), .ZN(n59) );
  NOR2_X1 U198 ( .A1(reset), .A2(n63), .ZN(state_reg_0__N3) );
  NOR2_X1 U199 ( .A1(n64), .A2(n65), .ZN(n63) );
  NAND2_X1 U200 ( .A1(n69), .A2(n70), .ZN(n64) );
  NAND2_X1 U201 ( .A1(n66), .A2(n67), .ZN(n65) );
  NOR2_X1 U202 ( .A1(reset), .A2(n16), .ZN(state_reg_5__N3) );
  NOR2_X1 U203 ( .A1(n17), .A2(n18), .ZN(n16) );
  NOR2_X1 U204 ( .A1(n19), .A2(n7), .ZN(n18) );
  NOR2_X1 U205 ( .A1(n21), .A2(n22), .ZN(n17) );
  NOR2_X1 U206 ( .A1(reset), .A2(n40), .ZN(state_reg_3__N3) );
  NOR2_X1 U207 ( .A1(n41), .A2(n42), .ZN(n40) );
  NOR2_X1 U208 ( .A1(n43), .A2(n44), .ZN(n42) );
  AND2_X1 U209 ( .A1(n45), .A2(n5), .ZN(n41) );
  NAND2_X1 U210 ( .A1(n68), .A2(n11), .ZN(n66) );
  NOR2_X1 U211 ( .A1(IN[0]), .A2(n39), .ZN(n68) );
  NAND2_X1 U212 ( .A1(n71), .A2(n72), .ZN(n70) );
  NOR2_X1 U213 ( .A1(IN[0]), .A2(n38), .ZN(n71) );
endmodule

