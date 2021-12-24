function int_date(str_date) {
  [y,m,d] = str_date.split('-');
  return parseInt(y)*10000 + parseInt(m)*100 + parseInt(d);
}

var region_code_id_prefix = "rc";
var point_code_id_prefix = "pc";
var connection_from_prefix = "fr";
var connection_to_prefix = "to";

var map_json = "/static/korea_map_readable.json";
var transmission_json = "/static/transmission.json";
var sf = 100;
var t_lati =  32.0, b_lati =  39.5;
var l_long = 124.8, r_long = 131.0;

// svg drawing
var width  = sf*(r_long-l_long);
var height = sf*(b_lati-t_lati);

var scale = 360*sf/(r_long - l_long);

var projection = d3.geoMercator()
  .center([(r_long+l_long)/2, (b_lati+t_lati)/2])
  .scale(scale)
  .translate([width/2,height/2]);

// function 
var path = d3.geoPath()
  .projection(projection);

// HTML element
d3.select("#input_date_s")
  .on("change", function() {
    date_s = int_date(d3.select(this).node().value);
    update_transmission();
  });

// HTML element
d3.select("#input_date_e")
  .on("change", function() {
    date_e = int_date(d3.select(this).node().value);
    update_transmission();
  });

d3.select("#main_viz")
  .attr("width", width)
  .attr("height", height);

function animateViewBox() {
  let moveTo = this.getAttribute("data-view");
  gsap.to(demo, {
    duration: 1,
    attr: { viewBox: moveTo },
    ease: "power3.inOut"
  });
}

var svg = d3.select("#main_viz").append("svg")
  .attr("width", width)
  .attr("height", height)
  .attr("viewBox", "0 0 " + width + " " + height)
  .attr("id", "map_svg")
  .on("contextmenu", function() {
    d3.event.preventDefault();
    var [x, y] = d3.mouse(this);
    svg.transition().duration(100).attr("viewBox", (x-width/4) + " " + (y-height/4) + " " + width/2 + " " + height/2);
  })
  .on("dblclick", function() {
    svg.transition().duration(100).attr("viewBox", 0 + " " + 0 + " " + width + " " + height);
  });
d3.select("header").append("div")
  .attr("id", "tooltip")
  .text("")
  .classed("hidden", true);

// date filter
var date_s = int_date(d3.select("#input_date_s").node().value);
var date_e = int_date(d3.select("#input_date_e").node().value);

function update_transmission() {
  d3.json(transmission_json, parse_transmission);
}

function show_map() {
  d3.json(map_json, draw_map);
}

function arc_link(x1,y1,x2,y2) {
  var cx = (x1+x2)/2;
  var cy = (y1+y2)/2;
  var dx = (x2-x1)/2;
  var dy = (y2-y1)/2;
  var i;

  dd = Math.sqrt(dx*dx+dy*dy);
  ex = cx + dy/dd * dx;
  ey = cy - dx/dd * dy;
  return "M"+x1+" "+y1+"Q"+ex+" "+ey+" "+x2+" "+y2;
}

function get_region_center_offset(region_code) {
  var region_path = d3.select("#" + region_code_id_prefix + region_code);
  var class_list = region_path.attr("class").split(" ");
  var dx, dy;
  for (var i in class_list) {
    var c = class_list[i];
    if (c.startsWith("offset")) {
      dx = c.split("_")[1];
      dy = c.split("_")[2];
    }
  }
  return [parseFloat(dx), parseFloat(dy)];
}

function reset_selection() {
  d3.selectAll(".selected").classed("selected", false);
  d3.selectAll(".selected_to").classed("selected_to", false);
  d3.selectAll(".selected_from").classed("selected_from", false);
  d3.selectAll(".child").classed("child", false);
  d3.selectAll(".parent").classed("parent", false);
}

