import numpy as np
import astropy.units as u
from astropy.coordinates import Galactic, ICRS
from astropy.coordinates import CartesianRepresentation, CartesianDifferential

# 输入：银河笛卡尔速度分量（km/s）
v_gal = np.array([-25.841, -244.657, 275.938]) * (u.km / u.s)

# 构造零位置的笛卡尔表示，并挂上速度微分
rep0 = CartesianRepresentation(1 * u.pc, 1 * u.pc, 1 * u.pc)
v_diff = CartesianDifferential(*v_gal)
rep_with_v = rep0.with_differentials(v_diff)

# 将表示绑定到 Galactic 框架（避免用 SkyCoord 构造的兼容性问题）
gal_frame = Galactic()
gal_with_v = gal_frame.realize_frame(rep_with_v)

# 转换到 ICRS 框架
icrs_with_v = gal_with_v.transform_to(ICRS())

# 读取 ICRS 笛卡尔速度分量（输出为 Quantity）
# 在不同版本的 astropy，速度微分键可能是 's' 或 's' 的别名，下面兼容读取
diffs = icrs_with_v.cartesian.differentials
if "s" in diffs:
    v_icrs = diffs["s"].d_xyz
else:
    # 有些版本把微分放在 .differentials[CartesianDifferential] 的方式下
    try:
        cd = list(diffs.values())[0]
        v_icrs = cd.d_xyz
    except Exception:
        # fallback: 尝试用 .differentials['s'] 访问会在上面分支处理
        raise RuntimeError("无法从 icrs_with_v.cartesian.differentials 读取速度微分；"
                           "请打印 icrs_with_v.cartesian.differentials 查看键名。")

print("v_galactic (km/s):", v_gal)
print("v_icrs (km/s):   ", v_icrs.to(u.km/u.s))