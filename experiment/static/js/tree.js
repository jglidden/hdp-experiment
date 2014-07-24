var margin = {top: 60, right: 60, bottom: 80, left: 60},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
    circlesize = 24;

var svg,
    drag_line,
    link,
    node;

function setUpPage(margin, width, height) {
    svg = d3.select("#content").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    drag_line = svg.append('svg:path')
        .attr('class', 'link dragline hidden')
        .attr('d', 'M0,0L0,0');

    link = svg.append('svg:g').selectAll('path')
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
}

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

function resetNodes() {
    var i;
    for (i = 0; i < nodes.length; i += 1) {
        //nodes[i].fixed = true;
        nodes[i].x = ((width - 100) / nodes.length) * i + 100;
        nodes[i].y = height - 100;
    }
}

var nodes_by_id = {};

function resetLinks(defaultLinks) {
    nodes_by_id = {};
    nodes.forEach(function(n) {nodes_by_id[n.id] = n;})
    var i;
    for (i = 0; i < defaultLinks.length; i += 1) {
        source = nodes_by_id[defaultLinks[i].source]
        target = nodes_by_id[defaultLinks[i].target]
        newLink = {source: source, target: target, right: true, left: false}
        links.push(newLink)
    }
}

function prettyTree(defaultLinks, h, w) {
    // from http://bl.ocks.org/mbostock/2949981
    var nodesByName = {};

    // Create nodes for each unique source and target.
    defaultLinks.forEach(function(l) {
    var parent = l.source = nodeByName(l.source),
        child = l.target = nodeByName(l.target);
    if (parent.children) parent.children.push(child);
    else parent.children = [child];
    });

    var targets = defaultLinks.map(function(l) { return l.target.name; });
    var sources = defaultLinks.map(function(l) { return l.source.name; });
    var roots = nodes.filter(function(n) { return targets.indexOf(n.id) === -1; })
                     .map(function(n) { return n.id; });
    var rootNodes = [];
    defaultLinks.forEach(function(l) {
        if ((roots.indexOf(l.source.name) > -1) 
            && (rootNodes.map(function(r) { return r.source }).indexOf(l.source) === -1)) {
            rootNodes.push(l)
        }
    });

    function nodeByName(name) {
    return nodesByName[name] || (nodesByName[name] = {name: name});
    }

    
    var trees = [];
    var x;
    var y;
    rootNodes.forEach(function(root) {
        var tree = d3.layout.tree()
            .size([w, h]);
        var treeNodes = tree.nodes(root.source);
        var realNodes = [];
        treeNodes.forEach(function(n) {
            realNode = nodes_by_id[n.name]
            realNode.x = n.x 
            realNode.y = n.y
            realNodes.push(realNode)
        });
        x = realNode.x;
        y = realNode.y;
        trees.push(realNodes)
    });

    nodes.forEach(function(newNode) {
        if (!newNode.hasOwnProperty('x')) {
            newNode.x = x;
            newNode.y = y;
            trees.push([newNode]);
        }
    });

    for (i = 0; i < trees.length; i += 1) {
        trees[i].forEach(function(n) {
            n.x = n.x/trees.length + w * i / trees.length
        })
    }
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
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; })
        .on('dblclick', function(d, i) {
            links.splice(i, 1);
            restart();});
    link.exit().remove()

    node = node.data(nodes, function(d) { return d.id; });
    g = node.enter().append('svg:g');
    g.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    })
     .call(drag);
    g.append('svg:circle')
        .attr('class', 'node')
        .attr('r', circlesize)
        .style('fill', function(d) { return "DarkGray"; })
        .on('mousedown', function(d) { onMouseDownNode(d, d3.event.shiftKey); })
        .on('mouseup', function(d) { onMouseUpNode(d); });

    g.append('svg:text')
        .attr('x', 0)
        .attr('y', 4)
        .attr('class', 'id')
        .text(function(d) { return d.name });

}

function onMouseDownNode(d, shiftkey) {
    if(!shiftkey) return;
    mousedown_node = d;
    if(mousedown_node === selected_node) selected_node = null;
    else selected_node = mousedown_node;
    drag_line
        .classed('hidden', false)
        .attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mousedown_node.x + ',' + mousedown_node.y)
        .style('marker-end', 'url(#end-arrow)');
    restart();
}

function onMouseUpNode(d) {
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
    onKeyDown(d3.event.keyCode);
}

function onKeyDown(keycode) {
    if(keycode === 16) {
        drag.on('drag', null);
        svg.classed('shift', true);
    }
}

function keyup() {
    onKeyUp(d3.event.keyCode);
}

function onKeyUp(keycode) {
    if(keycode === 16) {
        drag.on('drag', dragmove);
        svg.classed('shift', false)
    }
}

function mousemove() {
    onMouseMove(d3.mouse(this)[0], d3.mouse(this)[1]);
}

function onMouseMove(mouseX, mouseY) {
    if(!mousedown_node) return;
    drag_line.attr('d', 'M' + mousedown_node.x + ',' + mousedown_node.y + 'L' + mouseX + ',' + mouseY);
    restart();
}

function submitTree() {
    $('#links').val(JSON.stringify(links));
    $('form').submit();
}

