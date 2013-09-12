var width = 960,
    height = 520,
    colors = d3.scale.category20(),
    circlesize = 24;


var svg = d3.select('#content')
    .append('svg')
    .attr('width', width)
    .attr('height', height)

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

node = node.data(nodes, function(d) { return d.id; });
g = node.enter().append('svg:g');
g.attr('transform', function(d) {
    return 'translate(' + d.x + ',' + d.y + ')';
});

g.append('svg:circle')
    .attr('class', 'node')
    .attr('r', circlesize)
    .style('fill', function(d) { return colors(d.id); })
   
