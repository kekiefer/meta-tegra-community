SUMMARY = "STREAM sustainable memory bandwidth benchmark"
HOMEPAGE = "https://www.cs.virginia.edu/stream/"
LICENSE = "LicenseRef-stream"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=bca8cbe07976fe64c8946378d08314b0"

PV = "5.10+git"

SRC_URI = "git://github.com/jeffhammond/STREAM.git;protocol=https;branch=master"
SRCREV = "6703f7504a38a8da96b353cadafa64d3c2d7a2d3"

# Upstream repo does not tag
UPSTREAM_CHECK_COMMITS = "1"

CFLAGS += "-O3 -fopenmp -DSTREAM_ARRAY_SIZE=10000000 -DNTIMES=20"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o stream-64bit stream.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/stream-64bit ${D}${bindir}/
}