function configureMouse() {
    svg.on('mouseup', mouseup)
       .on('mousedown', mousedown)
       .on('mousemove', mousemove);
    d3.select(window)
      .on('keydown', keydown)
      .on('keyup', keyup);
}

function runTree() {
    setUpPage(margin, width, height);
    configureMouse();
    resetNodes();
    restart();
}

function runInstructions(time_elapsed, text, cursor) {
    resetNodes();
    var moveNode = nodes[4];
    var targetNode = nodes[5];
    onMouseDownNode(moveNode, true);
    onMouseUpNode(targetNode);
    link.transition()
        .attr('class', 'link hidden')
        .delay(time_elapsed)
        .duration(0);

    text.transition()
        .text('Click and drag to move concepts')
        .delay(time_elapsed)
        .duration(0);
    cursor.transition()
        .attr('x', 600)
        .attr('y', 200)
        .delay(time_elapsed)
        .duration(0);
    node.transition()
        .attr('transform', function(d) {
            return 'translate(' + d.x + ',' + d.y + ')';
        })
        .duration(0)
        .delay(time_elapsed);


    cursor.transition()
        .attr('x', moveNode.x)
        .attr('y', moveNode.y)
        .duration(1000)
        .delay(time_elapsed+100);

    moveNode.x = moveNode.x + 100;
    moveNode.y = moveNode.y - 300;
    node.transition()
        .attr('transform', function(d) {
            return 'translate(' + d.x + ',' + d.y + ')';
        })
        .duration(2000)
        .delay(time_elapsed+1200);
    cursor.transition()
        .attr('x', moveNode.x)
        .attr('y', moveNode.y)
        .duration(2000)
        .delay(time_elapsed+1200);
    drag_line.transition()
        .attr('class', 'link dragline hidden')
        .attr('d', 'M' + moveNode.x + ',' + moveNode.y + 'L' + moveNode.x + ',' + moveNode.y)
        .style('marker-end', 'url(#end-arrow)')
        .duration(0)
        .delay(time_elapsed+1200);

    text.transition()
        .text('Hold shift to link concepts')
        .duration(0)
        .delay(time_elapsed+3300);
    drag_line.transition()
        .attr('class', 'link dragline')
        .duration(0)
        .delay(time_elapsed+3300)

    cursor.transition()
        .attr('x', targetNode.x)
        .attr('y', targetNode.y)
        .duration(2000)
        .delay(time_elapsed+3400);
    drag_line.transition()
        .attr('class', 'link dragline')
        .attr('d', 'M' + moveNode.x + ',' + moveNode.y + 'L' + targetNode.x + ',' + targetNode.y)
        .style('marker-end', 'url(#end-arrow)')
        .duration(2000)
        .delay(time_elapsed+3400)
    drag_line.transition()
        .attr('class', 'link dragline hidden')
        .duration(0)
        .delay(time_elapsed+5400)

    link.transition()
        .attr('d', drawpath)
        .delay(time_elapsed+5200)
        .duration(0);

    link.transition()
        .attr('class', 'link')
        .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; })
        .delay(time_elapsed+5400)
        .duration(0);

    cursor.transition()
        .attr('x', (moveNode.x + targetNode.x)/2)
        .attr('y', (moveNode.y + targetNode.y)/2)
        .duration(2000)
        .delay(time_elapsed+5600);
    text.transition()
        .text('Double click a link to delete it')
        .delay(time_elapsed+7700)
        .duration(0);
    link.transition()
        .attr('class', 'link hidden')
        .style('marker-start', function(d) { return d.left ? 'url(#start-arrow)' : ''; })
        .style('marker-end', function(d) { return d.right ? 'url(#end-arrow)' : ''; })
        .delay(time_elapsed+8700)
        .duration(0);
}

function instructTree() {
    setUpPage(margin, width, height);
    resetNodes();
    restart();
    var i = 1;
    var time_elapsed = 0;
    var text = svg.append('text')
        .attr('class', 'instructions')
        .attr('x', 600)
        .attr('y', 50)
        .text('Click and drag to move concepts');

    var cursor = svg.append('image')
        .attr('xlink:href', "/static/cursor.png")
        .attr('height', 24)
        .attr('width', 24)
        .attr('x', 600)
        .attr('y', 200);

    runInstructions(time_elapsed, text, cursor);
    while(i<20) {
        time_elapsed = 9700 * i;
        runInstructions(time_elapsed, text, cursor);
        i += 1;
    }
}

function showExample(id, h, w) {
    d3.json("/example_taxonomy/" + String(id), function(error, data) {
      if (error) return;
      setUpPage(margin, w, h);
      nodes = data.nodes;
      defaultLinks = data.links;
      resetLinks(defaultLinks);
      prettyTree(defaultLinks, h, w);
      configureMouse();
      restart();
    });
}

function defaultTreeFromLinks(new_links) {
    nodes.sort(function(a, b) { return a.id - b.id});
    new_links.forEach(function(n) {
        setUpPage(margin, width, height);
        links = [];
        resetLinks(n);
        prettyTree(n, height, width);
        restart();
    });
    configureMouse();
}
