SUMMARY = "Message-passing scheduler latency benchmark"
HOMEPAGE = "https://git.kernel.org/pub/scm/linux/kernel/git/mason/schbench.git"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://schbench.c;beginline=1;endline=10;md5=1cd7db0d12dc74fbd8598709bd600f13"

SRC_URI = "git://git.kernel.org/pub/scm/linux/kernel/git/mason/schbench.git;protocol=https;branch=master"
SRCREV = "ab22f3f8766e1bf8a3e8f481c205c8f153dd200d"

do_compile() {
    ${CC} ${CFLAGS} -D_GNU_SOURCE ${LDFLAGS} -o schbench schbench.c -lpthread -lm
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/schbench ${D}${bindir}/
}
