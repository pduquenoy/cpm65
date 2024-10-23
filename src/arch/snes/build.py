from build.ab import simplerule
from tools.build import mkcpmfs
from build.llvm import llvmrawprogram
from third_party.projectl.build import l_as65c, l_link, l_hex2bin
from config import (
    MINIMAL_APPS,
    MINIMAL_APPS_SRCS,
    BIG_APPS,
    BIG_APPS_SRCS,
    SCREEN_APPS,
)

mkcpmfs(
    name="diskimage",
    format="generic-1440k",
    size=1440 * 1024,
    items={
        "0:ccp.sys@sr": "src+ccp",
        "0:bdos.sys@sr": "src/bdos",
        "0:cls.com": "apps+cls",
    }
    | MINIMAL_APPS
    | MINIMAL_APPS_SRCS,
)

l_as65c(
    name="main",
    srcs=["./main.asm"],
)

llvmrawprogram(
    name="bios",
    srcs=["./bios.S"],
    deps=["include", "src/lib+bioslib"],
    linkscript="./bios.ld",
)

l_link(
    name="main_hex",
    srcs=[".+main"],
    relinfo={"PROG": 0, "DATA": 0, "BANK0": 0x008000},
)

l_hex2bin(
    name="main_bin",
    src=".+main_hex",
    romformat="4",
)

simplerule(
    name="snes_cartridge",
    ins=[".+main_bin", ".+diskimage", "./checksum.py"],
    outs=["snes.img"],
    commands=[
        "cp {ins[0]} {outs[0]}",
        "dd if={ins[1]} of={outs[0]} bs=65536 seek=1 status=none",
        "truncate -s %d {outs[0]}" % (2048*1024),
        "chronic python3 {ins[2]} HIROM {outs[0]}"
    ],
    label="MKCARTRIDGE",
)
