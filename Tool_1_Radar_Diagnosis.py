import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import platform, os
from matplotlib import font_manager

def setup_cjk_fonts():
    system = platform.system()
    if system == 'Windows':
        candidates = ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simhei.ttf']
    elif system == 'Darwin':
        candidates = ['/System/Library/Fonts/PingFang.ttc']
    else:
        candidates = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
    font_p = next((font_manager.FontProperties(fname=fp) for fp in candidates if os.path.exists(fp)), None)
    return font_p

CJK_FONT = setup_cjk_fonts()

def generate_radar_diagnosis(iso_code, db_path='GH_Copilot_Knowledge_Base_Final.csv'):
    df = pd.read_csv(db_path)
    if iso_code not in df['ISO_Code'].values:
        return f"Error: 找不到国家 {iso_code} 的数据"
    
    country_data = df[df['ISO_Code'] == iso_code].iloc[-1]
    country_name = country_data['Country_Name']
    
    labels = np.array(['健康预期寿命\n(HALE)', '系统转化效率\n(DEA)', '人均医疗投入\n(Fund)', 
                       '医师覆盖率\n(Physician)', 'PM2.5负担控制\n(Environment)', '烟草负担控制\n(Tobacco)'])
    
    stats = np.array([
        country_data['HALE_Percentile'], country_data['DEA_Efficiency_Percentile'],
        country_data['Fund_Input_Percentile'], country_data['Physician_Coverage_Percentile'],
        country_data['PM25_Burden_Control_Percentile'], country_data['Tobacco_Burden_Control_Percentile']
    ])
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    stats_closed = np.concatenate((stats, [stats[0]]))
    angles_closed = np.concatenate((angles, [angles[0]]))
    
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles_closed, stats_closed, 'o-', linewidth=2.5, color='#1976D2')
    ax.fill(angles_closed, stats_closed, color='#1976D2', alpha=0.25)
    
    ax.set_thetagrids(angles * 180/np.pi, labels, fontproperties=CJK_FONT if CJK_FONT else None, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.grid(True, linestyle='--', alpha=0.6)
    
    title_font = {'fontproperties': CJK_FONT, 'fontsize': 15, 'fontweight': 'bold'} if CJK_FONT else {'fontsize': 15, 'fontweight': 'bold'}
    plt.title(f"{country_name} 健康系统“投入-风险-产出”基准画像", pad=20, **title_font)
    
    img_name = f'Radar_{iso_code}.png'
    plt.savefig(img_name, dpi=300, bbox_inches='tight')
    plt.close()
    
    report = f"==== 【诊断报告: {country_name} ({iso_code})】 ====\n"
    report += f"雷达图已保存为: {img_name}\n"
    report += "多维基准画像排位 (百分位):\n"
    for i in range(len(labels)):
        report += f"  - {labels[i].replace(chr(10), ' ')}: 击败全球 {stats[i]:.1f}% 的国家\n"
    return report

if __name__ == "__main__":
    print(generate_radar_diagnosis("CHN"))