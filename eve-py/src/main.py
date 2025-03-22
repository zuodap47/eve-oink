# -*- coding: utf-8 -*-

import time
import sys
import getopt
import subprocess  # 添加 subprocess 模块以调用 Oink
from parsrml import *
from arena2kripke import *
from srml2lts import *
from ltl2nbw import *
from nbw2dpw import *
from gltl2gpar import convertG, drawGPar, convertG_cgs
from utils import *
from nonemptiness import *
from enash import *
from anash import *


def parse_oink_output(output):
    """
    解析 Oink 的输出。
    假设 Oink 的输出格式为：Solution: [0, 1, 2]
    """
    if "Solution:" in output:
        solution = output.split("Solution:")[1].strip()  # 提取解决方案部分
        solution = solution.strip("[]").split(",")       # 解析为列表
        solution = [int(s.strip()) for s in solution]    # 转换为整数列表
        return solution
    else:
        raise ValueError("Oink output format not recognized")


def generate_parity_game(GPar):
    """
    将 GPar 转换为奇偶游戏的输入格式。
    """
    if not hasattr(GPar, 'vs'):
        raise ValueError("GPar 必须是一个图对象")

    parity_game_content = ""
    for v in GPar.vs:
        # 检查顶点是否包含 priority 和 player 属性
        if 'priority' not in v.attributes() or 'player' not in v.attributes():
            raise ValueError(f"顶点 {v.index} 缺少 'priority' 或 'player' 属性")

        # 顶点编号、优先级、玩家（0 或 1）、后继顶点
        parity_game_content += f"{v.index} {v['priority']} {v['player']} {' '.join(map(str, GPar.successors(v.index)))}\n"
    return parity_game_content


def print_performance(perfConstruction, perfParser, perfoink, empCheck, GPar_v, GPar_e, TTPG_vmax, TTPG_emax, q_flag):
    problem = ["E-Nash", "A-Nash", "Membership", "Non-Emptiness"]
    print('Parser Performance (milisecond)', perfParser)
    print('GPar Construction Performance (milisecond)', perfConstruction)
    print('Oink Performance (milisecond)', perfoink)
    print(problem[q_flag - 1] + ' performance (milisecond)', empCheck)
    print('Total performance (milisecond)', perfParser + perfConstruction + perfoink + empCheck)
    print('GPar states', GPar_v)
    print('GPar edges', GPar_e)
    print('Max TTPG states', TTPG_vmax)
    print('Max TTPG edges', TTPG_emax)


def printhelp():
    print("usage: main.py [problem] [path/name of the file] [options]\n")
    print("List of problems:")
    print("a \t Solve A-Nash")
    print("e \t Solve E-Nash")
    print("n \t Solve Non-Emptiness")
    print("\nList of optional arguments:")
    print("-d \t Draw the structures")
    print("-v \t verbose mode")
    print("\n")
    sys.exit()


