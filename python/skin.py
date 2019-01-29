#!/usr/bin/env python3

DEFAULT = """
text{font-size:11pt;
    font-style:normal;
    font-variant:normal;
    font-weight:normal;
    font-stretch:normal;
    text-align:center;
    fill-opacity:1;
    font-family:Helvetica}
.muted{fill:#aaa}
.warning{fill:#f6b900}
.error{fill:#f60000}
.info{fill:#0041c4}
.success{fill:#00ab00}
.h1{font-size:33pt;font-weight:bold}
.h2{font-size:27pt;font-weight:bold}
.h3{font-size:20pt;font-weight:bold}
.h4{font-size:14pt;font-weight:bold}
.h5{font-size:11pt;font-weight:bold}
.h6{font-size:8pt;font-weight:bold}
.path{fill:none;
    stroke:#000;
    stroke-width:1.5;
    stroke-linecap:round;
    stroke-linejoin:miter;
    stroke-miterlimit:4;
    stroke-opacity:1;
    stroke-dasharray:none}
.stripe{fill:none;
    stroke:#000;
    stroke-width:0.5;
    stroke-linecap:round;
    stroke-linejoin:miter;
    stroke-miterlimit:4;
    stroke-opacity:1;
    stroke-dasharray:none}
.arrow{fill:#000000;fill-opacity:1;stroke:none}
.hide{fill:#ffffff;fill-opacity:1;stroke:2}
"""

PATTERN = """
<defs>
    <pattern id="diagonalHatch" width="5" height="5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="5" style="stroke:black; stroke-width:1" />
    </pattern>
</defs>
"""