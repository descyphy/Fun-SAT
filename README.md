# Fun-SAT
[![License: MIT](https://github.com/descyphy/Fun-SAT/blob/9fa9c5aa5a1fca8924632e230028bf768b73f21b/LICENSE)

This repo contains the source code for **Functional Corruptibility-Guided SAT-Based Attack on Sequential Logic Encryption**.

For more information about the tool, please visit the [preprint](https://arxiv.org/abs/2108.04892) of our HOST'21 paper.

Tool Dependency:
------
The tool has been successfully tested on `Ubuntu 18.04.5 LTS` and `CentOS Stream 8`.

1. `Python 3.6` or higher version
2. [`nuXmv`](https://nuxmv.fbk.eu/) (**Please put the absolute path of the tool executable to `src/nuxmv_config.txt`**)
3. [`VCS`](https://www.synopsys.com/verification/simulation/vcs.html) (**Please put the absolute path of the tool executable
   to `src/vcs_config.txt`**)
4. [`Modified version of the SAT attack tool`](https://github.com/yinghuah/SAT_Attack_on_Logic_Locking) originally developed by Pramod Subramanyan (**After compiling this tool, please put the executable `sld` to `src/`**)
5. All the tool dependencies required by the above tools.

Netlist Format:
------

1. Must be Verilog files with the file suffix of `.v`.
2. Must be synchronous active high reset.
3. Currently, the tool only supports two-input gates, inverters, buffers, and posedge Flip-Flops (with the name of `DFF_*`) from the
   [Nangate Open Cell library](https://si2.org/open-cell-library/).
4. The names of the clock signal and the reset signal should be `clk` and `reset`, respectively. 

Please make sure the format of your netlists is the same as that of the sample netlists in `sample_run/` folder.

Command Format:
------

```
python unroll_sat.py <original netlist> 
                     <encrypted netlist> 
                     <key length> 
                     <bounded time window size>
                     <FC difference threshold>
                     <FC hold threshold> 
                     <Simulation count> 
                     <Time-out in seconds> 
                     <Fun-SAT enable (1 or 0)>
```
Note when the Fun-SAT feature is not enabled, i.e., the last argument is 0, all Fun-SAT-related arguments will not be used. However, the user should still put some arbitrary values as the placeholder. 

Sample Command (with the Fun-SAT feature):
------
```python unroll_sat.py ./sample_run/s27_ori.v ./sample_run/s27_kl4_uc10.v 4 50 0.01 5 1000 100000 1```

Sample Output:
------

```*****************************************

Original netlist: ./sample_run/s27_ori.v
Encrypted netlist: ./sample_run/s27_kl4_uc10.v
Key length in cycle count: 4
Original netlist: Verilog to Bench finished.
Encrypted netlist: Verilog to Bench finished.
Original netlist: Sequential to Combinational finished.
Encrypted netlist: Sequential to Combinational finished.

********** FC analysis phase ************

Simulating... (Unroll_count=1) 0.0
Simulating... (Unroll_count=2) 0.121
Simulating... (Unroll_count=3) 0.232
Simulating... (Unroll_count=4) 0.36
Simulating... (Unroll_count=5) 0.43
Simulating... (Unroll_count=6) 0.565
Simulating... (Unroll_count=7) 0.679
Simulating... (Unroll_count=8) 0.776
Simulating... (Unroll_count=9) 0.893
Simulating... (Unroll_count=10) 1.0
Simulating... (Unroll_count=11) 1.0
Simulating... (Unroll_count=12) 1.0
Simulating... (Unroll_count=13) 1.0
Simulating... (Unroll_count=14) 1.0
Simulating... (Unroll_count=15) 1.0

********** SAT attack phase *************

Feasible unroll cycles: 11
#DIPs = 2
Key prediction: 1001100101111100
Unique key passed!
key=1001100101111100

********** Attack Summary ***************

TotalRuntime: 46.11986494064331 sec.
Runtime (Attack): 45.779550552368164 sec.
UC:1, BMC:0, UMC:0
Succeeded at unroll cycles b=11
key=1001100101111100
```
Cite our work:
------
Please cite our work if you find this codebase useful to you:

```
@inproceedings{hu2021fun,
  title={{Fun-SAT}: Functional Corruptibility-Guided {SAT}-Based Attack on Sequential Logic Encryption},
  author={Hu, Yinghua and Zhang, Yuke and Yang, Kaixin and Chen, Dake and Beerel, Peter A and Nuzzo, Pierluigi},
  booktitle={International Symposium on Hardware Oriented Security and Trust (HOST)},
  year={2021},
  organization={IEEE}
}
```
