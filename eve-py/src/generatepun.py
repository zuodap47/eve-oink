# -*- coding: utf-8 -*-
from gltl2gpar import get_max_prior
import subprocess as sp

'''this generates input file for PGSolver from TTPG igraph structure'''
def ttpg2gm(TTPG,pl):
    max_idt=TTPG[pl].vcount() #highest occuring identifier
    max_prior = get_max_prior(TTPG[pl])
#    print 'parity '+str(max_idt)+';'
    tofile = 'parity '+str(max_idt)+';'
    for v in TTPG[pl].vs:
#        to_file=str(v.index)+' '+
        if v['itd']==True:
            own=1
        else:
            own=0
            
#        if len(v.successors())==1:
#            suc_list = str(v.successors()[0].index)
#        else:
#            for suc in v.successors():
#                suc_list = suc_list+','+
            
        for num,suc in enumerate(v.successors()):
            if num==0:
                suc_list = str(suc.index)
            else:
                suc_list = suc_list+','+str(suc.index)
#        print str(v.index)+' '+str(v['prior'])+' '+str(own)+' '+suc_list+';'
        tofile = tofile+'\n'+str(v.index)+' '+str((2*max_prior)-v['prior'])+' '+str(own)+' '+suc_list+';'
    f = open('/home/mirror/eve-parity-master/eve-py/temp/ttpg_'+pl,'w')
    f.write(tofile)
    f.close()
    


def compute_pun(pl_name, PUN, TTPG):
    '''从 TTPG 转换为 Oink 格式'''
    ttpg2gm(TTPG, pl_name)
    
    '''调用 Oink 计算 Pun_i'''
    oink_cmd = [
        '/usr/local/bin/oink',  # 确保 Oink 路径正确
        '--solver', 'fpi',      # 选择 fpi 作为求解算法（可以换成其他算法）
        '--timeout', '300',     # 设定超时（秒）
        '--print',              # 输出结果到终端
        '../temp/ttpg_%s' % pl_name  # 输入的 TTPG 文件路径
    ]

    try:
        process = sp.Popen(oink_cmd, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf8')
        out, err = process.communicate()
        
        if err:
            print("Oink 错误信息：", err)

        ttpg_results = {}
        out_lines = out.splitlines()
        
        for line in out_lines:
            words = line.split(" ")
            if words[0] == "Player":
                pl = words[1]
            for c in words:
                try:
                    if c[0] == "{":
                        ttpg_results[int(pl)] = line
                except IndexError:
                    pass
        
        # Debug 输出，查看 Oink 结果
        print("Oink 解析结果:", ttpg_results)
        
        try:
            PUN[pl_name] = list(map(int, ttpg_results[0].strip()[1:-1].replace(' ', '').split(',')))
        except (ValueError, KeyError):
            PUN[pl_name] = []
    
    except FileNotFoundError:
        print(f"错误：未找到 Oink 可执行文件，请检查路径 {oink_cmd[0]}")
        PUN[pl_name] = []
    
    return PUN
