#!/usr/bin/env python3
"""
计算（简化模型：无章动/无进动/无极移）：
1) Earth Rotation Angle (ERA) from UT1
2) 实验室在赤道面的投影与地固系 x 轴的角度
返回 (ERA + proj_angle) mod 2pi

用法示例：
    python era_plus_proj.py

函数：
    era_from_ut1_iso(ut1_iso) -> ERA in radians [0, 2*pi)
    proj_angle_lonlat(lon_deg, lat_deg) -> angle (radians) of lab projection wrt ECEF x-axis in [0, 2*pi)
    total_angle_mod(ut1_iso, lon_deg, lat_deg) -> (sum_rad, sum_deg)
"""

from datetime import datetime
import math

# ---------- 辅助：解析 ISO 并计算儒略日（JD） ----------
def parse_iso_to_datetime(iso_str):
    """
    解析 ISO 字符串到 datetime（假定其字段为 UT1，不做时区转换）。
    支持 'YYYY-MM-DDTHH:MM:SS', 带小数秒, 或带空格分隔的形式；若带 'Z' 则去掉。
    """
    s = iso_str.strip()
    if s.endswith('Z'):
        s = s[:-1]
    # Try fromisoformat (支持小数秒)
    try:
        dt = datetime.fromisoformat(s)
        return dt
    except Exception:
        # 回退到格式化解析（没有小数秒）
        try:
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
            return dt
        except Exception as e:
            raise ValueError(f"无法解析时间字符串: {iso_str}") from e

def jd_from_datetime(dt):
    """
    计算儒略日 JD（假定 dt 为 UT1）.
    使用 Meeus 算法，包含日内小数部分。
    返回 float JD.
    """
    year = dt.year
    month = dt.month
    day = dt.day
    # day fraction from time
    day_frac = (dt.hour + dt.minute/60.0 + (dt.second + dt.microsecond*1e-6)/3600.0) / 24.0

    if month <= 2:
        year -= 1
        month += 12

    A = year // 100
    B = 2 - A + A // 4
    # For Gregorian calendar dates (after 1582)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5 + day_frac
    return jd

# ---------- 计算 ERA ----------
def era_from_ut1_iso(ut1_iso):
    """
    Compute Earth Rotation Angle (ERA) in radians from UT1 ISO string.
    Using IAU 2000/2006 definition:
      ERA = 2*pi * frac(0.7790572732640 + 0.00273781191135448 * D + fractional_day)
      where D = JD_UT1 - 2451545.0
    返回值：ERA (radians), 范围 [0, 2*pi)
    """
    dt = parse_iso_to_datetime(ut1_iso)
    jd = jd_from_datetime(dt)
    D = jd - 2451545.0
    # fractional day (UT1 day fraction)
    frac_day = (jd + 0.5 - math.floor(jd + 0.5))  # 另一种方式；更直接使用 day fraction:
    # 上面可改为用时间直接算 day fraction:
    # Compute day fraction explicitly to avoid ambiguity:
    day_fraction = (dt.hour + dt.minute/60.0 + (dt.second + dt.microsecond*1e-6)/3600.0) / 24.0

    # ERA fractional revolutions
    f = 0.7790572732640 + 0.00273781191135448 * D + day_fraction
    # take fractional part
    f_frac = f - math.floor(f)
    era = 2.0 * math.pi * f_frac
    # normalize
    era = era % (2.0 * math.pi)
    return era

# ---------- 实验室投影角度 ----------
def proj_angle_lonlat(lon_deg, lat_deg):
    """
    计算实验室位置在赤道面的投影与地固坐标系 x 轴之间的角度。
    输入：
      lon_deg: 经度，东经为正
      lat_deg: 纬度，北纬为正（纬度只用于计算 z，投影不依赖纬度值的符号）
    输出：
      angle in radians in [0, 2*pi).
    说明：
      ECEF 单位向量（球面近似）： x = cosφ cosλ, y = cosφ sinλ, z = sinφ
      投影到赤道面后向量 (x, y, 0); 对 x 轴的极角为 atan2(y, x).
      atan2 返回 (-pi, pi], 转为 [0, 2pi).
    """
    lon = math.radians(lon_deg)
    lat = math.radians(lat_deg)
    coslat = math.cos(lat)
    x = coslat * math.cos(lon)
    y = coslat * math.sin(lon)
    # proj angle relative to ECEF x axis:
    ang = math.atan2(y, x)  # range (-pi, pi]
    if ang < 0.0:
        ang += 2.0 * math.pi
    return ang

# ---------- 主合成函数 ----------
def total_angle_mod(ut1_iso, lon_deg, lat_deg):
    """
    计算 (ERA + proj_angle) mod 2pi:
    返回 (sum_rad, sum_deg), 其中 sum_rad in [0,2pi).
    """
    era = era_from_ut1_iso(ut1_iso)
    proj = proj_angle_lonlat(lon_deg, lat_deg)
    s = era + proj
    s_mod = s % (2.0 * math.pi)
    return s_mod, math.degrees(s_mod), era, proj

# ---------- 测试 / 示例 ----------
if __name__ == "__main__":
    # 示例输入
    ut1 = "2025-8-17T12:00:00"  # UT1 时间字符串（示例）
    lon = 39.906217  # 东经39.906217度
    lat = 116.3912757   # 北纬116.3912757度

    total_rad, total_deg, era_rad, proj_rad = total_angle_mod(ut1, lon, lat)
    print(f"UT1 = {ut1}")
    print(f"Longitude = {lon} deg, Latitude = {lat} deg")
    print(f"ERA (rad) = {era_rad:.12f}, (deg) = {math.degrees(era_rad):.9f}")
    print(f"Proj angle (rad) = {proj_rad:.12f}, (deg) = {math.degrees(proj_rad):.9f}")
    print(f"Sum mod 2pi (rad) = {total_rad:.12f}, (deg) = {total_deg:.9f}")