#!/usr/bin/env python3
# 指定脚本解释器：在类 Unix 系统上使用环境中的 python3 运行此脚本

from astropy.time import Time                      # 导入 Time，用于高精度天文时间处理（支持 TT/UTC/TDB 等）
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric_posvel
# 导入 solar_system_ephemeris（设置/选择行星历）和 get_body_barycentric_posvel（获取相对于太阳系质心的位矢与速度）

import astropy.units as u                           # 导入 astropy 的单位模块，通常简称 u，用于带单位的物理量
import numpy as np                                 # 导入 NumPy（数值数组与线性代数）
import sys                                         # 导入 sys，用于访问命令行参数等解释器信息

def earth_velocity_wrt_sun_icrs_kms_tt(time_tt_iso: str, ephem: str = "de440"):
    """
    计算地球相对于太阳在 ICRS（/BCRS 方向）下的速度向量（单位 km/s），
    输入时间为 TT（Terrestrial Time）的 ISO 字符串。
    参数：
      time_tt_iso: TT 的 ISO 时间字符串，例如 "2025-08-09T00:00:00"
      ephem: JPL 行星历名称，默认 "de440"
    返回：
      vec: numpy 数组，形状 (3,) -> [vx, vy, vz]（单位 km/s）
      speed: 浮点数，速度幅值（km/s）
    """
    t = Time(time_tt_iso, scale="tt")               # 将输入字符串解析为 astropy.time.Time 对象，显式指定为 TT（地球时）
    solar_system_ephemeris.set(ephem)               # 设置全局行星历为指定的 ephem（例如 "de430" 或 "de440"）
    _, v_earth = get_body_barycentric_posvel("earth", t)
    # 获取地球相对于太阳系质心（barycenter）的位矢与速度，返回 (pos, vel)
    # 这里只保留速度 v_earth，位置用下划线 _ 丢弃

    _, v_sun = get_body_barycentric_posvel("sun", t)
    # 获取太阳相对于太阳系质心的位矢与速度，保留速度 v_sun
    # 注意：在 JPL 模型中太阳并非严格位于质心（行星影响产生微小偏移），因此需要减去太阳的速度

    v_rel = v_earth - v_sun                          # 计算地球相对于太阳的速度矢量（带单位的 astropy 对象）
    v_kms = v_rel.xyz.to(u.km / u.s)                # 将速度的 xyz 分量转换为 km/s 单位（返回 Quantity 数组）

    vec = np.array([v_kms[0].value, v_kms[1].value, v_kms[2].value], dtype=float)
    # 提取三个分量的纯数值（去除单位），生成 NumPy 浮点数组，便于后续数值处理或保存
    speed = float(np.linalg.norm(vec))              # 计算速度向量的欧几里得范数（速度大小），并转换为 Python float

    return vec, speed                               # 返回速度向量（三分量 km/s）和速度大小（km/s）

if __name__ == "__main__":
    # 当脚本作为主程序运行时执行以下代码（而非被 import 到其他模块）
    # 用法示例：python script.py "YYYY-MM-DDThh:mm:ss" de440

    time_tt = sys.argv[1] if len(sys.argv) > 1 else "2025-08-09T00:00:00"
    # 从命令行读取第一个参数作为 time_tt（TT 的 ISO 字符串）
    # 如果未提供则使用默认时间 "2025-08-09T00:00:00"

    ephem = sys.argv[2] if len(sys.argv) > 2 else "de440"
    # 从命令行读取第二个参数作为行星历名称（ephem），默认 "de440"

    vec, speed = earth_velocity_wrt_sun_icrs_kms_tt(time_tt, ephem=ephem)
    # 调用函数计算速度向量与速度大小

    print(f"TT: {time_tt}, ephem: {ephem}")          # 打印所用的时间与行星历，便于核对
    print(f"vx, vy, vz (km/s): {vec[0]:.9f}, {vec[1]:.9f}, {vec[2]:.9f}")
    # 以小数点后 9 位格式化打印三分量（单位：km/s）

    print(f"speed (km/s): {speed:.9f}")              # 以小数点后 9 位打印速度大小（单位：km/s）