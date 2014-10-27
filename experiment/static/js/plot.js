var margin = {top: 20, right: 80, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y%m%d").parse;

var x = d3.scale.linear()
    .range([0, width]);

var xSessions = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(xSessions)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .interpolate("linear")
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); });

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

function lineChart(error, data) {
    names = d3.keys(data[0]).filter(function(key) { return key != 'session' && key != 'x'; });

    var xMax = d3.max(data, function(d) { return +d.x });
    var users = names.map(function(name) {
        return {
            name: name,
            tree_url: "/admin/trees/" + name,
            values: data.filter(function(d) {return d[name] > 0}).map(function(d) {
                return {
                    x: +d.session * xMax + +d.x,
                    y: +d[name],
                    session: +d.session,
                    raw_x: +d.x}
            })
        };
    });

    x.domain([
      0,
      d3.max(users, function(u) { return d3.max(u.values, function(v) { return v.x; }); })
      ]);

    sessionMax = d3.max(users, function(u) { return d3.max(u.values, function(v) { return v.session; })+1; });
    xSessions.domain([
      0,
      sessionMax
    ]);
    xAxis.tickValues(d3.range(sessionMax));

    y.domain([
      0,
      d3.max(users, function(u) { return d3.max(u.values, function(v) { return v.y; }); })
      ]);
            
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
    .append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("session");

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("% correct");

    var user = svg.selectAll(".user")
        .data(users)
      .enter().append("svg:a")
        .attr("xlink:href", function(d) { return d.tree_url; })
        .attr("target", "_blank")
      .append("g")
        .attr("class", "user");

    user.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.values); });


    svg.selectAll(".session")
        .data(users.filter(function(d) {return d.raw_x == xMax;}))
      .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", function(d) { return x(d.x); })
        .attr("cy", function(d) { return y(d.y); })
        .style("fill", function(d) { return color(d.name); });
}




