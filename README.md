# eve-oink
Faster parity game solver for faster rational verification (Integrating oink into EVEE) 

# EVE with Oink Integration
Equilibrium Verification Environment

__EVE__ (Equilibrium Verification Environment) is a formal verification tool for the automated analysis of temporal equilibrium properties of concurrent and multi-agent systems represented as multi-player games (see [rational verification](https://link.springer.com/article/10.1007/s10489-021-02658-y)). Systems/Games in EVE are modeled using the Simple Reactive Module Language (SRML) as a collection of independent system components (players/agents in a game). These components/players are assumed to have goals expressed using Linear Temporal Logic (LTL) formulae. __EVE__ checks for the existence of Nash equilibria in such systems and can be used to do rational synthesis and verification automatically.

## Publications
1. **Automated Temporal Equilibrium Analysis: Verification and Synthesis of Multi-Player Games**  
   - Authors: J. Gutierrez, M. Najib, G. Perelli, and M. Wooldridge  
   - Published in *Artificial Intelligence*, 2020.  
   - [DOI](https://doi.org/10.1016/j.artint.2020.103353) | [PDF](aij20.pdf)

2. **EVE: A Tool for Temporal Equilibrium Analysis**  
   - Authors: J. Gutierrez, M. Najib, G. Perelli, and M. Wooldridge  
   - In *Proceedings of the 16th International Symposium on Automated Technology for Verification and Analysis (ATVA-2018)*, Los Angeles, October 2018.  
   - [DOI](https://doi.org/10.1007/978-3-030-01090-4_35) | [PDF](atva18.pdf)


The main repository of EVE is: [https://github.com/eve-mas/eve-parity](https://github.com/eve-mas/eve-parity).

---

## Oink Integration
EVE now integrates **Oink**, a modern implementation of parity game solvers written in C++. Oink provides high-performance implementations of state-of-the-art algorithms for solving parity games, replacing the previously used PGSolver. Oink is licensed under the Apache 2.0 license and is designed for both researchers and practitioners.

### About Oink
Oink was initially developed (&copy; 2017-2021) by Tom van Dijk and the [Formal Models and Verification](http://fmv.jku.at/) group at the Johannes Kepler University Linz as part of the RiSE project. It is now maintained in the [Formal Methods and Tools](https://fmt.ewi.utwente.nl) group at the University of Twente.

The main author of Oink is Tom van Dijk, who can be reached via <tom@tvandijk.nl>. If you use Oink in your projects, please let us know. Researchers are encouraged to cite the following publication:

- Tom van Dijk (2018) [Oink: An Implementation and Evaluation of Modern Parity Game Solvers](https://doi.org/10.1007/978-3-319-89960-2_16). In: TACAS 2018.

The main repository of Oink is: [https://github.com/trolando/oink](https://github.com/trolando/oink).

---

## Supported Platforms
EVE runs on **Linux/UNIX** platforms, including:
1. Fedora
2. Ubuntu
3. macOS

For convenience, EVE is also available as a preinstalled **Open Virtual Appliance (OVA)** image running Lubuntu (a lightweight Linux based on Ubuntu). The image (1.5 GB) can be downloaded from [https://goo.gl/ikdSnw](https://goo.gl/ikdSnw) and run directly on **VirtualBox** ([https://www.virtualbox.org/](https://www.virtualbox.org/)).

### Windows Users
Windows users can run EVE via **WSL Ubuntu** ([https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-10#1-overview)). Note: You may need to disable sandboxing when initializing OPAM (see: [https://stackoverflow.com/questions/54987110/installing-ocaml-on-windows-10-using-wsl-ubuntu-problems-with-bwrap-bubblewr](https://stackoverflow.com/questions/54987110/installing-ocaml-on-windows-10-using-wsl-ubuntu-problems-with-bwrap-bubblewr)).

---

## Installation

### Prerequisites
Before installing EVE, ensure the following prerequisites are installed:
1. **Python 3.x**
2. **OPAM** ([https://opam.ocaml.org/doc/Install.html](https://opam.ocaml.org/doc/Install.html)) + **OCaml** version 4.03.0 or later ([https://ocaml.org/docs/install.html](https://ocaml.org/docs/install.html)).  
   To check the OCaml version, run:  
   ```bash
   ocaml --version
   ```
   To initialize OPAM (along with OCaml):  
   ```bash
   echo "y" | opam init
   eval `opam config env`
   ```
3. **Cairo** ([https://cairographics.org/download/](https://cairographics.org/download/)) or **Pycairo** ([https://pycairo.readthedocs.io/en/latest/index.html](https://pycairo.readthedocs.io/en/latest/index.html))
4. **IGraph** version 0.7 or later ([http://igraph.org/python/](http://igraph.org/python/))
5. **Oink** (see installation instructions below)

### Installing Oink
Oink is compiled using CMake. Optionally, use `ccmake` to set options. By default, Oink does not compile the extra tools, only the library `liboink` and the main tools `oink` and `test_solvers`. Oink requires several Boost libraries.
```bash
mkdir build && cd build
cmake .. && make
ctest
```

### Configuration Steps
1. Ensure all prerequisites are installed.
2. Navigate to the `eve-py` folder.
3. Run the executable script **./config.sh** (you may need to run `chmod +x config.sh` first).  
   **Note:** Ensure OCaml is version 4.03.0 or later before running `config.sh`.

---

## Usage

### Basic Usage
From inside the folder **eve-py/src**, execute the following command:  
```bash
python main.py [problem] [path/name of the file] [options]
```

#### List of Problems:
- `a`: Solve **A-Nash** problem.
- `e`: Solve **E-Nash** problem.
- `n`: Solve **Non-Emptiness** problem.

#### List of Optional Arguments:
- `-d`: Draw the structures.
- `-v`: Execute in verbose mode.

#### Example:
```bash
python main.py a ../examples/a-nash_1 -d
```
This solves the **A-Nash** problem and draws the structures. The drawing will be saved in the current (`src`) folder as `str.png`.

---

## Running Experiments
1. Navigate to the folder **eve-py/src/experiments**. There are 8 scripts available (you may need to run `chmod +x <script_filename.sh>` to make them executable):
   - `bisim_ne_emptiness.sh`
   - `bisim_none_emptiness.sh`
   - `gossip_protocol_emptiness.sh`
   - `gossip_protocol_enash.sh`
   - `gossip_protocol_anash.sh`
   - `replica_control_emptiness.sh`
   - `replica_control_enash.sh`
   - `replica_control_anash.sh`

2. Execute the script using the command:  
   ```bash
   ./experiment_name.sh 8
   ```
   This will run the experiment up to 8 steps.

3. The results are saved in the file **exetime_experiment_name.txt**, with the following values separated by semicolons:
   - Parser performance (ms)
   - Construction performance (ms)
   - Oink performance (ms)
   - Non-emptiness/E-Nash/A-Nash performance (ms)
   - Total number of parity game states
   - Total number of parity game edges
   - Maximum total number of sequentialised parity game states
   - Maximum total number of sequentialised parity game edges
   - Total time performance (ms)

---

## Oink Tools
Oink comes with several tools built around the library `liboink`:

### Main Tools
Tool          | Description
:------------ | :-------------
oink          | The main tool for solving parity games
verify        | Small tool that verifies a solution
nudge         | Swiss army knife for transforming parity games
dotty         | Generates a .dot graph of a parity game
test_solvers  | Main testing tool for parity game solvers and benchmarking

### Game Generators
Tool           | Description
:------------- | :----------
rngame         | Faster version of the random game generator of PGSolver
stgame         | Faster version of the steady game generator of PGSolver
counter_rr     | Counterexample to the RR solver
counter_dp     | Counterexample to the DP solver
counter_m      | Counterexample of Maciej Gazda, PhD Thesis, Sec. 3.5
counter_qpt    | Counterexample of Fearnley et al
counter_core   | Counterexample of Benerecetti, Dell'Erba, Mogavero
counter_rob    | SCC version of counter_core
counter_dtl    | Counterexample to the DTL solver
counter_ortl   | Counterexample to the ORTL solver
counter_symsi  | Counterexample of Matthew Maat to symmetric strategy improvement
tc             | Two binary counters generator
tc+            | TC modified to defeat the RTL solver

---

For further assistance or inquiries, please contact [yc2033@hw.ac.uk]
