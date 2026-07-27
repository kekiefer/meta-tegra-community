SUMMARY = "X Render extension exerciser"
HOMEPAGE = "https://gitlab.freedesktop.org/xorg/test/rendercheck"
LICENSE = "GPL-2.0-or-later AND MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=ff84617f9d8cecf388d25880f32448b0"

SRC_URI = "git://gitlab.freedesktop.org/xorg/test/rendercheck.git;protocol=https;branch=master \
           file://run_rendercheck.py \
           "
SRCREV = "a750b29b12e16528607811f4573f125a5f81fd2f"
UPSTREAM_CHECK_GITTAGREGEX = "rendercheck-(?P<pver>\d+\.\d+)"

inherit meson pkgconfig features_check

REQUIRED_DISTRO_FEATURES = "x11 opengl"

DEPENDS = "virtual/libx11 libxrender libxext"

do_install:append() {
    install -m 0755 ${UNPACKDIR}/run_rendercheck.py ${D}${bindir}/run-rendercheck
}

RDEPENDS:${PN} += "python3-core"
