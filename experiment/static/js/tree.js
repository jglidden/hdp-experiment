var width = 960,
    height = 520,
    colors = d3.scale.category20();


var svg = d3.select('#content')
    .append('svg')
    .attr('width', width)
    .attr('height', height)

var drag_line = svg.append('svg:path')
    .attr('class', 'link dragline hidden')
    .attr('d', 'M0,0L0,0');

var link = svg.append('svg:g').selectAll('path')
    node = svg.append('svg:g').selectAll('g');


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
        .attr('d', function(d) {
            return 'M' + d.source.x + ',' + d.source.y + 'L' + d.target.x + ',' + d.target.y;
        });

    node = node.data(nodes, function(d) { return d.id; });
    g = node.enter().append('svg:g');
    g.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    })
     .call(drag);
    g.append('svg:circle')
        .attr('class', 'node')
        .attr('r', 24)
        .style('fill', function(d) { return colors(d.id); })
        .on('mousedown', function(d) {
            if(!d3.event.shiftKey) return;
            mousedown_node = d;
            if(mousedown_node === selected_node) selected_node = null;
            else selected_node = mousedown_node;
            drag_line
                .classed('hidden', false)
                .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y);
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
            } else{
                source = mouseup_node;
                target = mousedown_node;
            }
            var link;
            link = links.filter(function(l) {
                return (l.source === source && l.target === target);
            })[0];
            if(!link){
                link = {source: source, target: target};
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

function tick() {
    node.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    });
    
    link.attr('d', function(d) {
        return 'M' + d.source.x + ',' + d.source.y + 'L' + d.target.x + ',' + d.target.y;
    });

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


