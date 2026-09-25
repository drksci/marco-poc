/* ==========================================================================
   MARCO — visual layer. D3 v7, bound to assets/data.json.

   Five views, each rendering a claim rather than decorating one:

     manifold   the six places positioned only by how far apart their addresses
                are. Nothing about the layout is chosen by hand; it is a
                classical MDS embedding of the address distance matrix, so two
                places that render close *are* close in the coordinate.

     gradient   a slider across the 45 axes. At each position you see how many
                distinct groups the six places fall into and which places are
                still confusable. Dragging it right is progressive refinement.

     ladder     the eight stages from seed to address and root, moved through
                one at a time, each showing the real intermediate value.

     bootstrap  the candidate set collapsing as the generator asks its own
                questions. No question list exists; the trace is what it chose.

     matrix     the 6x6 address distance matrix.

   Each initialiser is idempotent and does nothing if its mount point is absent.
   ========================================================================== */
(function () {
  "use strict";

  var CACHE = null;
  function load() {
    if (CACHE) return Promise.resolve(CACHE);
    return fetch("assets/data.json").then(function (r) { return r.json(); })
      .then(function (d) { CACHE = d; return d; });
  }

  var COLOUR = { ink: "#16161a", muted: "#74747e", rule: "#e2e2e6", grid: "#f4f4f5",
                 signal: "#3f6b52", signalSoft: "#eaf0eb",
                 warm: "#9a6f2f", warmSoft: "#f8f2e6" };

  function text(el, s, attrs) {
    var t = el.append("text").text(s);
    for (var k in (attrs || {})) t.attr(k, attrs[k]);
    return t;
  }

  /* ---------------------------------------------------------------- manifold */
  function manifold(sel, data) {
    var W = 720, H = 460, P = 60;
    var svg = sel.append("svg").attr("viewBox", "0 0 " + W + " " + H)
      .attr("width", "100%").style("max-width", W + "px")
      .style("font-family", "ui-monospace, Menlo, monospace");

    var xs = data.manifold.map(function (m) { return m.x; });
    var ys = data.manifold.map(function (m) { return m.y; });
    var x = d3.scaleLinear().domain([Math.min.apply(null, xs) - 0.12,
                                     Math.max.apply(null, xs) + 0.12]).range([P, W - P]);
    var y = d3.scaleLinear().domain([Math.min.apply(null, ys) - 0.12,
                                     Math.max.apply(null, ys) + 0.12]).range([H - P, P]);

    var dist = {};
    data.matrix_names.forEach(function (a, i) {
      data.matrix_names.forEach(function (b, j) { dist[a + "|" + b] = data.matrix[i][j]; });
    });

    svg.append("g").selectAll("line")
      .data(data.matrix_names.flatMap(function (a, i) {
        return data.matrix_names.slice(i + 1).map(function (b) {
          return { a: a, b: b, d: dist[a + "|" + b] };
        });
      }))
      .join("line")
      .attr("x1", function (e) { return x(byName(data, e.a).x); })
      .attr("y1", function (e) { return y(byName(data, e.a).y); })
      .attr("x2", function (e) { return x(byName(data, e.b).x); })
      .attr("y2", function (e) { return y(byName(data, e.b).y); })
      .attr("stroke", COLOUR.rule)
      .attr("stroke-width", function (e) { return e.d < 12 ? 2 : 1; })
      .attr("stroke-dasharray", function (e) { return e.d < 12 ? null : "2 4"; });

    // distance labels on the two closest pairs, where the number is the point
    svg.append("g").selectAll("text")
      .data(data.matrix_names.flatMap(function (a, i) {
        return data.matrix_names.slice(i + 1).map(function (b) {
          return { a: a, b: b, d: dist[a + "|" + b] };
        });
      }).filter(function (e) { return e.d <= 12; }))
      .join("text")
      .attr("x", function (e) { return (x(byName(data, e.a).x) + x(byName(data, e.b).x)) / 2; })
      .attr("y", function (e) { return (y(byName(data, e.a).y) + y(byName(data, e.b).y)) / 2 - 4; })
      .attr("text-anchor", "middle").attr("font-size", 11).attr("fill", COLOUR.signal)
      .text(function (e) { return "\u2194 " + e.d; });

    var g = svg.append("g").selectAll("g")
      .data(data.manifold).join("g")
      .attr("transform", function (m) { return "translate(" + x(m.x) + "," + y(m.y) + ")"; });

    g.append("circle")
      .attr("r", function (m) { return 12 + m.statements; })
      .attr("fill", COLOUR.signalSoft).attr("stroke", COLOUR.signal).attr("stroke-width", 1.5);

    g.append("text").attr("text-anchor", "middle").attr("y", 4)
      .attr("font-size", 11).attr("fill", COLOUR.ink)
      .text(function (m) { return m.statements; });

    g.append("text").attr("text-anchor", "middle").attr("y", function (m) { return 26 + m.statements; })
      .attr("font-size", 11).attr("fill", COLOUR.ink)
      .text(function (m) { return m.name.replace(/_/g, " "); });

    g.append("text").attr("text-anchor", "middle").attr("y", function (m) { return 40 + m.statements; })
      .attr("font-size", 9.5).attr("fill", COLOUR.muted)
      .text(function (m) { return m.address.slice(2, 22); });

    g.append("text").attr("text-anchor", "middle").attr("y", function (m) { return 52 + m.statements; })
      .attr("font-size", 9).attr("fill", COLOUR.warm)
      .text(function (m) { return "!" + m.root.slice(0, 6); });

    text(svg, "position fitted only to address distance \u00b7 circle holds the number of true statements",
         { x: P, y: H - 16, "font-size": 11, fill: COLOUR.muted });
  }

  function byName(data, n) {
    return data.manifold.filter(function (m) { return m.name === n; })[0];
  }

  /* ---------------------------------------------------------------- gradient */
  function gradient(sel, data) {
    var last = data.gradient[data.gradient.length - 1].axes;
    var W = 720, H = 300, P = 34;
    var svg = sel.append("svg").attr("viewBox", "0 0 " + W + " " + H)
      .attr("width", "100%").style("max-width", W + "px")
      .style("font-family", "ui-monospace, Menlo, monospace");

    var control = sel.append("div")
      .style("display", "flex").style("align-items", "center").style("gap", "12px")
      .style("margin", "10px 0 0").style("font-family", "ui-monospace, Menlo, monospace")
      .style("font-size", "12px");
    control.append("span").text("axes read");
    var slider = control.append("input").attr("type", "range")
      .attr("min", 1).attr("max", last).attr("value", 1).attr("step", 1)
      .style("flex", "1");
    var readout = control.append("span").style("color", COLOUR.muted);

    var addr = sel.append("div").attr("class", "locus-block")
      .style("margin-top", "8px").style("font-size", "15px");

    var gRow = svg.append("g");
    var y = d3.scaleBand().domain(data.manifold.map(function (m) { return m.name; }))
      .range([P, H - P]).padding(0.35);
    var x = d3.scaleLinear().domain([1, last]).range([P + 120, W - P]);

    function draw(k) {
      var step = data.gradient[k - 1];
      readout.text(k + " of " + last + " \u00b7 " + step.distinct + " distinct groups");
      addr.text(step.example);
      gRow.selectAll("*").remove();

      // the six places, grouped by shared prefix
      gRow.selectAll("rect")
        .data(data.manifold)
        .join("rect")
        .attr("x", P).attr("y", function (m) { return y(m.name); })
        .attr("width", 110).attr("height", y.bandwidth())
        .attr("rx", 3)
        .attr("fill", function (m) {
          var gi = step.groups.findIndex(function (gr) { return gr.indexOf(m.name) >= 0; });
          var shade = ["#3f6b52", "#5d7a55", "#7f8f5e", "#9a9d68", "#b0a479", "#c2ab8c"];
          return shade[gi % shade.length];
        })
        .attr("opacity", 0.85);
      gRow.selectAll("text.name")
        .data(data.manifold).join("text")
        .attr("class", "name")
        .attr("x", P + 6).attr("y", function (m) { return y(m.name) + y.bandwidth() / 2 + 4; })
        .attr("font-size", 10.5).attr("fill", "#ffffff")
        .text(function (m) { return m.name.replace(/_/g, " "); });

      // the prefix digits, one per distinct group
      gRow.selectAll("text.digit")
        .data(step.groups).join("text")
        .attr("class", "digit")
        .attr("x", x(k) + 10)
        .attr("y", function (gr, i) { return P + 26 + i * 26; })
        .attr("font-size", 14).attr("fill", COLOUR.ink)
        .text(function (gr) { return "'" + byName(data, gr[0]).prefix.slice(0, k) + "'"; });
      gRow.selectAll("text.members")
        .data(step.groups).join("text")
        .attr("class", "members")
        .attr("x", x(k) + 10)
        .attr("y", function (gr, i) { return P + 40 + i * 26; })
        .attr("font-size", 9.5).attr("fill", COLOUR.muted)
        .text(function (gr) { return gr.map(function (n) { return n.split("_")[0]; }).join(" + "); });

      gRow.selectAll("line.mark")
        .data([k]).join("line").attr("class", "mark")
        .attr("x1", x(k)).attr("x2", x(k)).attr("y1", P - 10).attr("y2", H - P + 10)
        .attr("stroke", COLOUR.rule).attr("stroke-dasharray", "3 3");

      text(gRow, "axes read \u2192", { x: W - P, y: H - 12, "text-anchor": "end",
                                      "font-size": 11, fill: COLOUR.muted });
    }

    slider.on("input", function () { draw(+this.value); });
    draw(1);
  }

  /* ---------------------------------------------------------------- ladder */
  function ladder(sel, data) {
    var W = 720, P = 28;
    var svg = sel.append("svg").attr("viewBox", "0 0 " + W + " 380")
      .attr("width", "100%").style("max-width", W + "px")
      .style("font-family", "ui-monospace, Menlo, monospace");

    var control = sel.append("div")
      .style("display", "flex").style("align-items", "center").style("gap", "10px")
      .style("font-family", "ui-monospace, Menlo, monospace").style("font-size", "12px")
      .style("margin", "10px 0 0");
    var prev = control.append("button").attr("class", "badge").text("\u2190 back");
    var next = control.append("button").attr("class", "badge").text("next stage \u2192");
    var pos = control.append("span").style("color", COLOUR.muted);

    var stage = 0;
    function draw() {
      var s = data.ladder[stage];
      svg.selectAll("*").remove();
      pos.text("stage " + s.n + " of " + data.ladder.length);

      svg.append("rect").attr("x", P).attr("y", 20).attr("width", W - 2 * P)
        .attr("height", 300).attr("rx", 8)
        .attr("fill", COLOUR.grid).attr("stroke", COLOUR.rule);
      text(svg, s.n + "  " + s.name.toUpperCase(),
           { x: P + 22, y: 56, "font-size": 15, fill: COLOUR.ink, "font-weight": "bold" });
      text(svg, "from", { x: P + 22, y: 88, "font-size": 10, fill: COLOUR.muted });
      text(svg, s.in_.slice(0, 92), { x: P + 22, y: 106, "font-size": 12, fill: COLOUR.ink });
      text(svg, "produces", { x: P + 22, y: 142, "font-size": 10, fill: COLOUR.muted });

      var out = s.out;
      var chunks = [];
      while (out.length) { chunks.push(out.slice(0, 96)); out = out.slice(96); }
      chunks.slice(0, 4).forEach(function (c, i) {
        text(svg, c, { x: P + 22, y: 162 + i * 18, "font-size": 12,
                       fill: s.name === "root" ? COLOUR.warm : COLOUR.ink });
      });

      text(svg, s.value, { x: P + 22, y: 292, "font-size": 11.5, fill: COLOUR.muted });

      // the rungs, down the right edge
      data.ladder.forEach(function (l, i) {
        svg.append("circle").attr("cx", W - 60).attr("cy", 52 + i * 32).attr("r", 5)
          .attr("fill", i === stage ? COLOUR.signal : "#ffffff")
          .attr("stroke", i === stage ? COLOUR.signal : COLOUR.rule);
      });
    }
    prev.on("click", function () { stage = Math.max(0, stage - 1); draw(); });
    next.on("click", function () { stage = Math.min(data.ladder.length - 1, stage + 1); draw(); });
    draw();
  }

  /* ------------------------------------------------------------- bootstrap */
  function bootstrap(sel, data) {
    var steps = data.bootstrap.steps;
    var W = 720, H = 260, P = 44;
    var svg = sel.append("svg").attr("viewBox", "0 0 " + W + " " + H)
      .attr("width", "100%").style("max-width", W + "px")
      .style("font-family", "ui-monospace, Menlo, monospace");

    var x = d3.scaleLinear().domain([-0.5, steps.length - 0.5]).range([P, W - P]);
    var y = d3.scaleLog().domain([1, data.bootstrap.population]).range([H - P, P]);
    var line = d3.line()
      .x(function (s, i) { return x(i); })
      .y(function (s) { return y(Math.max(1, s.after)); });

    svg.append("g").selectAll("line")
      .data(y.ticks(4)).join("line")
      .attr("x1", P).attr("x2", W - P).attr("y1", y).attr("y2", y)
      .attr("stroke", COLOUR.grid);
    svg.append("g").selectAll("text")
      .data(y.ticks(4)).join("text")
      .attr("x", P - 8).attr("y", function (d) { return y(d) + 4; })
      .attr("text-anchor", "end").attr("font-size", 10).attr("fill", COLOUR.muted)
      .text(function (d) { return d; });

    svg.append("path").datum(steps).attr("d", line)
      .attr("fill", "none").attr("stroke", COLOUR.signal).attr("stroke-width", 2);

    svg.append("g").selectAll("circle").data(steps).join("circle")
      .attr("cx", function (s, i) { return x(i); })
      .attr("cy", function (s) { return y(Math.max(1, s.after)); })
      .attr("r", 4).attr("fill", function (s) { return s.a ? COLOUR.signal : COLOUR.warm; })
      .append("title").text(function (s) {
        return "q" + s.i + ": " + s.q + "\nanswer " + (s.a ? "yes" : "no") +
               "\n" + s.before + " \u2192 " + s.after + " possible";
      });

    text(svg, data.bootstrap.population + " places", { x: P, y: P - 18, "font-size": 10, fill: COLOUR.muted });
    text(svg, "1 place", { x: P, y: H - P + 22, "font-size": 10, fill: COLOUR.muted });
    text(svg, "questions, in the order the generator chose them (" + data.bootstrap.questions +
              ", then resolved)",
         { x: W - P, y: H - 12, "text-anchor": "end", "font-size": 10, fill: COLOUR.muted });
  }

  /* ---------------------------------------------------------------- matrix */
  function matrix(sel, data) {
    var n = data.matrix_names.length, cell = 62, P = 170;
    var W = P + n * cell + 40, H = P + n * cell + 60;
    var svg = sel.append("svg").attr("viewBox", "0 0 " + W + " " + H)
      .attr("width", "100%").style("max-width", W + "px")
      .style("font-family", "ui-monospace, Menlo, monospace");
    var max = d3.max(data.matrix, function (r) { return d3.max(r); });
    var shade = d3.scaleLinear().domain([0, max])
      .range(["#3f6b52", "#f4f4f5"]);

    data.matrix.forEach(function (row, i) {
      row.forEach(function (v, j) {
        svg.append("rect").attr("x", P + j * cell).attr("y", P + i * cell)
          .attr("width", cell - 2).attr("height", cell - 2)
          .attr("fill", shade(v))
          .attr("stroke", i === j ? COLOUR.ink : null).attr("stroke-width", 2);
        text(svg, v, { x: P + j * cell + cell / 2 - 1, y: P + i * cell + cell / 2 + 5,
                       "text-anchor": "middle", "font-size": 13,
                       fill: v > max * 0.5 ? COLOUR.ink : "#ffffff" });
      });
      text(svg, data.matrix_names[i].replace(/_/g, " "),
           { x: P - 10, y: P + i * cell + cell / 2 + 4, "text-anchor": "end",
             "font-size": 11, fill: COLOUR.ink });
    });
    data.matrix_names.forEach(function (nm, j) {
      svg.append("text").attr("transform", "translate(" + (P + j * cell + cell / 2) + "," +
                              (P - 12) + ") rotate(-42)")
        .attr("font-size", 11).attr("fill", COLOUR.ink)
        .text(nm.replace(/_/g, " "));
    });
    text(svg, "ringed diagonal: the same place, seen by both models",
         { x: P, y: P + n * cell + 30, "font-size": 11, fill: COLOUR.muted });
  }

  /* ---------------------------------------------------------------- mounts */
  function mount() {
    var jobs = [
      ["#viz-manifold", manifold], ["#viz-gradient", gradient],
      ["#viz-ladder", ladder], ["#viz-bootstrap", bootstrap],
      ["#viz-matrix", matrix]
    ].filter(function (j) { return document.querySelector(j[0]); });
    if (!jobs.length) return;
    load().then(function (data) {
      jobs.forEach(function (j) {
        try { j[1](d3.select(j[0]), data); }
        catch (e) { console.error("viz", j[0], e); }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
