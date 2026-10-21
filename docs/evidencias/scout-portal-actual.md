<h2>:mag: Vulnerabilities of <code>uts-cwpp-portal:latest</code></h2>

<details open="true"><summary>:package: Image Reference</strong> <code>uts-cwpp-portal:latest</code></summary>
<table>
<tr><td>digest</td><td><code>sha256:42c1ff3a7ba8d3c48d3dccf44cab38b8323094ba2aaa8c6ebdb17e667438d5c8</code></td><tr><tr><td>vulnerabilities</td><td><img alt="critical: 0" src="https://img.shields.io/badge/critical-0-lightgrey"/> <img alt="high: 1" src="https://img.shields.io/badge/high-1-e25d68"/> <img alt="medium: 0" src="https://img.shields.io/badge/medium-0-lightgrey"/> <img alt="low: 0" src="https://img.shields.io/badge/low-0-lightgrey"/> <!-- unspecified: 0 --></td></tr>
<tr><td>platform</td><td>linux/amd64</td></tr>
<tr><td>size</td><td>52 MB</td></tr>
<tr><td>packages</td><td>145</td></tr>
</table>
</details></table>
</details>

<table>
<tr><td valign="top">
<details><summary><img alt="critical: 0" src="https://img.shields.io/badge/C-0-lightgrey"/> <img alt="high: 1" src="https://img.shields.io/badge/H-1-e25d68"/> <img alt="medium: 0" src="https://img.shields.io/badge/M-0-lightgrey"/> <img alt="low: 0" src="https://img.shields.io/badge/L-0-lightgrey"/> <!-- unspecified: 0 --><strong>zlib</strong> <code>1:1.3.dfsg+really1.3.1-1</code> (deb)</summary>

<small><code>pkg:deb/debian/zlib@1%3A1.3.dfsg%2Breally1.3.1-1?os_distro=trixie&os_name=debian&os_version=13</code></small><br/>
<a href="https://scout.docker.com/v/CVE-2026-85091?s=debian&n=zlib&ns=debian&t=deb&osn=debian&osv=13&vr=%3E0"><img alt="high : CVE--2026--85091" src="https://img.shields.io/badge/CVE--2026--85091-lightgrey?label=high%20&labelColor=e25d68"/></a>

<table>
<tr><td>Affected range</td><td><code>>0</code></td></tr>
<tr><td>Fixed version</td><td><strong>Not Fixed</strong></td></tr>
<tr><td>EPSS Score</td><td><code>0.356%</code></td></tr>
<tr><td>EPSS Percentile</td><td><code>28th percentile</code></td></tr>
</table>

<details><summary>Description</summary>
<blockquote>

zlib versions 1.3.1.2 through 1.3.2 contain a heap buffer overflow vulnerability in the gz_vacate() function when processing non-blocking gzwrite() operations with stale external buffer pointers. Attackers can trigger the overflow by calling gzprintf() or gzvprintf() after a write stall, causing an unchecked memmove() to write beyond the internal input buffer boundary.

---
- zlib <unfixed> (bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1146895)
https://gist.github.com/thesmartshadow/e0b9481792afb7c31e86fee1ff084490
https://github.com/madler/zlib/issues/1310
https://github.com/madler/zlib/pull/1317
Fixed by: https://github.com/madler/zlib/commit/df84af25dc1942490e1d1c899a07619152a46148
Discussion on affected range: https://github.com/madler/zlib/issues/1310#issuecomment-5979623265
Support non-blocking devices in the gz* routines introduced with:
https://github.com/madler/zlib/commit/81cc0bebedd935daeb81b0b6e475d8786b51af3d (v1.3.1.2)

</blockquote>
</details>
</details></td></tr>
</table>
