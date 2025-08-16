from astropy.time import Time
from astropy.utils import iers
import warnings

# 兼容性处理：忽略已知的 IERS 相关警告（若存在）
for warn_name in ('IERSRangeWarning', 'IERSStaleWarning', 'IERSWarning'):
    warn_cls = getattr(iers, warn_name, None)
    if warn_cls is not None:
        warnings.filterwarnings('ignore', category=warn_cls)

def ut1_to_tt_astropy(ut1_iso):
    """
    Convert UT1 (ISO string) -> TT using Astropy.
    Input:
      ut1_iso: ISO string like '2025-08-16T12:00:00' (interpreted as scale='ut1')
    Returns:
      astropy.time.Time object in TT scale
    """
    t_ut1 = Time(ut1_iso, scale='ut1')
    t_tt = t_ut1.tt
    return t_tt

if __name__ == "__main__":
    ut1_time_str = '2025-08-17T12:00:00'
    t_tt = ut1_to_tt_astropy(ut1_time_str)
    print("Input (UT1) : ", ut1_time_str)
    print("Output (TT)  : ", t_tt.iso)
    print("JD (TT)     : ", t_tt.jd)