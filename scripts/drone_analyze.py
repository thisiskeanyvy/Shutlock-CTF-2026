#!/usr/bin/env python3
"""Deep MAVLink analysis for drone.pcap (#79)."""
import math
import os
import re
import statistics
import struct
from collections import Counter
from datetime import datetime

PCAP = os.environ.get("DRONE_PCAP", "drone.pcap")


def parse_packets(path: str):
    raw = open(path, "rb").read()
    off = 24
    gps, heartbeats, raw_udp = [], [], []
    while off + 16 <= len(raw):
        ts_sec, ts_usec = struct.unpack_from("<II", raw, off)
        incl_len = struct.unpack_from("<I", raw, off + 8)[0]
        off += 16
        pkt = raw[off : off + incl_len]
        off += incl_len
        if len(pkt) < 42:
            continue
        if struct.unpack_from(">H", pkt, 12)[0] != 0x0800:
            continue
        ihl = (pkt[14] & 0xF) * 4
        if pkt[23] != 17:
            continue
        udp_off = 14 + ihl
        sport, dport, ulen, _ = struct.unpack("!HHHH", pkt[udp_off : udp_off + 8])
        data = pkt[udp_off + 8 : udp_off + ulen]
        wall = datetime.fromtimestamp(ts_sec + ts_usec / 1e6)
        raw_udp.append((wall, data))
        if not data or data[0] != 0xFE or len(data) < 6:
            continue
        plen, msgid = data[1], data[5]
        payload = data[6 : 6 + plen]
        if msgid == 33 and len(payload) >= 28:
            t_ms, lat, lon, alt, ralt, vx, vy, vz, hdg = struct.unpack_from(
                "<IiiiihhhH", payload, 0
            )
            gps.append(
                {
                    "wall": wall,
                    "t": t_ms,
                    "lat": lat / 1e7,
                    "lon": lon / 1e7,
                    "lat_i": lat,
                    "lon_i": lon,
                    "alt_m": alt / 1000.0,
                    "vx": vx,
                    "vy": vy,
                    "vz": vz,
                    "hdg": None if hdg == 65535 else hdg / 100.0,
                    "seq": data[2],
                    "crc": data[6 + plen : 6 + plen + 2].hex(),
                }
            )
        elif msgid == 0:
            heartbeats.append((wall, payload.hex()))
    return gps, heartbeats, raw_udp


def hav_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(
        lat2 * p
    ) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def fmt_coord(lat, lon, nd=3):
    def one(v, is_lat):
        if is_lat:
            hemi = "N" if v >= 0 else "S"
        else:
            hemi = "E" if v >= 0 else "W"
        return f"{abs(v):.{nd}f}{hemi}"

    return f"{one(lat, True)},{one(lon, False)}"


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    slope = num / den
    return slope, my - slope * mx


def main():
    gps, hb, raw_udp = parse_packets(PCAP)
    print(f"GPS fixes: {len(gps)}  Heartbeats: {len(hb)}  UDP: {len(raw_udp)}")
    if not gps:
        return

    s, e = gps[0], gps[-1]
    wall_d = (e["wall"] - s["wall"]).total_seconds()
    boot_d = e["t"] - s["t"]
    print(f"Wall: {s['wall']} -> {e['wall']} ({wall_d:.1f}s)")
    print(f"Boot ms: {s['t']} -> {e['t']} ({boot_d}) ratio={boot_d/(wall_d*1000):.1f}x")

    path_m = sum(
        hav_m(gps[i - 1]["lat"], gps[i - 1]["lon"], gps[i]["lat"], gps[i]["lon"])
        for i in range(1, len(gps))
    )
    net_m = hav_m(s["lat"], s["lon"], e["lat"], e["lon"])
    print(f"Path length: {path_m:.2f} m  Net displacement: {net_m:.2f} m")

    slon, ilon = linfit([g["t"] for g in gps], [g["lon_i"] for g in gps])
    slat, ilat = linfit([g["t"] for g in gps], [g["lat_i"] for g in gps])
    derived_lon = (slon * e["t"] + ilon) / 1e7
    derived_lat = (slat * e["t"] + ilat) / 1e7
    print(f"Linear derive @end: {derived_lat:.7f}, {derived_lon:.7f}")
    print(f"  formatted: {fmt_coord(derived_lat, derived_lon)}")

    tail = gps[-20:]
    tail_lat = statistics.mean(g["lat"] for g in tail)
    tail_lon = statistics.mean(g["lon"] for g in tail)
    print(f"Tail mean (20): {tail_lat:.7f}, {tail_lon:.7f} -> {fmt_coord(tail_lat, tail_lon)}")

    print(f"Start: {fmt_coord(s['lat'], s['lon'])}")
    print(f"End:   {fmt_coord(e['lat'], e['lon'])}")
    print(f"Time wall: {s['wall'].strftime('%Hh%M')} -> {e['wall'].strftime('%Hh%M')}")

  # heartbeat
    print(f"Heartbeat unique: {set(h[1] for h in hb)}")

    # strings
    blob = b"".join(d for _, d in raw_udp)
    for m in re.finditer(rb"SHLK\{[^}]+\}", blob):
        print("FLAG STRING:", m.group().decode())
    for m in re.finditer(rb"[ -~]{10,}", blob):
        t = m.group().decode("ascii", "replace")
        if any(x in t.lower() for x in ("shlk", "flag", "shutlock", "derive")):
            print("ASCII:", t)

    # candidate flags
    t_end = e["wall"].strftime("%Hh%M")
    t_start = s["wall"].strftime("%Hh%M")
    dur_min = int(wall_d // 60)
    dur_sec = int(wall_d % 60)
    cands = [
        f"SHLK{{{fmt_coord(derived_lat, derived_lon)}_{t_end}}}",
        f"SHLK{{{fmt_coord(e['lat'], e['lon'])}_{t_end}}}",
        f"SHLK{{{fmt_coord(tail_lat, tail_lon)}_{t_end}}}",
        f"SHLK{{{fmt_coord(derived_lat, derived_lon)}}}",
        f"SHLK{{{fmt_coord(e['lat'], e['lon'])}}}",
        f"SHLK{{derive_{int(path_m)}m}}",
        f"SHLK{{derive_{int(net_m)}m}}",
        f"SHLK{{{int(path_m)}m_{t_end}}}",
        f"SHLK{{{fmt_coord(derived_lat, derived_lon)}_{t_start}}}",
        f"SHLK{{{fmt_coord(e['lat'], e['lon'])}_{dur_min:02d}h{dur_sec:02d}}}",
    ]
    print("\nCandidates:")
    for c in cands:
        print(" ", c)


if __name__ == "__main__":
    main()
