import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import platform, os
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

def setup_cjk_fonts():
    system = platform.system()
    if system == 'Windows':
        candidates_r = ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf']
        candidates_b = ['C:/Windows/Fonts/msyhbd.ttc', 'C:/Windows/Fonts/simhei.ttf']
    elif system == 'Darwin':
        candidates_r = ['/System/Library/Fonts/PingFang.ttc']
        candidates_b = ['/System/Library/Fonts/PingFang.ttc']
    else:
        candidates_r = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
        candidates_b = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']
    font_r = next((font_manager.FontProperties(fname=fp) for fp in candidates_r if os.path.exists(fp)), None)
    font_b = next((font_manager.FontProperties(fname=fp) for fp in candidates_b if os.path.exists(fp)), None)
    return font_r, (font_b or font_r)

CJK_FONT, CJK_BOLD = setup_cjk_fonts()

def txcjk(ax, x, y, text, fs=10, bold=False, **kw):
    fp = CJK_BOLD if bold else CJK_FONT
    if fp:
        ax.text(x, y, text, fontsize=fs, fontproperties=fp, **kw)
    else:
        ax.text(x, y, text, fontsize=fs, fontfamily='sans-serif', fontweight='bold' if bold else 'normal', **kw)

def run_optimization_and_sankey(iso_code, alpha=0.5517, friction_coef=0.0125, db_path='GH_Copilot_Knowledge_Base_Final.csv'):
    # 1. 动态数据接入
    df = pd.read_csv(db_path)
    if iso_code not in df['ISO_Code'].values:
        return f"Error: 找不到国家 {iso_code} 的数据"
        
    country_data = df[df['ISO_Code'] == iso_code].iloc[-1]
    country_name = country_data['Country_Name']
    
    # 提取真实因果弹性与资金本底
    cates = np.array([country_data['CATE_Clinical'], country_data['CATE_Admin'], 
                      country_data['CATE_PublicHealth'], country_data['CATE_Env'], country_data['CATE_Tobacco']])
    current_B = np.array([country_data['Clinical_Budget_Pct'], country_data['Admin_Budget_Pct'], 
                          country_data['PublicHealth_Pct'], country_data['Env_Pct'], country_data['Tobacco_Pct']])
    
    # 2. MO-QPO 寻优
    def objective(delta): return - (alpha * np.sum(delta * cates)) + (friction_coef * np.sum(delta**2))
    def jacobian(delta): return - (alpha * cates) + (2 * friction_coef * delta)
    bounds = [(-15.0, 0.0), (-3.0, 0.0), (0.0, 0.0), (0.0, 15.0), (0.0, 15.0)]
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x)})
    res = minimize(objective, np.zeros(5), method='SLSQP', jac=jacobian, bounds=bounds, constraints=cons)
    delta_B = np.round(res.x, 2)
    optimal_B = np.round(current_B + delta_B, 2)

    # 3. 构建流转矩阵
    N_NODES = 5
    flow_matrix = np.zeros((N_NODES, N_NODES))
    pool_total = np.sum(delta_B[delta_B > 0])
    if pool_total > 0.001:
        for i in range(N_NODES):
            if delta_B[i] < 0: 
                flow_matrix[i][i] = current_B[i] + delta_B[i] 
                for j in range(N_NODES):
                    if delta_B[j] > 0: flow_matrix[i][j] = (-delta_B[i]) * (delta_B[j] / pool_total)
            else: flow_matrix[i][i] = current_B[i]
    else: np.fill_diagonal(flow_matrix, current_B)
    
    lt = [round(sum(row), 2) for row in flow_matrix] 
    rt = [round(sum(flow_matrix[i][j] for i in range(N_NODES)), 2) for j in range(N_NODES)]
    S = sum(lt)

    # 4. 你的专属高级 Sankey 画图引擎
    nodes_info = [("专科临床与医师资源", "Clinical & Physicians", "#1976D2"),
                  ("医疗转化与行政管理", "Admin & Efficiency", "#00695C"),
                  ("基础公共卫生服务", "Basic Public Health", "#2E7D32"),
                  ("空气质量与环境治理", "Air Pollution Control", "#E64A19"),
                  ("烟草管控与行为防线", "Tobacco & NCDs", "#B71C1C")]

    FIG_W, FIG_H, LEFT_X, RIGHT_X, NODE_W, GAP = 16, 9, 0.22, 0.78, 0.02, 0.02
    A = 1.0 - (N_NODES - 1) * GAP

    def build_node_positions(vals):
        nodes, y = [], 0.0
        for v in vals:
            h = (v / S) * A
            nodes.append((y, h))
            y += h + GAP
        offset = (1.0 - (y - GAP)) / 2   
        return [(yy + offset, hh) for yy, hh in nodes]

    LN, RN = build_node_positions(lt[::-1])[::-1], build_node_positions(rt[::-1])[::-1]

    def draw_bezier_flow(ax, x0, y0, x1, y1, h0, h1, color, alpha=0.35):
        N = 100  
        cx0, cx1 = x0 + (x1 - x0) * 0.38, x0 + (x1 - x0) * 0.62
        top_pts, bot_pts = [], []
        for i in range(N + 1):
            t = i / N
            bx = (1-t)**3*x0 + 3*(1-t)**2*t*cx0 + 3*(1-t)*t**2*cx1 + t**3*x1
            by_top = (1-t)**3*(y0+h0) + 3*(1-t)**2*t*(y0+h0) + 3*(1-t)*t**2*(y1+h1) + t**3*(y1+h1)
            by_bot = (1-t)**3*y0 + 3*(1-t)**2*t*y0 + 3*(1-t)*t**2*y1 + t**3*y1
            top_pts.append((bx, by_top)); bot_pts.append((bx, by_bot))
        verts = top_pts + bot_pts[::-1] + [top_pts[0]]
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(mpatches.PathPatch(Path(verts, codes), facecolor=color, edgecolor='none', alpha=alpha, zorder=2, antialiased=True))
        for pts in [top_pts, bot_pts]:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, alpha=min(alpha + 0.12, 0.55), linewidth=0.25, zorder=3)

    fig, ax = plt.subplots(1, 1, figsize=(FIG_W, FIG_H), dpi=150)
    fig.patch.set_facecolor('#FAFBFD'); ax.set_facecolor('#FAFBFD')
    lc, rc = [n[0] for n in LN], [n[0] for n in RN] 

    for i in range(N_NODES):
        for j in range(N_NODES):
            v = flow_matrix[i][j]
            if v < 0.001: continue
            h = (v / S) * A
            is_self = (i == j)
            color, alpha = ('#B0BEC5', 0.20) if is_self else (nodes_info[i][2], 0.60)
            draw_bezier_flow(ax, LEFT_X+NODE_W, lc[i], RIGHT_X, rc[j], h, h, color, alpha=alpha)
            lc[i] += h; rc[j] += h

    for i in range(N_NODES):
        y, h = LN[i]
        ax.add_patch(mpatches.FancyBboxPatch((LEFT_X, y), NODE_W, h, boxstyle="round,pad=0.0015", facecolor=nodes_info[i][2], edgecolor='white', linewidth=1.2, zorder=5))
        txcjk(ax, LEFT_X-0.015, y+h/2+0.015, nodes_info[i][0], fs=11, bold=True, color='#1A237E', ha='right', va='center', zorder=10)
        ax.text(LEFT_X-0.015, y+h/2-0.015, f'{nodes_info[i][1]}  ({lt[i]:.1f}%)', fontsize=9, color='#546E7A', ha='right', va='center', style='italic', fontfamily='sans-serif', zorder=10)
        
        y_r, h_r = RN[i]
        ax.add_patch(mpatches.FancyBboxPatch((RIGHT_X, y_r), NODE_W, h_r, boxstyle="round,pad=0.0015", facecolor=nodes_info[i][2], edgecolor='white', linewidth=1.2, zorder=5))
        pct_change = round(rt[i] - lt[i], 2)
        sign = "+" if pct_change > 0 else ""
        color_text = '#B71C1C' if pct_change > 0 else ('#1976D2' if pct_change < 0 else '#546E7A')
        txcjk(ax, RIGHT_X+NODE_W+0.015, y_r+h_r/2+0.015, nodes_info[i][0], fs=11, bold=True, color='#1A237E', ha='left', va='center', zorder=10)
        ax.text(RIGHT_X+NODE_W+0.015, y_r+h_r/2-0.015, f'{nodes_info[i][1]}  ({rt[i]:.2f}%, {sign}{pct_change:.2f}%)', fontsize=9, color=color_text, ha='left', va='center', fontweight='bold', fontfamily='sans-serif', zorder=10)

    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.1, 1.15); ax.axis('off')
    txcjk(ax, 0.5, 1.12, f'{country_name}健康系统资金池Pareto最优重组Sankey流向图', fs=16, bold=True, color='#0D1B2A', ha='center', va='top')
    txcjk(ax, LEFT_X+NODE_W/2, 1.02, '当前资金配置', fs=12, bold=True, color='#37474F', ha='center', va='bottom')
    txcjk(ax, RIGHT_X+NODE_W/2, 1.02, 'Pareto最优配置', fs=12, bold=True, color='#37474F', ha='center', va='bottom')

    def draw_group_bracket(ax, x, y0, y1, cn, en, color, is_right=False):
        ax.plot([x, x], [y0, y1], color=color, lw=3, solid_capstyle='round', zorder=10)
        direction = 1 if is_right else -1
        cn_x, en_x = x + (0.015 * direction), x + (0.030 * direction)
        rot = 270 if is_right else 90
        txcjk(ax, cn_x, (y0+y1)/2, cn, fs=10, bold=True, color=color, ha='center', va='center', rotation=rot, zorder=10)
        ax.text(en_x, (y0+y1)/2, en, fontsize=8, color=color, ha='center', va='center', rotation=rot, fontfamily='sans-serif', zorder=10)

    bxl, bxr = LEFT_X - 0.16, RIGHT_X + NODE_W + 0.2
    draw_group_bracket(ax, bxl, LN[1][0], LN[0][0]+LN[0][1], '冗余削减区', 'Redundant Reduction', '#1565C0')
    draw_group_bracket(ax, bxl, LN[4][0], LN[3][0]+LN[3][1], '历史欠账区', 'Historical Deficit', '#C62828')
    draw_group_bracket(ax, bxr, RN[1][0], RN[0][0]+RN[0][1], '释放沉淀资金', 'Capital Release', '#1565C0', is_right=True)
    draw_group_bracket(ax, bxr, RN[4][0], RN[3][0]+RN[3][1], '全额靶向滴灌', 'Targeted Injection', '#C62828', is_right=True)

    mid = 0.5
    ax.annotate('', xy=(0.60, mid), xytext=(0.40, mid), arrowprops=dict(arrowstyle='-|>', color='#90A4AE', lw=2))
    txcjk(ax, 0.50, mid+0.02, 'Pareto重组', fs=12, bold=True, color="#27333A", alpha=0.9, ha='center', va='center', zorder=10)

    ly, lx = -0.05, 0.35
    for idx, (col, alp, cn) in enumerate([('#1976D2', 0.55, '由临床与行政释放的重组资金'), ('#B0BEC5', 0.20, '各部门底座自留资金')]):
        xx = lx + idx*0.20
        ax.add_patch(mpatches.FancyBboxPatch((xx, ly), 0.015, 0.015, boxstyle="round,pad=0.001", facecolor=col, alpha=alp+0.2, edgecolor='#90A4AE', linewidth=0.5, zorder=9))
        txcjk(ax, xx+0.025, ly+0.008, cn, fs=9, color='#37474F', ha='left', va='center', zorder=9)

    plt.tight_layout(pad=0.5)
    img_name = f'Sankey_{iso_code}.png'
    plt.savefig(img_name, dpi=400, bbox_inches='tight')
    plt.close()
    
    report = f"==== 【决策引擎寻优输出: {country_name} ({iso_code})】 ====\n"
    report += f"✅ 桑基图已渲染并保存为: {img_name}\n"
    report += "📊 系统本底与重组指令 (Delta):\n"
    for i in range(N_NODES):
        sign = "+" if delta_B[i] > 0 else ""
        report += f"  - {nodes_info[i][0]}: 本底 {lt[i]:.1f}% -> 目标 {rt[i]:.1f}% (变动 {sign}{delta_B[i]:.2f}%)\n"
    return report

if __name__ == "__main__":
    print(run_optimization_and_sankey("CHN"))