function int_date(str_date) {
  [y,m,d] = str_date.split('-')
  return parseInt(y)*10000 + parseInt(m)*100 + parseInt(d)
}

var region_code_id_prefix = "rc"
var point_code_id_prefix = "pc"
var connection_from_prefix = "fr"
var connection_to_prefix = "to"

// main map
// var map_json = "/static/sel_regions.json";
// var transmission_json = "/static/transmission_simple.json";

var map_json = "/static/korea_map_readable.json";
var transmission_json = "/static/transmission.json";
var sf = 150;
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

d3.select("#main_viz")
  .attr("width", width)
  .attr("height", height)

// HTML element
var svg = d3.select("#main_viz").append("svg")
  .attr("width", width)
  .attr("height", height)
  .attr("viewBox", "0 0 " + width + " " + height)
  .attr("id", "map_svg");

// HTML element
d3.select("header").append("input")
  .attr("type", "date")
  .attr("id", "input_date_s")
  .attr("value", "2020-01-01")
  // .range([width, 10])
  .on("change", function() {
    date_s = int_date(d3.select(this).node().value)
  });

// HTML element
d3.select("header").append("input")
  .attr("type", "date")
  .attr("id", "input_date_e")
  .attr("value", "2020-03-30")
  .on("change", function() {
    date_e = int_date(d3.select(this).node().value)
  })


// HTML element
d3.select("header").append("input")
  .attr("type", "button")
  .attr("id", "map_update")
  .attr("value", "Show transmission within range")
  .on("click", update_transmission);

// date filter
var date_s = int_date(d3.select("#input_date_s").node().value)
var date_e = int_date(d3.select("#input_date_e").node().value)

function update_transmission() {
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

function parse_transmission(error, raw_patients) {
  var patient_count_max = 0;
  var region_patient_count = {};
  var region_connection = [];

  var patients = {}

  for (var pid in raw_patients) {
    if ((raw_patients[pid].date >= date_s) && (raw_patients[pid].date <= date_e)) {
      patients[pid] = raw_patients[pid];
    }
  }

  for (var pid in patients) {
    var patient = patients[pid]
    var region_code = patient.code;
    if (region_patient_count.hasOwnProperty(region_code)) {
      region_patient_count[region_code] += 1;
    } else {
      region_patient_count[region_code] = 1;
    }
    if (patient_count_max < region_patient_count[region_code]) {
      patient_count_max = region_patient_count[region_code];
    }
    for (var i in patient.branch) {
      var iid = patient.branch[i];
      if (patients.hasOwnProperty(iid)) {
        if (patients[pid].code != patients[iid].code) {
          region_connection.push(patients[pid].code + "." + patients[iid].code)
        }
      }
    }
  }
  //unique only
  region_connection = region_connection.filter((v, i, a) => a.indexOf(v) === i)

  for (var pid in patients) {
    var region_code = patients[pid].code;
    if (region_patient_count.hasOwnProperty(region_code)) {
      region_patient_count[region_code] += 1;
    } else {
      region_patient_count[region_code] = 1;
    }
    if (patient_count_max < region_patient_count[region_code]) {
      patient_count_max = region_patient_count[region_code];
    }
  }

  var svg_point = svg.selectAll(".point").data(d3.entries(region_patient_count));
  svg_point.enter()
    .append("circle")
    .merge(svg_point)
    .attr("class", "point")
    .attr("id", function(data, i) {
      return point_code_id_prefix + data.key;
    })
    .attr("cx", function(data, i) {
      var region_path = d3.select("#" + region_code_id_prefix + data.key);
      var region_loc = region_path.node().getBBox();
      return region_loc.x + region_loc.width/2;
    })
    .attr("cy", function(data, i) {
      var region_path = d3.select("#" + region_code_id_prefix + data.key);
      var region_loc = region_path.node().getBBox();
      return region_loc.y + region_loc.height/2;
    })
    .attr("r", function(data, i) {
      return data.value/patient_count_max*2+1;
    });
  svg_point.exit().remove()

  var svg_connection = svg.selectAll(".connection").data(region_connection);
  svg_connection.enter()
    .append("path")
    .merge(svg_connection)
    .attr("class", function(data, i) {
      var sd = data.split(".");
      return "connection " + connection_from_prefix + sd[0] + " " + connection_to_prefix + sd[1];
    })
    .attr("d", function(data, i) {
      var sd = data.split(".");
      var s = d3.select("#" + region_code_id_prefix + sd[0]).node().getBBox();
      var d = d3.select("#" + region_code_id_prefix + sd[1]).node().getBBox();
      return arc_link(s.x + s.width/2,s.y + s.height/2,d.x + d.width/2,d.y + d.height/2);
    })
  svg_connection.exit().remove()
}

function draw_map(error, regions) {
  if (error) console.log(error);
  var svg_city_path = svg.selectAll(".city_path").data(regions.features);
  svg_city_path.enter()
    .append("path")
    .merge(svg_city_path)
    .attr("class", "city_path")
    .attr("d", path)
    .attr("id", function(d) {
      return region_code_id_prefix + d.properties.code
    })
    .on("mouseover", function(d) {
      d3.select(this).classed("active", true)
    })
    .on("mouseout", function(d) {
      d3.select(this).classed("active", false)
    })
    .on("click", function(d) {
      var x = d3.select(this).classed("selected")
      d3.selectAll(".connection").classed("hidden", true); //hide all first; check if it is selection turning off, show them back
      if (!x) { //maybe other is on, need to turn it off first
        d3.selectAll(".selected").classed("selected", false);
        d3.selectAll(".selected_to").classed("selected_to", false);
        d3.selectAll(".selected_from").classed("selected_from", false);
        d3.selectAll(".child").classed("child", false);
        d3.selectAll(".parent").classed("parent", false);
      } else { //turning off selection obviously
        d3.selectAll(".connection").classed("hidden", false); //show them back as promised
      }
      d3.select(this).classed("selected", !x);
      d3.selectAll("."+connection_from_prefix+d.properties.code).classed("hidden", false).classed("child", !x);
      d3.selectAll("."+connection_from_prefix+d.properties.code)
        .each(function() {
          var class_list = d3.select(this).attr("class").split(" ");
          for (var i in class_list) {
            var c = class_list[i];
            if (c.startsWith(connection_to_prefix)) {
              var region_code = c.substr(2);
              console.log("#"+region_code_id_prefix+region_code);
              d3.selectAll("#"+region_code_id_prefix+region_code).classed("selected_to", !x);
            }
          }
        })
      d3.selectAll("."+connection_to_prefix+d.properties.code).classed("hidden", false).classed("parent", !x)
      d3.selectAll("."+connection_to_prefix+d.properties.code)
        .each(function() {
          var class_list = d3.select(this).attr("class").split(" ");
          for (var i in class_list) {
            var c = class_list[i];
            if (c.startsWith(connection_from_prefix)) {
              var region_code = c.substr(2);
              console.log("#"+region_code_id_prefix+region_code);
              d3.selectAll("#"+region_code_id_prefix+region_code).classed("selected_from", !x);
            }
          }
        })
    })
  svg_city_path.exit().remove()
  d3.json(transmission_json, parse_transmission);
}

update_transmission()