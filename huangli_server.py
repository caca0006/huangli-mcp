# Huangli MCP server (compatible with lunar-python 1.4.x)
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

import pytz
from mcp.server.fastmcp import FastMCP
# 只导入 Solar / Lunar，不能导入 LunarHour（1.4.x 没有）
from lunar_python import Solar, Lunar

mcp = FastMCP("Huangli")

def _parse_date(date_str: Optional[str], tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return tz.localize(datetime(dt.year, dt.month, dt.day, 12, 0, 0))
    now_tz = datetime.now(tz)
    return now_tz.replace(hour=12, minute=0, second=0, microsecond=0)

def _fmt_weekday(w: int, lang: str) -> str:
    if lang == "en":
        return ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][w-1]
    return ["一","二","三","四","五","六","日"][w-1]

def _maybe_list(xs) -> List[str]:
    try:
        return [x for x in xs if x]
    except Exception:
        return []

def _safe(getter, default=""):
    try:
        v = getter()
        return v if v is not None else default
    except Exception:
        return default

def _almanac_for(dt: datetime, lang: str = "zh") -> Dict[str, Any]:
    solar = Solar.fromYmd(dt.year, dt.month, dt.day)
    lunar: Lunar = solar.getLunar()

    weekday = solar.getWeek()  # 1..7 Mon=1

    # 部分 API 在旧版不存在，用 _safe 包一层
    jieqi     = _safe(lunar.getJieQi, "")
    moonphase = _safe(lunar.getYueXiang, "")  # 如果旧版没有，会返回 ""

    yi        = _maybe_list(_safe(lunar.getDayYi, []))
    ji        = _maybe_list(_safe(lunar.getDayJi, []))

    chong_animal = _safe(lunar.getChongShengXiao, "")
    chong_desc   = _safe(lunar.getChongDesc, "")
    sha          = _safe(lunar.getSha, "")

    pengzu_gan = _safe(lunar.getPengZuGan, "")
    pengzu_zhi = _safe(lunar.getPengZuZhi, "")

    # 黄道黑道 / 天神
    day_tianshen      = _safe(lunar.getDayTianShen, "")
    huangdao_or_heidao = "黄道日" if _safe(lunar.isDayHuangDao, False) else "黑道日"

    # 吉神/凶煞（旧版可能没有这些方法，_safe 兜底为空列表）
    ji_shen   = _maybe_list(_safe(lunar.getDayJiShen, []))
    xiong_sha = _maybe_list(_safe(lunar.getDayXiongSha, []))

    # 喜神/福神/财神方位（旧版若无，置空）
    pos_xi  = _safe(lunar.getPositionXi, "")
    pos_fu  = _safe(lunar.getPositionFu, "")
    pos_cai = _safe(lunar.getPositionCai, "")

    # 纳音
    nayin_year  = _safe(lunar.getYearNaYin, "")
    nayin_month = _safe(lunar.getMonthNaYin, "")
    nayin_day   = _safe(lunar.getDayNaYin, "")
    # 旧版无时辰纳音与时柱，这里留空
    nayin_time  = ""

    result = {
        "date": {
            "gregorian": {
                "year": solar.getYear(),
                "month": solar.getMonth(),
                "day": solar.getDay(),
                "weekday": f"星期{_fmt_weekday(weekday,'zh')}" if lang!="en" else _fmt_weekday(weekday,'en'),
            },
            "lunar": {
                "year": lunar.getYear(),
                "month": lunar.getMonth(),
                "day": lunar.getDay(),
                "monthName": _safe(lunar.getMonthInChinese, ""),
                "dayName": _safe(lunar.getDayInChinese, ""),
                "zodiac": _safe(lunar.getYearShengXiao, ""),
            },
            "solarTerm": jieqi,
            "moonPhase": moonphase,
            "timezone": str(dt.tzinfo),
        },
        "stemsBranches": {
            "yearGZ":  _safe(lunar.getYearInGanZhi, ""),
            "monthGZ": _safe(lunar.getMonthInGanZhi, ""),
            "dayGZ":   _safe(lunar.getDayInGanZhi, ""),
            "timeGZ":  "",  # 旧版不算时柱
            "nayin": {
                "year":  nayin_year,
                "month": nayin_month,
                "day":   nayin_day,
                "time":  nayin_time
            }
        },
        "almanac": {
            "yi": yi,
            "ji": ji,
            "dayTianShen": day_tianshen,
            "huangDaoOrHeiDao": huangdao_or_heidao,
            "chong": {"animal": chong_animal, "desc": chong_desc},
            "sha": sha,
            "pengzu": {"gan": pengzu_gan, "zhi": pengzu_zhi},
            "godsDirection": {"xi": pos_xi, "fu": pos_fu, "cai": pos_cai},
            "stars": {"jiShen": ji_shen, "xiongSha": xiong_sha}
        }
    }
    return result

@mcp.tool()
def get_huangli(date: Optional[str] = None,
                tz: str = "Asia/Shanghai",
                lang: str = "zh") -> Dict[str, Any]:
    """Get Chinese Huangli for a date (compatible with lunar-python 1.4.x)."""
    tz = tz or "Asia/Shanghai"
    try:
        dt = _parse_date(date, tz)
    except Exception as e:
        raise ValueError(f"Invalid date or timezone. date={date}, tz={tz}, err={e}")
    return _almanac_for(dt, lang=lang)

@mcp.resource("huangli://{date}")
def huangli_resource(date: str) -> str:
    data = get_huangli(date=date, tz="Asia/Shanghai", lang="zh")
    return json.dumps(data, ensure_ascii=False, indent=2)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