function parse_transmission(error, raw_patients) {
  var region_patient_count = {};
  var region_connection = [];

  var patients = {};

  for (var pid in raw_patients) {
    if ((raw_patients[pid].date >= date_s) && (raw_patients[pid].date <= date_e)) {
      patients[pid] = raw_patients[pid];
    }
  }

  for (var pid in patients) {
    var patient = patients[pid];
    var region_code = patient.code;
    if (region_patient_count.hasOwnProperty(region_code)) {
      region_patient_count[region_code] += 1;
    } else {
      region_patient_count[region_code] = 1;
    }
    for (var i in patient.branch) {
      var iid = patient.branch[i];
      if (patients.hasOwnProperty(iid)) {
        if (patients[pid].code != patients[iid].code) {
          region_connection.push(patients[pid].code + "." + patients[iid].code);
        }
      }
    }
  }
  //unique only
  region_connection = region_connection.filter((v, i, a) => a.indexOf(v) === i);

  //new thing; needs to turn off selection here
  reset_selection()
  //new thing; needs to turn off selection here

  svg.selectAll(".point").remove();
  var svg_point = svg.selectAll(".point").data(d3.entries(region_patient_count));
  svg_point.enter()
    .append("circle")
    // .merge(svg_point) //might not needed
    .attr("class", "point")
    .attr("id", function(data, i) {
      return point_code_id_prefix + data.key;
    })
    .attr("cx", function(data, i) {
      var region_path = d3.select("#" + region_code_id_prefix + data.key);
      var [dx, dy] = get_region_center_offset(data.key);
      var region_loc = region_path.node().getBBox();
      return region_loc.x + region_loc.width/2 + dx*scale
    })
    .attr("cy", function(data, i) {
      var region_path = d3.select("#" + region_code_id_prefix + data.key);
      var [dx, dy] = get_region_center_offset(data.key);
      var region_loc = region_path.node().getBBox();
      return region_loc.y + region_loc.height/2 + dy*scale
    })
    .attr("r", function(data, i) {
      return 1+Math.log(data.value) / Math.log(20);
    });
  // svg_point.exit().remove();

  svg.selectAll(".connection").remove();
  var svg_connection = svg.selectAll(".connection").data(region_connection);
  svg_connection.enter()
    .append("path")
    // .merge(svg_connection) //might not needed
    .attr("class", function(data, i) {
      var sd = data.split(".");
      return "connection " + connection_from_prefix + sd[0] + " " + connection_to_prefix + sd[1];
    })
    .attr("d", function(data, i) {
      var sd = data.split(".");
      var [sdx, sdy] = get_region_center_offset(sd[0]);
      var [ddx, ddy] = get_region_center_offset(sd[1]);
      var s = d3.select("#" + region_code_id_prefix + sd[0]).node().getBBox();
      var d = d3.select("#" + region_code_id_prefix + sd[1]).node().getBBox();
      return arc_link(s.x + s.width/2 + sdx*scale, s.y + s.height/2 + sdy*scale, d.x + d.width/2 + ddx*scale, d.y + d.height/2 + ddy*scale);
    });
  // svg_connection.exit().remove();
}

function draw_map(error, regions) {
  if (error) console.log(error);
  var svg_city_path = svg.selectAll(".city_path").data(regions.features);
  svg_city_path.enter()
    .append("path")
    .merge(svg_city_path)
    .attr("class", function(d) {
      return "city_path offset_" + d.properties.offset[0] + "_" + d.properties.offset[1];
    })
    .attr("d", path)
    .attr("id", function(d) {
      return region_code_id_prefix + d.properties.code;
    })
    .on("mouseover", function(d) {
      d3.select(this).classed("active", true);
      d3.select("#tooltip").classed("hidden", false).text(d.properties.name_eng);
    })
    .on("mouseout", function(d) {
      d3.select(this).classed("active", false);
      d3.select("#tooltip").classed("hidden", true);
    })
    .on("click", function(d) {
      var x = d3.select(this).classed("selected")
      d3.selectAll(".connection").classed("hidden", true); //hide all first; check if it is selection turning off, show them back
      if (!x) { //maybe other is on, need to turn it off first
        reset_selection()
      } else { //turning off selection obviously
        d3.selectAll(".connection").classed("hidden", false); //show them back as promised
      }
      d3.select(this).classed("selected", !x);
      d3.selectAll("."+connection_to_prefix+d.properties.code).classed("hidden", false).classed("parent", !x);
      d3.selectAll("."+connection_to_prefix+d.properties.code)
        .each(function() {
          var class_list = d3.select(this).attr("class").split(" ");
          for (var i in class_list) {
            var c = class_list[i];
            if (c.startsWith(connection_from_prefix)) {
              d3.selectAll("#"+region_code_id_prefix+c.substr(2)).classed("selected_from", !x);
            }
          }
        });
      d3.selectAll("."+connection_from_prefix+d.properties.code).classed("hidden", false).classed("child", !x);
      d3.selectAll("."+connection_from_prefix+d.properties.code)
        .each(function() {
          var class_list = d3.select(this).attr("class").split(" ");
          for (var i in class_list) {
            var c = class_list[i];
            if (c.startsWith(connection_to_prefix)) {
              d3.selectAll("#"+region_code_id_prefix+c.substr(2)).classed("selected_to", !x);
            }
          }
        });
    })
  svg_city_path.exit().remove();
  update_transmission();
}

show_map();
(function() {
  document.onmousemove = handleMouseMove;
  function handleMouseMove(event) {
    var eventDoc, doc, body;

    event = event || window.event;

    if (event.pageX == null && event.clientX != null) {
      eventDoc = (event.target && event.target.ownerDocument) || document;
      doc = eventDoc.documentElement;
      body = eventDoc.body;

      event.pageX = event.clientX +
        (doc && doc.scrollLeft || body && body.scrollLeft || 0) -
        (doc && doc.clientLeft || body && body.clientLeft || 0);
      event.pageY = event.clientY +
        (doc && doc.scrollTop  || body && body.scrollTop  || 0) -
        (doc && doc.clientTop  || body && body.clientTop  || 0 );
    }
    d3.select("#tooltip")
      .style("left", event.pageX + 10 + "px")
      .style("top", event.pageY + 20 + "px");
  }
})();
