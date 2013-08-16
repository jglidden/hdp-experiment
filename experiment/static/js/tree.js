var width = 960,
    height = 520,
    colors = d3.scale.category20(),
    circlesize = 24;


var svg = d3.select('#content')
    .append('svg')
    .attr('width', width)
    .attr('height', height)

var drag_line = svg.append('svg:path')
    .attr('class', 'link dragline hidden')
    .attr('d', 'M0,0L0,0');

var link = svg.append('svg:g').selectAll('path')
    node = svg.append('svg:g').selectAll('g');

// define arrow markers for graph links
svg.append('svg:defs').append('svg:marker')
    .attr('id', 'end-arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 6)
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('orient', 'auto')
  .append('svg:path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#000');


svg.append('svg:defs').append('svg:marker')
    .attr('id', 'start-arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 4)
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('orient', 'auto')
  .append('svg:path')
    .attr('d', 'M10,-5L0,0L10,5')
    .attr('fill', '#000');


var nodes = [
    {id: 1, name: 'hob'},
    {id: 2, name: 'pim'},
    {id: 3, name: 'bot'},
    {id: 4, name: 'som'},
    {id: 5, name: 'vad'},
    {id: 6, name: 'tis'},
    {id: 7, name: 'rel'},
    {id: 8, name: 'mul'},
    {id: 9, name: 'fac'},
    {id: 10, name: 'zim'},
    {id: 11, name: 'com'},
    {id: 12, name: 'lar'}
    ],
    links = [];

nodes.sort(function(a, b) {return 0.5 - Math.random()});
var i;
for (i = 0; i < nodes.length; i += 1) {
    //nodes[i].fixed = true;
    nodes[i].x = ((width - 100) / nodes.length) * i + 100;
    nodes[i].y = height - 100;
}


var drag = d3.behavior.drag()
            .on('drag', dragmove)

//mouse event variables
var selected_node = null,
    mousedown_node = null,
    mouseup_node = null;

function resetMouseVars() {
    selected_node = null;
    mouseup_node = null;
    mousedown_node = null;
}

function restart() {
    link = link.data(links);
    link.enter().append('svg:path');
    link.attr('class', 'link')
        .attr('d', drawpath)
        .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; });

    node = node.data(nodes, function(d) { return d.id; });
    g = node.enter().append('svg:g');
    g.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    })
     .call(drag);
    g.append('svg:circle')
        .attr('class', 'node')
        .attr('r', circlesize)
        .style('fill', function(d) { return colors(d.id); })
        .on('mousedown', function(d) {
            if(!d3.event.shiftKey) return;
            mousedown_node = d;
            if(mousedown_node === selected_node) selected_node = null;
            else selected_node = mousedown_node;
            drag_line
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y)
                .style('marker-end', 'url(#end-arrow)');
            restart();
        })
        .on('mouseup', function(d) {
            if(!mousedown_node) return;
            mouseup_node = d;
            if(mouseup_node === mousedown_node) { resetMouseVars(); return; }
            var source, target;
            if(mousedown_node.id < mouseup_node.id) {
                source = mousedown_node;
                target = mouseup_node;
                direction = 'right';
            } else{
                source = mouseup_node;
                target = mousedown_node;
                direction = 'left';
            }
            var link;
            link = links.filter(function(l) {
                return (l.source === source && l.target === target);
            })[0];
            if(!link){
                link = {source: source, target: target, left: false, right: false};
                link[direction] = true;
                links.push(link);
            }
            selected_node = null;
            restart();
        });

    g.append('svg:text')
        .attr('x', 0)
        .attr('y', 4)
        .attr('class', 'id')
        .text(function(d) { return d.name });

}

function drawpath(d) {
    var deltaX = d.target.x - d.source.x,
        deltaY = d.target.y - d.source.y,
        dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY),
        normX = deltaX / dist,
        normY = deltaY / dist,
        sourcePadding = d.left ? 29 : circlesize,
        targetPadding = d.right ? 29 : circlesize,
        sourceX = d.source.x + (sourcePadding * normX),
        sourceY = d.source.y + (sourcePadding * normY),
        targetX = d.target.x - (targetPadding * normX),
        targetY = d.target.y - (targetPadding * normY);
    return 'M' + sourceX + ',' + sourceY + 'L' + targetX + ',' + targetY;
}


function mousedown() {
    //prevent I-bar on drag
    d3.event.preventDefault();
}

function mouseup() {
    if(mousedown_node) {
        drag_line
            .classed('hidden', true);
    }

    resetMouseVars();
}

function dragmove(d) {
    d3.select(this)
        .attr('transform', function(d) {
            return 'translate(' + d3.event.x + ',' + d3.event.y + ')';
        });
    d.x = d3.event.x;
    d.y = d3.event.y;
    restart();
}

function keydown() {
    if(d3.event.keyCode === 16) {
        drag.on('drag', null);
        svg.classed('shift', true);
    }
}

function keyup() {
    if(d3.event.keyCode === 16) {
        drag.on('drag', dragmove);
        svg.classed('shift', false)
    }
}

function mousemove() {
    if(!mousedown_node) return;
    drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);

    restart();
}

function submitTree() {
    $('#links').val(JSON.stringify(links));
    $('form').submit();
}

svg.on('mouseup', mouseup)
   .on('mousedown', mousedown)
   .on('mousemove', mousemove);
d3.select(window)
  .on('keydown', keydown)
  .on('keyup', keyup);
restart();


