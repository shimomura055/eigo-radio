from __future__ import annotations

import os

import av

OUT_DIR = "er011_output/no18_tight_speech_only_removal_trial_15"

PAIRS = [
    (f"{OUT_DIR}/theme_root/a2/assembled/English_Your_Way_A2_POOL_N18_NOTIFICATIONS_SPECFIX_V2.wav",
     f"{OUT_DIR}/trial_a2_full.webm"),
    ("er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/assembled/"
     "English_Your_Way_A2_POOL_N18_NOTIFICATIONS_SPECFIX_V2.wav",
     f"{OUT_DIR}/prod_a2_full.webm"),
]


def convert(src, dst):
    in_container = av.open(src)
    in_stream = in_container.streams.audio[0]
    out_container = av.open(dst, "w", format="webm")
    out_stream = out_container.add_stream("libopus", rate=48000)
    out_stream.bit_rate = 96000
    for frame in in_container.decode(in_stream):
        for packet in out_stream.encode(frame):
            out_container.mux(packet)
    for packet in out_stream.encode(None):
        out_container.mux(packet)
    out_container.close()
    in_container.close()
    print(dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    for src, dst in PAIRS:
        convert(src, dst)
