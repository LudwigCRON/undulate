'use strict';

var tspan = require('tspan'),
    jsonmlParse = require('./create-element'),
    w3 = require('./w3'),
    findLaneMarkers = require('./find-lane-markers');

function renderWaveLane (root, content, index, lane) {
    var i,
        j,
        k,
        g,
        gg,
        title,
        b,
        labels = [1],
        name,
        xoffset,
        xmax     = 0,
        xgmax    = 0,
        glengths = [];
    for (j = 0; j < content.length; j += 1) {
        name = content[j][0][0];
        if (name) { // check name
            g = jsonmlParse(['g',
                {
                    id: 'wavelane_' + j + '_' + index,
                    transform: 'translate(0,' + ((lane.y0) + j * lane.yo) + ')'
                }
            ]);
            root.insertBefore(g, null);
            title = tspan.parse(name);
            title.unshift(
                'text',
                {
                    x: lane.tgo,
                    y: lane.ym,
                    class: 'info',
                    'text-anchor': 'end',
                    'xml:space': 'preserve'
                }
            );
            title = jsonmlParse(title);
            g.insertBefore(title, null);

            // scale = lane.xs * (lane.hscale) * 2;

            glengths.push(title.getBBox().width);

            xoffset = content[j][0][1];
            xoffset = (xoffset > 0) ? (Math.ceil(2 * xoffset) - 2 * xoffset) :
                (-2 * xoffset);
            gg = jsonmlParse(['g',
                {
                    id: 'wavelane_draw_' + j + '_' + index,
                    transform: 'translate(' + (xoffset * lane.xs) + ', 0)'
                }
            ]);
            g.insertBefore(gg, null);

            if (content[j][1]) {
                for (i = 0; i < content[j][1].length; i += 1) {
                    b = document.getElementById(content[j][1][i]).cloneNode(true);
                    //b = document.createElementNS(w3.svg, 'use');
                    //b.setAttributeNS(w3.xlink, 'xlink:href', '#' + content[j][1][i]);
                    b.setAttribute('transform', 'translate(' + (i * lane.xs) + ')');
                    if(content[j][3].hasOwnProperty('slewing')) {
                        let slew = (content[j][3].slewing == true) ? 16 : content[j][3].slewing;
                        let path  = b.querySelector(".s1");
                        switch (content[j][1][i]) {
                            case 'Nclk': path.setAttribute('d', 'm0,0 '+slew+',20 '+(20-slew)+',0'); break;
                            case 'Pclk': path.setAttribute('d', 'M0,20 '+slew+',0 20,0'); break;
                            case 'nclk': path.setAttribute('d', 'm0,0 '+slew+',20 '+(20-slew)+',0'); break;
                            case 'pclk': path.setAttribute('d', 'M0,20 '+slew+',0 20,0'); break;
                            default: break;
                        }
                        gg.insertBefore(b, null);
                        let arrow = b.querySelector(".s9");
                        if(arrow != null) {
                            let angleDeg = 180/Math.PI*Math.atan2(slew,20);
                            switch (content[j][1][i]) {
                                case 'Nclk': arrow.setAttribute('transform', 'rotate(-'+angleDeg+')'); break;
                                case 'Pclk': arrow.setAttribute('transform', 'translate('+(slew)+', 0) rotate('+angleDeg+')'); break;
                                default: break;
                            }
                        }
                    } else {
                        gg.insertBefore(b, null);
                    }
                    
                }
                if (content[j][2] && content[j][2].length) {
                    labels = findLaneMarkers(content[j][1]);

                    if (labels.length !== 0) {
                        for (k in labels) {
                            if (content[j][2] && (typeof content[j][2][k] !== 'undefined')) {
                                title = tspan.parse(content[j][2][k]);
                                title.unshift(
                                    'text',
                                    {
                                        x: labels[k] * lane.xs + lane.xlabel,
                                        y: lane.ym,
                                        'text-anchor': 'middle',
                                        'xml:space': 'preserve'
                                    }
                                );
                                title = jsonmlParse(title);
                                gg.insertBefore(title, null);
                            }
                        }
                    }
                }
                if (content[j][1].length > xmax) {
                    xmax = content[j][1].length;
                }
            }
        }
    }
    // xmax if no xmax_cfg,xmin_cfg, else set to config
    lane.xmax = Math.min(xmax, lane.xmax_cfg - lane.xmin_cfg);
    lane.xg = xgmax + 20;
    return glengths;
}

module.exports = renderWaveLane;
