from parsrml import *
from srmlutil import *
from igraph import Graph
import copy


def Arena2Kripke(mdl):
    """
    将 SRML 竞技场转换为 Kripke 结构。
    """
    KripkeStruct = Graph(directed=True)
    S0 = set()  # 初始状态集合
    S = set()  # 状态集合

    # 添加初始状态
    for state in productInit(mdl):
        stateLabel = getValuation(state)
        if stateLabel is None:
            stateLabel = frozenset()
        else:
            stateLabel = frozenset(stateLabel)

        # 添加顶点，并设置 priority 和 player 属性
        v = KripkeStruct.add_vertex(label=stateLabel)
        v['priority'] = 0  # 默认优先级
        v['player'] = 0  # 默认玩家

        # 添加到初始状态集合和状态集合
        S0.add(stateLabel)
        S.add(stateLabel)

    # 构建状态转移
    prevS = set()
    while prevS != S:
        prevS = copy.copy(S)
        for state in KripkeStruct.vs:
            for updateCommand in jointEnabled(guardEval(state['label'], mdl)):
                commands = []
                for k, v in updateCommand:
                    # 移除 guard 键
                    updateCommand_noguard = without_keys(v, 'guard')
                    for var, expr in updateCommand_noguard.items():
                        if var != 0:  # 排除名称检查
                            commands.append(str({var: parse_rpn(state['label'], expr)}))

                # 计算下一个状态
                try:
                    nextState = frozenset(getValuation(tuple(commands)))
                except TypeError:
                    nextState = frozenset()

                # 如果下一个状态不在 S 中，则添加到 KripkeStruct
                if nextState not in S:
                    S.add(nextState)
                    v = KripkeStruct.add_vertex(label=nextState)
                    v['priority'] = 0  # 默认优先级
                    v['player'] = 0  # 默认玩家

    # 添加边
    for currentState in KripkeStruct.vs:
        for updateCommand in jointEnabled(guardEval(list(currentState['label']), mdl)):
            commands = []
            for k, v in updateCommand:
                # 移除 guard 键
                updateCommand_noguard = without_keys(v, 'guard')
                for var, expr in updateCommand_noguard.items():
                    if var != 0:  # 排除名称检查
                        commands.append(str({var: parse_rpn(currentState['label'], expr)}))

            # 计算下一个状态
            cmdval = getValuation(commands)
            if cmdval is None:
                cmdval = frozenset()
            else:
                cmdval = frozenset(cmdval)

            # 找到下一个状态对应的顶点
            nextVertex = KripkeStruct.vs.find(label=cmdval)
            KripkeStruct.add_edge(currentState.index, nextVertex.index)

    return KripkeStruct


def print_K(KripkeStruct):
    """
    打印 Kripke 结构的信息。
    """
    print("顶点信息：")
    for v in KripkeStruct.vs:
        print(f"顶点 {v.index}: label={v['label']}, priority={v['priority']}, player={v['player']}")

    print("边信息：")
    for e in KripkeStruct.es:
        print(f"边 {e.tuple[0]} -> {e.tuple[1]}")
