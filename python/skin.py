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
.s3 > polygon {fill:#ffffb4;fill-opacity:1,stroke:none}
.s4 > polygon {fill:#ffe0b9;fill-opacity:1,stroke:none}
.s5 > polygon {fill:#b9e0ff;fill-opacity:1,stroke:none}
.ticks {stroke: rgb(136, 136, 136); stroke-width: 0.5; stroke-dasharray: 1,3;}
.edges {fill:none;stroke:#00F;stroke-width:1}
.edges.arrowhead {marker-start:url(#arrow); overflow:visible;}
.edges.arrowtail {marker-end:url(#arrow); overflow:visible;}
"""

PATTERN = """
<defs>
    <pattern id="diagonalHatch" width="5" height="5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="5" style="stroke:black; stroke-width:1" />
    </pattern>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
        markerWidth="8" markerHeight="8"
        orient="auto-start-reverse" style="fill:#00F;">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>
</defs>
"""