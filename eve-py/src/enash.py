# -*- coding: utf-8 -*-
from utils import *
from gltl2gpar import drawGPar, sequencer_rmg_single, sequencer_cgs_single
from generatepun import compute_pun
import time


def enash(modules, GPar, draw_flag, cgsFlag, pf, DPW_prop, alphabets):
    """
    检查是否存在某个 Nash 均衡满足给定属性。

    参数：
    - modules: 玩家模块列表
    - GPar: 游戏图
    - draw_flag: 是否绘制策略图
    - cgsFlag: 是否为 CGS 模式
    - pf: 属性公式
    - DPW_prop: 属性对应的 DPW 自动机
    - alphabets: 字母表

    返回：
    - perfPGSolver: PGSolver 的性能统计（毫秒）
    - TTPG_vmax: TTPG 的最大顶点数
    - TTPG_emax: TTPG 的最大边数
    """
    TTPG_vmax = 0  # 记录 TTPG/GPar 序列化中的最大顶点数
    TTPG_emax = 0  # 记录 TTPG/GPar 序列化中的最大边数
    TTPG = {}      # 使用字典存储每个玩家的图对象
    perfPGSolver = 0.0  # 性能统计

    # 生成 W（获胜联盟），反转列表以从大到小生成
    W = list(reversed(generate_set_W(modules)))

    # 计算 G^{-L}_{PAR}
    GPar_L = Graph(directed=True)
    NE_flag = False  # Nash 均衡标志
    PUN = {}         # 惩罚区域

    for w in W:
        if len(w) == len(modules):
            # 平凡情况：全部玩家获胜或失败
            s_Alpha = build_streett_prod(GPar, w, modules)
            L, L_sigma = Streett_emptyness(GPar, s_Alpha, modules)

            # 如果不为空
            if L.vcount() != 0:
                DPW_product = graph_product(GPar, DPW_prop, alphabets, cgsFlag)
                e_Alpha = build_streett_prod(DPW_product, w + (len(modules),), modules + [{1: set(['environment'])}])
                E, E_sigma = Streett_emptyness(DPW_product, e_Alpha, modules + [{1: set(['environment'])}])

                if E.vcount() != 0:
                    print('>>> YES, the property ' + replace_symbols(pf) + ' is satisfied in SOME NE <<<')
                    NE_flag = True
                    if draw_flag:
                        # 绘制并打印策略配置文件 \vec{sigma}
                        drawGPar(E_sigma)
                        printSynthSigmaDetails(E_sigma)

                        # 合成与策略配置文件对应的 lasso 运行
                        synth_lasso(E_sigma, e_Alpha, cgsFlag)
                    break
        else:
            l = get_l(list(w), modules)
            PUN_L = set([v.index for v in GPar.vs])
            for pl in l:
                pl_name = list(modules[pl][1])[0]
                try:
                    if TTPG.get(pl_name, None):  # 使用 get 方法避免 KeyError
                        pass
                except KeyError:
                    if check_verbose_flag():
                        print("\n Sequentialising GPar for punishing <" + pl_name + ">")
                    if not cgsFlag:
                        startPGSolver = time.time() * 1000
                        TTPG[pl_name] = Graph(directed=True)  # 初始化图对象
                        sequencer_rmg_single(pl, GPar, TTPG[pl_name], modules)
                        perfPGSolver = perfPGSolver + time.time() * 1000 - startPGSolver
                        if TTPG_vmax < TTPG[pl_name].vcount():
                            TTPG_vmax = TTPG[pl_name].vcount()
                        if TTPG_emax < TTPG[pl_name].ecount():
                            TTPG_emax = TTPG[pl_name].ecount()
                    else:
                        startPGSolver = time.time() * 1000
                        TTPG[pl_name] = Graph(directed=True)  # 初始化图对象
                        sequencer_cgs_single(pl, GPar, TTPG[pl_name], modules)
                        perfPGSolver = perfPGSolver + time.time() * 1000 - startPGSolver
                        if TTPG_vmax < TTPG[pl_name].vcount():
                            TTPG_vmax = TTPG[pl_name].vcount()
                        if TTPG_emax < TTPG[pl_name].ecount():
                            TTPG_emax = TTPG[pl_name].ecount()

                # 确保 TTPG[pl_name] 已初始化
                if pl_name not in TTPG:
                    TTPG[pl_name] = Graph(directed=True)  # 如果未初始化，则初始化

                # 计算 pl_name 的惩罚区域
                if pl_name not in PUN:
                    if check_verbose_flag():
                        print("\n Computing punishing region for <" + pl_name + ">")
                    startPGSolver = time.time() * 1000
                    PUN = compute_pun(pl_name, PUN, TTPG)
                    perfPGSolver = perfPGSolver + time.time() * 1000 - startPGSolver
                PUN_L = PUN_L.intersection(set(PUN[pl_name]))

                # 初始状态 s0 不包含在 PUN_L 中
                if 0 in PUN_L:
                    GPar_L[frozenset(l)] = build_GPar_L(GPar, w, l, PUN_L)
                else:
                    GPar_L[frozenset(l)] = Graph(directed=True)

            if GPar_L[frozenset(l)].vcount() != 0:
                # 构建 Streett 自动机的乘积
                s_Alpha = build_streett_prod(GPar_L[frozenset(l)], w, modules)
                L, L_sigma = Streett_emptyness(GPar_L[frozenset(l)], s_Alpha, modules)

                # 如果不为空
                if L.vcount() != 0:
                    DPW_product = graph_product(L_sigma, DPW_prop, alphabets, cgsFlag)
                    e_Alpha = build_streett_prod(DPW_product, w + (len(modules),), modules + [{1: set(['environment'])}])
                    E, E_sigma = Streett_emptyness(DPW_product, e_Alpha, modules + [{1: set(['environment'])}])

                    if E.vcount() != 0:
                        print('>>> YES, the property ' + replace_symbols(pf) + ' is satisfied in SOME NE <<<')
                        NE_flag = True
                        if draw_flag:
                            # 绘制并打印策略配置文件 \vec{sigma}
                            drawGPar(E_sigma)
                            printSynthSigmaDetails(E_sigma)

                            # 合成与策略配置文件对应的 lasso 运行
                            synth_lasso(E_sigma, e_Alpha, cgsFlag)
                        break

    if not NE_flag:
        print('>>> NO, the property ' + replace_symbols(pf) + ' is not satisfied in ANY NE <<<')
        if draw_flag:
            # 如果没有找到 Nash 均衡，绘制默认策略图
            drawGPar(L_sigma)
            printSynthSigmaDetails(L_sigma)

    return perfPGSolver, TTPG_vmax, TTPG_emax