def main(argv):
    print("Raw command line arguments:", sys.argv)  # 打印出原始的命令行参数
    args_list = list(sys.argv)
    print("args_list:", args_list)  # 打印出处理后的命令行参数

    file_name = args_list[2]  # 获取文件路径
    print("File path:", file_name)

    prob = str(args_list[1])  # 获取问题类型
    q_flag = 0
    print("args_list:", args_list)
    # Default values for flags
    with open("verbose_flag", "w") as f:
        f.write("0")
    verbose = False

    with open("draw_flag", "w") as f:
        f.write("0")
    draw_flag = False

    # Parse command-line options
    try:
        opts, args = getopt.getopt(argv, "vd")
    except getopt.GetoptError:
        printhelp()

    for o, a in opts:
        if o == "-d":
            with open("draw_flag", "w") as f:
                f.write("1")
            draw_flag = True
        elif o == "-v":
            with open("verbose_flag", "w") as f:
                f.write("1")
            verbose = True
        else:
            print("ERROR: Undefined option")
            printhelp()

    # Read and parse the file
    perfParser = 0.0
    start = time.time() * 1000
    if (yacc.parse(open(str(file_name)).read())) != False:
        perfParser = time.time() * 1000 - start
    if len(environment) != 0:
        cgsFlag = True
    else:
        cgsFlag = False

    perfConstruction = 0.0
    start = time.time() * 1000

    # Get the property formula for E/A-Nash
    try:
        if prob != "n" and len(propFormula) == 0:  # 仅在非 Non-Emptiness 功能时检查属性公式
            print("Error: No property formula input...")
            sys.exit(1)
        else:
            pf = str(propFormula[0]) if len(propFormula) > 0 else None  # 如果属性公式存在，则访问第一个元素
    except IndexError:
        pf = None

    if prob == "e":
        if pf == None:
            print("No property formula input...")
        else:
            print("Checking E-Nash property formula: " + replace_symbols(pf))
        q_flag = 1

        # Convert \\phi to NBW
        NBW_prop = ltl2nbw(propFormula[0], PFAlphabets[0])
        DPW_prop = nbw2dpw(NBW_prop, PFAlphabets[0])

    elif prob == "a":
        if pf == None:
            print("No property formula input...")
        else:
            print("Checking A-Nash property formula: " + replace_symbols(pf))
        # Convert \\phi to NBW
        NBW_prop = ltl2nbw('!(' + propFormula[0] + ')', PFAlphabets[0])
        DPW_prop = nbw2dpw(NBW_prop, PFAlphabets[0])
        q_flag = 2
    elif prob == "n":
        print("Solving Non-Emptiness of " + file_name)
        q_flag = 4
    else:
        print("ERROR: Undefined problem")
        printhelp()

    if cgsFlag:
        # Concurrent Game uses LTS instead of KS
        M = Arena2LTS(modules)
    else:
        # RMG uses Kripke structure
        M = Arena2Kripke(modules)

    updateLabM(M)
    print("Kripke states", M.vcount())
    print("Kripke edges", M.ecount())

    '''Don't need to do LTL2DPW conversion for memoryless case'''
    if q_flag in [1, 2, 4]:
        NBWs = Graph(directed=True)
        DPWs = Graph(directed=True)

        '''Convert NBWs to DPWs'''
        for m in modules:
            NBWs[list(m[1])[0]] = ltl2nbw(list(m[5])[0], list(m[6]))
            NBWs[list(m[1])[0]]['goal'] = list(m[5])[0]
            goal = list(m[5])[0]
            goal = replace_symbols(goal)
            print(list(m[1])[0], goal)
            DPWs[list(m[1])[0]] = nbw2dpw(NBWs[list(m[1])[0]], list(m[6]))

        if not cgsFlag:
            if verbose:
                print("\n Convert G_{LTL} to G_{PAR}...\n")
            GPar = convertG(modules, DPWs, M)

        else:
            if verbose:
                print("\n Convert G_{LTL} to G_{PAR}...\n")
            GPar = convertG_cgs(modules, DPWs, M)

        GPar_v = GPar.vcount()
        GPar_e = GPar.ecount()
        perfConstruction = time.time() * 1000 - start
    else:
        print("ERROR: Undefined problem")
        printhelp()

    if q_flag == 1:
        '''E-Nash'''
        empCheck = 0.0
        perfoink = 0.0
        TTPG_vmax = 0
        TTPG_emax = 0
        start = time.time() * 1000
        perfoink, TTPG_vmax, TTPG_emax = enash(modules, GPar, draw_flag, cgsFlag, pf, DPW_prop, PFAlphabets[0])
        empCheck = time.time() * 1000 - start
    elif q_flag == 2:
        '''A-Nash'''
        empCheck = 0.0
        perfoink = 0.0
        TTPG_vmax = 0
        TTPG_emax = 0
        start = time.time() * 1000
        perfoink, TTPG_vmax, TTPG_emax = anash(modules, GPar, draw_flag, cgsFlag, pf, DPW_prop, PFAlphabets[0])
        empCheck = time.time() * 1000 - start
    elif q_flag == 4:
        '''Solving Non-Emptiness'''
        empCheck = 0.0
        perfoink = 0.0
        TTPG_vmax = 0
        TTPG_emax = 0
        start = time.time() * 1000
        perfoink, TTPG_vmax, TTPG_emax = nonemptiness(modules, GPar, draw_flag, cgsFlag)
        empCheck = time.time() * 1000 - start
    else:
        print("Undefined Problem!")
        printhelp()
        return True

    if (q_flag not in [6, 7, 8]) and verbose:
        print_performance(perfConstruction, perfParser, perfoink, empCheck, GPar_v, GPar_e, TTPG_vmax, TTPG_emax, q_flag)


if __name__ == "__main__":
    main(sys.argv[3:])

print("Formula:", propFormula)
print("Parsed property formula:", propFormula)
