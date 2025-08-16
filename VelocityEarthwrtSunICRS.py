#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算地球相对于太阳在 ICRS/BCRS 下的速度向量（单位 km/s）。
默认 TT 时间：2025-08-17T12:01:09.110

用法：
  python VelocityEarthwrtSunICRS.py "2025-08-17T12:01:09.110" de440

如果不提供参数，将使用默认时间和 ephemeris（de440）。
依赖：astropy, numpy
安装（如果未安装）：
  pip install astropy numpy
"""

from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric_posvel
import astropy.units as u
import numpy as np
import sys


def earth_velocity_wrt_sun_icrs_kms_tt(time_tt_iso: str, ephem: str = "de440"):
    """
    计算地球相对于太阳的速度向量（单位 km/s），输入时间为 TT（Terrestrial Time）ISO 字符串。

    参数：
      time_tt_iso: TT 的 ISO 时间字符串，例如 "2025-08-17T12:01:09.110"
      ephem: JPL 行星历名称，默认 "de440"

    返回：
      vec: numpy 数组，形状 (3,) -> [vx, vy, vz]（单位 km/s）
      speed: 浮点数，速度幅值（km/s）
    """
    # 解析时间（显式指定 format="isot" 能更稳定地解析 ISO 时间，包括小数秒）
    try:
        t = Time(time_tt_iso, format="isot", scale="tt")
    except Exception:
        # 作为后备，尝试自动解析（不指定 format）
        t = Time(time_tt_iso, scale="tt")

    # 设置行星历
    solar_system_ephemeris.set(ephem)

    # 获取地球与太阳相对于太阳系质心的速度矢量（BCRS/ICRS 表示）
    pos_e, v_earth = get_body_barycentric_posvel("earth", t)
    pos_s, v_sun = get_body_barycentric_posvel("sun", t)

    # 地球相对于太阳的速度（带单位的 Quantity 三分量）
    v_rel = v_earth - v_sun
    v_kms = v_rel.xyz.to(u.km / u.s)  # Quantity array with 3 elements

    vec = np.array([v_kms[0].value, v_kms[1].value, v_kms[2].value], dtype=float)
    speed = float(np.linalg.norm(vec))

    return vec, speed


def main():
    # 默认 TT 时间（已改为用户给定的时间）
    default_time = "2025-08-17T12:01:09.110"
    default_ephem = "de440"

    time_tt = sys.argv[1] if len(sys.argv) > 1 else default_time
    ephem = sys.argv[2] if len(sys.argv) > 2 else default_ephem

    try:
        vec, speed = earth_velocity_wrt_sun_icrs_kms_tt(time_tt, ephem=ephem)
    except Exception as e:
        print("Error computing ephemeris:", e)
        sys.exit(1)

    print(f"TT: {time_tt}, ephem: {ephem}")
    print(f"vx, vy, vz (km/s): {vec[0]:.9f}, {vec[1]:.9f}, {vec[2]:.9f}")
    print(f"speed (km/s): {speed:.9f}")


if __name__ == "__main__":
    main()