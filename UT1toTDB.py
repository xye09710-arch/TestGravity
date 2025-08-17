from astropy.time import Time

# 假设你知道 UT1 时间字符串和 DUT1 已内置（Astropy 可用 'ut1'）
# 如果你有 UT1 时间：
t_ut1 = Time("2025-08-17T12:00:00", scale='ut1')  # 需确保 astropy 可以解析该 ut1 时间
# 把 UT1 转为 UTC（Astropy 会处理 DUT1/leap second，如果本地安装了 IERS 数据）
t_utc = t_ut1.utc

# 或者若你只有 UT1 并需要先减 DUT1 (手工):
# dut1 = 0.1234  # seconds, 从 IERS 获取
# t_utc = Time(t_ut1.iso) - dut1*u.s

# 由 UTC -> TAI -> TT
t_tt = t_utc.tt

# TT -> TDB
t_tdb = t_tt.tdb

print("TDB:", t_tdb.iso)
print("TDB - TT (s):", (t_tdb - t_tt).to('s'))