/* ==========================================================================
   MARCO — the visual layer. D3 v7, bound to assets/data.json.

   Every view here draws a measured quantity. Nothing is a decorative shape:
   each one binds to a number that also appears under evidence/, so a figure and
   the artefact behind it cannot drift apart.

   Views (each is idempotent, and does nothing when its mount point is absent):

     manifold      six places positioned only by how far apart their addresses
                   are. A classical MDS embedding of the distance matrix, so two
                   places drawn close ARE close in the coordinate.
     gradient      how many distinct names the six places have as you read more
                   of the order, drawn as a curve.
     ladder        the eight stages from seed to address and root.
     bootstrap     the candidate set collapsing as the generator picks its own
                   questions. No question list is transmitted; the trace is what
                   it chose.
     matrix        the 6x6 address distance matrix as a heatmap.
     seedKeys      the eleven top-level keys of the seed, as bars sized by the
                   bytes each one occupies.
     sizeCompare   the three byte counts on one scale: seed, frame, registry.
     rootBars      for each of six places, how many of six independent families
                   produced the byte-identical root.
     controls      the result beside its two nulls, with the null spread drawn.
     precision     how many places fall into how many groups as you read more.
     capability    nine agents from two organisations, laid out by address
                   distance only, with the correct partners joined.
     layers        three positions in one layered environment, by distance.
     turn          the single MARCO/POLO question, drawn as a timeline.
   ========================================================================== */
(function () {
  "use strict";

  var CACHE = null;
  function load() {
    if (CACHE) return Promise.resolve(CACHE);
    return fetch("assets/data.json").then(function (r) { return r.json(); })
      .then(function (d) { CACHE = d; return d; });
  }

  var C = {
    ink: "#16161a", muted: "#74747e", rule: "#e2e2e6", grid: "#f4f4f5",
    signal: "#3f6b52", signalSoft: "#eaf0eb",
    warm: "#9a6f2f", warmSoft: "#f8f2e6",
    blue: "#3a4a6b", blueSoft: "#eef0f5"
  };

  function svgIn(sel, W, H) {
    return sel.append("svg")
      .attr("viewBox", "0 0 " + W + " " + H)
      .attr("width", "100%")
      .attr("preserveAspectRatio", "xMidYMid meet")
      .style("display", "block")
      .style("font-family", "ui-monospace, SFMono-Regular, Menlo, monospace");
  }

  function txt(el, s, attrs) {
    var t = el.append("text").text(s);
    for (var k in (attrs || {})) t.attr(k, attrs[k]);
    return t;
  }

  function byName(data, n) {
    for (var i = 0; i < data.manifold.length; i++)
      if (data.manifold[i].name === n) return data.manifold[i];
    return { x: 0, y: 0 };
  }

  /* ---------------------------------------------------------------- manifold */
  function manifold(sel, data) {
    var W = 780, H = 480, P = 70;
    var svg = svgIn(sel, W, H);
    var xs = data.manifold.map(function (m) { return m.x; });
    var ys = data.manifold.map(function (m) { return m.y; });
    var x = d3.scaleLinear()
      .domain([Math.min.apply(null, xs) - 0.14, Math.max.apply(null, xs) + 0.14])
      .range([P, W - P]);
    var y = d3.scaleLinear()
      .domain([Math.min.apply(null, ys) - 0.14, Math.max.apply(null, ys) + 0.14])
      .range([H - P, P]);

    var dist = {};
    data.matrix_names.forEach(function (a, i) {
      data.matrix_names.forEach(function (b, j) { dist[a + "|" + b] = data.matrix[i][j]; });
    });

    var edges = data.matrix_names.flatMap(function (a, i) {
      return data.matrix_names.slice(i + 1).map(function (b) {
        return { a: a, b: b, d: dist[a + "|" + b] };
      });
    });

    svg.append("g").selectAll("line").data(edges).join("line")
      .attr("x1", function (e) { return x(byName(data, e.a).x); })
      .attr("y1", function (e) { return y(byName(data, e.a).y); })
      .attr("x2", function (e) { return x(byName(data, e.b).x); })
      .attr("y2", function (e) { return y(byName(data, e.b).y); })
      .attr("stroke", function (e) { return e.d <= 9 ? C.signal : C.rule; })
      .attr("stroke-width", function (e) { return e.d <= 9 ? 2.5 : 1; })
      .attr("stroke-dasharray", function (e) { return e.d <= 9 ? null : "2 5"; });

    svg.append("g").selectAll("text")
      .data(edges.filter(function (e) { return e.d <= 9; }))
      .join("text")
      .attr("x", function (e) {
        return (x(byName(data, e.a).x) + x(byName(data, e.b).x)) / 2; })
      .attr("y", function (e) {
        return (y(byName(data, e.a).y) + y(byName(data, e.b).y)) / 2 - 7; })
      .attr("text-anchor", "middle").attr("font-size", 11.5)
      .attr("fill", C.signal).attr("font-weight", "700")
      .text(function (e) { return e.d + " apart"; });

    var g = svg.append("g").selectAll("g").data(data.manifold).join("g")
      .attr("transform", function (p) { return "translate(" + x(p.x) + "," + y(p.y) + ")"; });
    g.append("circle").attr("r", 7)
      .attr("fill", C.signal).attr("stroke", "#ffffff").attr("stroke-width", 2);
    g.append("text").attr("y", -16).attr("text-anchor", "middle")
      .attr("font-size", 12).attr("fill", C.ink).attr("font-weight", "700")
      .text(function (p) { return p.name.replace(/_/g, " "); });
    g.append("text").attr("y", 28).attr("text-anchor", "middle")
      .attr("font-size", 10.5).attr("fill", C.muted)
      .text(function (p) { return p.address.replace("\u2301 ", ""); });
    g.append("text").attr("y", 42).attr("text-anchor", "middle")
      .attr("font-size", 10).attr("fill", C.muted)
      .text(function (p) { return p.statements + " of 45 true"; });

    txt(svg, "positions fitted to the address distances alone",
      { x: P, y: H - 20, "font-size": 11, fill: C.muted });
    txt(svg, "solid green: the two closest pairs, 9 apart",
      { x: W - P, y: H - 20, "font-size": 11, fill: C.signal, "text-anchor": "end" });
  }

  /* -------------------------------------------------------------- seedKeys */
  function seedKeys(sel, data) {
    var rows = data.seed_keys.slice().sort(function (a, b) { return b.bytes - a.bytes; });
    var W = 800, H = 52 + rows.length * 30, P = 200;
    var svg = svgIn(sel, W, H);
    var x = d3.scaleLinear()
      .domain([0, d3.max(rows, function (d) { return d.bytes; })])
      .range([0, W - P - 120]);

    var g = svg.append("g").selectAll("g").data(rows).join("g")
      .attr("transform", function (d, i) { return "translate(0," + (30 + i * 30) + ")"; });

    g.append("text").attr("x", P - 12).attr("y", 16).attr("text-anchor", "end")
      .attr("font-size", 12.5).attr("fill", C.ink)
      .text(function (d) { return d.key; });
    g.append("rect").attr("x", P).attr("y", 3).attr("height", 18).attr("rx", 2)
      .attr("width", function (d) { return Math.max(x(d.bytes), 2); })
      .attr("fill", function (d) { return d.share > 0.5 ? C.signal : C.blue; });
    g.append("text").attr("x", function (d) { return P + x(d.bytes) + 9; })
      .attr("y", 17).attr("font-size", 11.5).attr("fill", C.muted)
      .text(function (d) {
        return d.bytes + " B   " + (d.share * 100).toFixed(1) + "%"; });

    txt(svg, "bars drawn to the bytes each top-level key occupies",
      { x: P, y: 14, "font-size": 11, fill: C.muted });
  }

  /* ----------------------------------------------------------- sizeCompare */
  function sizeCompare(sel, data) {
    var bars = [
      { label: "the seed, sent", v: data.primer.seed_bytes, c: C.signal,
        note: "3,300 bytes, nothing else travels" },
      { label: "the frame each side rebuilds", v: 4532, c: C.blue,
        note: "4,532 bytes, derived, never transmitted" },
      { label: "if the whole registry shipped", v: data.primer.naive_bytes, c: C.warm,
        note: "67,561 bytes, 20.47 times the seed" }
    ];
    var W = 800, H = 250, P = 250;
    var svg = svgIn(sel, W, H);
    var x = d3.scaleLinear().domain([0, data.primer.naive_bytes]).range([0, W - P - 130]);

    var g = svg.append("g").selectAll("g").data(bars).join("g")
      .attr("transform", function (d, i) { return "translate(0," + (46 + i * 56) + ")"; });

    g.append("text").attr("x", P - 14).attr("y", 18).attr("text-anchor", "end")
      .attr("font-size", 12.5).attr("fill", C.ink)
      .text(function (d) { return d.label; });
    g.append("rect").attr("x", P).attr("y", 2).attr("height", 24).attr("rx", 2)
      .attr("width", function (d) { return Math.max(x(d.v), 2); })
      .attr("fill", function (d) { return d.c; });
    g.append("text").attr("x", function (d) { return P + Math.max(x(d.v), 2) + 10; })
      .attr("y", 19).attr("font-size", 12).attr("fill", C.ink)
      .text(function (d) { return d.v.toLocaleString() + " bytes"; });
    g.append("text").attr("x", P).attr("y", 42).attr("font-size", 10.5)
      .attr("fill", C.muted).text(function (d) { return d.note; });

    txt(svg, "one scale, three quantities", { x: P, y: 18,
      "font-size": 12, fill: C.ink, "font-weight": "700" });
  }

  /* ------------------------------------------------------------- rootBars */
  function rootBars(sel, data) {
    var rows = Object.keys(data.roots_by_place).map(function (k) {
      return { place: k, n: data.roots_by_place[k].largest,
               distinct: data.roots_by_place[k].distinct };
    }).sort(function (a, b) { return b.n - a.n; });
    var W = 800, H = 52 + rows.length * 40, P = 210;
    var svg = svgIn(sel, W, H);
    var cell = (W - P - 210) / 6;

    var g = svg.append("g").selectAll("g").data(rows).join("g")
      .attr("transform", function (d, i) { return "translate(0," + (36 + i * 40) + ")"; });

    g.append("text").attr("x", P - 12).attr("y", 19).attr("text-anchor", "end")
      .attr("font-size", 12.5).attr("fill", C.ink)
      .text(function (d) { return d.place.replace(/_/g, " "); });

    g.each(function (d) {
      var gg = d3.select(this);
      d3.range(6).forEach(function (i) {
        gg.append("rect")
          .attr("x", P + i * (cell + 3)).attr("y", 4)
          .attr("width", cell - 3).attr("height", 21).attr("rx", 2)
          .attr("fill", i < d.n ? C.signal : C.grid);
      });
      gg.append("text").attr("x", P + 6 * (cell + 3) + 14).attr("y", 19)
        .attr("font-size", 12).attr("fill", C.muted)
        .text(d.n + " of 6 agree \u00b7 " + d.distinct + " distinct values");
    });

    txt(svg, "filled cells: families that produced the byte-identical root",
      { x: P, y: 16, "font-size": 11, fill: C.muted });
  }

  /* ------------------------------------------------------------- controls */
  function controls(sel, data) {
    var c = data.controls;
    var rows = [
      { label: "real cross-model", v: c.strict, lo: c.strict, hi: c.strict, c: C.signal },
      { label: "label shuffle", v: c.shuffle.accuracy,
        lo: c.shuffle.accuracy - c.shuffle.sd,
        hi: Math.min(c.shuffle.accuracy + c.shuffle.sd, 1), c: C.warm },
      { label: "random vocabulary", v: c.randvocab.accuracy,
        lo: c.randvocab.accuracy - c.randvocab.sd,
        hi: c.randvocab.accuracy + c.randvocab.sd, c: C.warm },
      { label: "chance", v: c.chance, lo: c.chance, hi: c.chance, c: C.muted }
    ];
    var W = 800, H = 290, P = 215;
    var svg = svgIn(sel, W, H);
    var x = d3.scaleLinear().domain([0, 1]).range([P, W - 110]);
    var y = d3.scalePoint().domain(rows.map(function (d) { return d.label; }))
      .range([72, H - 58]);

    svg.append("g").selectAll("line").data(x.ticks(5)).join("line")
      .attr("x1", x).attr("x2", x).attr("y1", 62).attr("y2", H - 50)
      .attr("stroke", C.grid);
    svg.append("g").selectAll("text").data(x.ticks(5)).join("text")
      .attr("x", x).attr("y", H - 28).attr("text-anchor", "middle")
      .attr("font-size", 10.5).attr("fill", C.muted)
      .text(function (d) { return (d * 100).toFixed(0) + "%"; });

    var g = svg.append("g").selectAll("g").data(rows).join("g")
      .attr("transform", function (d) { return "translate(0," + y(d.label) + ")"; });

    g.append("text").attr("x", P - 14).attr("y", 5).attr("text-anchor", "end")
      .attr("font-size", 12.5).attr("fill", C.ink)
      .text(function (d) { return d.label; });
    g.append("line").attr("x1", function (d) { return x(d.lo); })
      .attr("x2", function (d) { return x(d.hi); })
      .attr("stroke", function (d) { return d.c; }).attr("stroke-width", 2.5)
      .attr("opacity", 0.5);
    g.append("circle").attr("cx", function (d) { return x(d.v); }).attr("r", 7)
      .attr("fill", function (d) { return d.c; });
    g.append("text").attr("x", function (d) { return x(d.v) + 15; }).attr("y", 5)
      .attr("font-size", 12).attr("fill", C.muted)
      .text(function (d) { return (d.v * 100).toFixed(1) + "%"; });

    txt(svg, "same room came out nearest, strict", { x: P, y: 24,
      "font-size": 12.5, fill: C.ink, "font-weight": "700" });
    txt(svg, "whiskers: one standard deviation, 6,000 trials per null",
      { x: P, y: H - 10, "font-size": 11, fill: C.muted });
  }

  /* ---------------------------------------------------------------- matrix */
  function matrix(sel, data) {
    var n = data.matrix_names.length;
    var cell = 54, P = 168;
    var W = P + n * cell + 70, H = P + n * cell + 76;
    var svg = svgIn(sel, W, H);
    var max = d3.max(data.matrix, function (r) { return d3.max(r); });
    var fill = d3.scaleSequential().domain([0, max]).interpolator(d3.interpolateGreens);

    var cells = [];
    data.matrix.forEach(function (row, i) {
      row.forEach(function (v, j) { cells.push({ i: i, j: j, v: v }); });
    });

    var g = svg.append("g").selectAll("g").data(cells).join("g")
      .attr("transform", function (d) {
        return "translate(" + (P + d.j * cell) + "," + (P + d.i * cell) + ")"; });
    g.append("rect").attr("width", cell - 2).attr("height", cell - 2)
      .attr("fill", function (d) { return d.i === d.j ? "#ffffff" : fill(d.v); })
      .attr("stroke", C.rule);
    g.append("text").attr("x", (cell - 2) / 2).attr("y", (cell - 2) / 2 + 5)
      .attr("text-anchor", "middle").attr("font-size", 13)
      .attr("fill", function (d) { return d.v > max * 0.55 ? "#ffffff" : C.ink; })
      .text(function (d) { return d.i === d.j ? "\u00b7" : d.v; });

    svg.append("g").selectAll("text").data(data.matrix_names).join("text")
      .attr("x", P - 10).attr("y", function (d, i) { return P + i * cell + cell / 2 + 4; })
      .attr("text-anchor", "end").attr("font-size", 11).attr("fill", C.ink)
      .text(function (d) { return d.replace(/_/g, " "); });

    svg.append("g").selectAll("text").data(data.matrix_names).join("text")
      .attr("transform", function (d, i) {
        return "translate(" + (P + i * cell + cell / 2 + 4) + "," + (P - 14) + ") rotate(-45)"; })
      .attr("text-anchor", "start").attr("font-size", 11).attr("fill", C.ink)
      .text(function (d) { return d.replace(/_/g, " "); });

    txt(svg, "distance between two addresses, in letters of 36. Blank diagonal: a place against itself.",
      { x: P, y: H - 20, "font-size": 11, fill: C.muted });
  }

  /* ------------------------------------------------------------- bootstrap */
  function bootstrap(sel, data) {
    var steps = data.bootstrap.steps;
    var W = 780, H = 330, P = 66;
    var svg = svgIn(sel, W, H);
    var x = d3.scaleLinear().domain([-0.5, steps.length - 0.5]).range([P, W - P]);
    var y = d3.scaleLog().domain([1, data.bootstrap.population]).range([H - P, P + 20]);

    svg.append("g").selectAll("line").data(y.ticks(4, "~s")).join("line")
      .attr("x1", P).attr("x2", W - P).attr("y1", y).attr("y2", y)
      .attr("stroke", C.grid);
    svg.append("g").selectAll("text").data(y.ticks(4, "~s")).join("text")
      .attr("x", P - 8).attr("y", function (d) { return y(d) + 4; })
      .attr("text-anchor", "end").attr("font-size", 10.5).attr("fill", C.muted)
      .text(function (d) { return d; });

    // what a purely random strategy would do, for contrast
    svg.append("path")
      .datum(steps.map(function (s, i) {
        return { after: data.bootstrap.population / Math.pow(2, i + 1) }; }))
      .attr("d", d3.line()
        .x(function (d, i) { return x(i); })
        .y(function (d) { return y(Math.max(d.after, 1)); }))
      .attr("fill", "none").attr("stroke", C.rule).attr("stroke-dasharray", "4 4");

    svg.append("path").datum(steps)
      .attr("d", d3.line()
        .x(function (d, i) { return x(i); })
        .y(function (d) { return y(Math.max(d.after, 1)); }))
      .attr("fill", "none").attr("stroke", C.signal).attr("stroke-width", 2.5);

    svg.append("g").selectAll("circle").data(steps).join("circle")
      .attr("cx", function (s, i) { return x(i); })
      .attr("cy", function (s) { return y(Math.max(s.after, 1)); })
      .attr("r", 2.8)
      .attr("fill", function (s) { return s.a ? C.signal : C.warm; })
      .append("title").text(function (s) {
        return "q" + s.i + ": " + s.q + "\nanswer " + (s.a ? "yes" : "no") +
               "\n" + s.before + " \u2192 " + s.after + " candidates left";
      });

    txt(svg, data.bootstrap.population + " candidate places", { x: P, y: P + 8,
      "font-size": 11, fill: C.muted });
    txt(svg, "one candidate left after " + data.bootstrap.questions + " questions",
      { x: W - P, y: H - P + 24, "text-anchor": "end", "font-size": 11, fill: C.warm });
    txt(svg, "the generator chose each question to halve what was left",
      { x: P - 8, y: 26, "font-size": 12, fill: C.ink, "font-weight": "700" });
    txt(svg, "questions, in the order the generator chose them",
      { x: W - P, y: H - 12, "text-anchor": "end", "font-size": 11, fill: C.muted });
  }

  /* ------------------------------------------------------------- precision */
  function precision(sel, data) {
    var W = 800, H = 320, P = 70;
    var svg = svgIn(sel, W, H);
    var pts = data.gradient;
    var x = d3.scaleLinear().domain([0, 45]).range([P, W - P]);
    var y = d3.scaleLinear().domain([0, 7]).range([H - P, P + 10]);

    svg.append("g").selectAll("line").data(y.ticks(6)).join("line")
      .attr("x1", P).attr("x2", W - P).attr("y1", y).attr("y2", y)
      .attr("stroke", C.grid);
    svg.append("g").selectAll("text").data(y.ticks(6)).join("text")
      .attr("x", P - 10).attr("y", function (d) { return y(d) + 4; })
      .attr("text-anchor", "end").attr("font-size", 10.5).attr("fill", C.muted)
      .text(function (d) { return d; });

    svg.append("path").datum(pts)
      .attr("d", d3.line()
        .x(function (d) { return x(d.axes); })
        .y(function (d) { return y(d.distinct); })
        .curve(d3.curveStepAfter))
      .attr("fill", "none").attr("stroke", C.signal).attr("stroke-width", 2.5);

    svg.append("g").selectAll("circle").data(pts).join("circle")
      .attr("cx", function (d) { return x(d.axes); })
      .attr("cy", function (d) { return y(d.distinct); })
      .attr("r", 4.5).attr("fill", C.signal);

    svg.append("g").selectAll("text").data(pts).join("text")
      .attr("x", function (d) { return x(d.axes); })
      .attr("y", H - P + 24).attr("text-anchor", "middle")
      .attr("font-size", 11).attr("fill", C.muted)
      .text(function (d) { return d.axes; });

    var six = pts.filter(function (d) { return d.distinct === 6; })[0];
    svg.append("line")
      .attr("x1", x(six.axes)).attr("x2", x(six.axes))
      .attr("y1", P + 10).attr("y2", H - P)
      .attr("stroke", C.warm).attr("stroke-dasharray", "3 4");
    txt(svg, "at " + six.axes + " questions, all six are apart",
      { x: x(six.axes) + 9, y: P + 26, "font-size": 11, fill: C.warm });

    txt(svg, "distinct names", { x: P - 10, y: P + 2, "font-size": 11,
      fill: C.muted, "text-anchor": "end" });
    txt(svg, "questions read", { x: W / 2, y: H - 12, "font-size": 11,
      fill: C.muted, "text-anchor": "middle" });
    txt(svg, "the count never falls. No two places that stood apart are ever merged.",
      { x: P, y: 26, "font-size": 12, fill: C.ink, "font-weight": "700" });
  }

  /* ------------------------------------------------------------ capability */
  function capability(sel, data) {
    var W = 800, H = 470, P = 80;
    var svg = svgIn(sel, W, H);
    var agents = data.capability.agents;

    function strip(a) { return a.replace("\u2301 ", "").replace(/[\u00b7+~.]/g, ""); }
    var names = agents.map(function (a) { return strip(a.address); });
    var n = names.length;
    var D = [];
    for (var i = 0; i < n; i++) {
      var row = [];
      for (var j = 0; j < n; j++) {
        var a = names[i], b = names[j], d = 0, L = Math.max(a.length, b.length);
        for (var k = 0; k < L; k++) if (a[k] !== b[k]) d++;
        row.push(d);
      }
      D.push(row);
    }
    var J = [];
    for (i = 0; i < n; i++) {
      J.push([]);
      for (j = 0; j < n; j++) J[i].push(i === j ? 1 - 1 / n : -1 / n);
    }
    var B = [];
    for (i = 0; i < n; i++) {
      B.push([]);
      for (j = 0; j < n; j++) {
        var s = 0;
        for (var p = 0; p < n; p++) for (var q = 0; q < n; q++)
          s += J[i][p] * (-0.5 * D[p][q] * D[p][q]) * J[q][j];
        B[i].push(s);
      }
    }
    function power(M) {
      var v = [];
      for (var i2 = 0; i2 < n; i2++) v.push(Math.sin(i2 * 1.7) + 0.3);
      for (var it = 0; it < 300; it++) {
        var w = [];
        for (var i3 = 0; i3 < n; i3++) {
          var t = 0;
          for (var j3 = 0; j3 < n; j3++) t += M[i3][j3] * v[j3];
          w.push(t);
        }
        var nrm = Math.sqrt(w.reduce(function (x, y) { return x + y * y; }, 0)) || 1;
        v = w.map(function (x) { return x / nrm; });
      }
      return v;
    }
    var v1 = power(B), l1 = 0;
    for (i = 0; i < n; i++) {
      var t1 = 0;
      for (j = 0; j < n; j++) t1 += B[i][j] * v1[j];
      l1 += v1[i] * t1;
    }
    var B2 = B.map(function (r, i2) {
      return r.map(function (x, j2) { return x - l1 * v1[i2] * v1[j2]; });
    });
    var v2 = power(B2), l2 = 0;
    for (i = 0; i < n; i++) {
      var t2 = 0;
      for (j = 0; j < n; j++) t2 += B2[i][j] * v2[j];
      l2 += v2[i] * t2;
    }

    var xs = v1.map(function (x) { return x * Math.sqrt(Math.max(l1, 0)); });
    var ys = v2.map(function (x) { return x * Math.sqrt(Math.max(l2, 0)); });
    var pad = 0.25;
    var x = d3.scaleLinear()
      .domain([d3.min(xs) - pad, d3.max(xs) + pad]).range([P, W - P]);
    var y = d3.scaleLinear()
      .domain([d3.min(ys) - pad, d3.max(ys) + pad]).range([H - P, P + 40]);

    var jobs = {};
    agents.forEach(function (a) { (jobs[a.job] = jobs[a.job] || []).push(a); });

    Object.keys(jobs).forEach(function (job) {
      var grp = jobs[job];
      if (grp.length !== 2) return;
      var i1 = agents.indexOf(grp[0]), i2 = agents.indexOf(grp[1]);
      svg.append("line")
        .attr("x1", x(xs[i1])).attr("y1", y(ys[i1]))
        .attr("x2", x(xs[i2])).attr("y2", y(ys[i2]))
        .attr("stroke", C.signal).attr("stroke-width", 2.5);
    });

    var g = svg.append("g").selectAll("g").data(agents).join("g")
      .attr("transform", function (a, i2) {
        return "translate(" + x(xs[i2]) + "," + y(ys[i2]) + ")"; });

    g.append("circle").attr("r", 6)
      .attr("fill", function (a) { return a.org === "acme.com" ? C.blue : C.warm; })
      .attr("stroke", "#fff").attr("stroke-width", 1.5);
    g.append("text").attr("y", -13).attr("text-anchor", "middle")
      .attr("font-size", 10.5).attr("fill", C.ink)
      .text(function (a) { return a.path; });
    g.append("text").attr("y", 20).attr("text-anchor", "middle")
      .attr("font-size", 10).attr("fill", C.muted)
      .text(function (a) { return a.org; });

    txt(svg, "nine agents, laid out by address distance only",
      { x: P, y: 24, "font-size": 12, fill: C.ink, "font-weight": "700" });
    txt(svg, "green lines: the four pairs doing the same job, with no mapping table.",
      { x: P, y: H - 14, "font-size": 11, fill: C.signal });
  }

  /* ---------------------------------------------------------------- layers */
  function layers(sel, data) {
    var ov = data.overlay;
    var keys = ["base", "project", "session"];
    var W = 800, H = 330, P = 100;
    var svg = svgIn(sel, W, H);
    var bp = ov.pairs["base|project"].hamming;
    var bs = ov.pairs["base|session"].hamming;
    var xs = { base: 0, project: bp, session: bs };
    var maxx = Math.max(bp, bs);
    var x = d3.scaleLinear().domain([-1.2, maxx + 1.2]).range([P, W - P - 130]);

    svg.append("line").attr("x1", P).attr("x2", W - P - 130)
      .attr("y1", 175).attr("y2", 175).attr("stroke", C.rule).attr("stroke-width", 2);

    keys.forEach(function (k) {
      var pos = ov.positions[k];
      var g = svg.append("g").attr("transform", "translate(" + x(xs[k]) + ",175)");
      g.append("circle").attr("r", 8).attr("fill", C.signal)
        .attr("stroke", "#fff").attr("stroke-width", 2);
      g.append("text").attr("y", -22).attr("text-anchor", "middle")
        .attr("font-size", 12).attr("fill", C.ink).attr("font-weight", "700")
        .text(pos.layer);
      g.append("text").attr("y", 32).attr("text-anchor", "middle")
        .attr("font-size", 10.5).attr("fill", C.muted)
        .text(pos.n_statements + " statements true");
      g.append("text").attr("y", -40).attr("text-anchor", "middle")
        .attr("font-size", 10).attr("fill", C.muted)
        .text(pos.address.replace("\u2301 ", "").slice(0, 30));
      g.append("text").attr("y", 50).attr("text-anchor", "middle")
        .attr("font-size", 10).attr("fill", C.muted)
        .text("\u2301 " + pos.marker);
    });

    var cg = svg.append("g").attr("transform", "translate(" + (W - P - 56) + ",175)");
    cg.append("circle").attr("r", 8).attr("fill", C.warm)
      .attr("stroke", "#fff").attr("stroke-width", 2);
    cg.append("text").attr("y", -22).attr("text-anchor", "middle")
      .attr("font-size", 12).attr("fill", C.warm).text("a sealed empty room");
    cg.append("text").attr("y", 32).attr("text-anchor", "middle")
      .attr("font-size", 10.5).attr("fill", C.muted).text("24 letters away");

    txt(svg, "three positions in one environment, and one room with nothing in common",
      { x: P, y: 26, "font-size": 12, fill: C.ink, "font-weight": "700" });
    txt(svg, "distance in letters of a 36-letter address",
      { x: P, y: H - 14, "font-size": 11, fill: C.muted });
  }

  /* ------------------------------------------------------------------ turn */
  function turn(sel, data) {
    var p = data.polo;
    var W = 800, H = 300, P = 100;
    var svg = svgIn(sel, W, H);
    var rows = [
      { who: "hider", what: "discloses " + p.opening_address, at: 0, up: true },
      { who: "seeker", what: "asks whether the hider can see other people", at: 1, up: false },
      { who: "hider", what: "answers YES", at: 2, up: true },
      { who: "seeker", what: "rebuilds the coordinate, compares the root, and agrees", at: 3, up: false }
    ];
    var x = d3.scalePoint().domain([0, 1, 2, 3]).range([P, W - P]);

    svg.append("line").attr("x1", P).attr("x2", W - P)
      .attr("y1", 150).attr("y2", 150).attr("stroke", C.rule).attr("stroke-width", 2);

    rows.forEach(function (r) {
      var g = svg.append("g").attr("transform", "translate(" + x(r.at) + ",150)");
      g.append("circle").attr("r", 8)
        .attr("fill", r.who === "hider" ? C.signal : C.blue)
        .attr("stroke", "#fff").attr("stroke-width", 2);
      g.append("text").attr("y", r.up ? -48 : 44).attr("text-anchor", "middle")
        .attr("font-size", 10.5).attr("fill", C.muted).text(r.who);
      g.append("text").attr("y", r.up ? -32 : 62).attr("text-anchor", "middle")
        .attr("font-size", 11).attr("fill", C.ink).text(r.what);
    });

    txt(svg, "verdict " + p.verdict + " \u00b7 " + p.questions_asked + " question \u00b7 " +
        p.hider_calls + " model call \u00b7 $" + p.cost_usd.toFixed(7),
      { x: P, y: 26, "font-size": 12, fill: C.ink, "font-weight": "700" });
    txt(svg, "the hider is " + p.hider_model + ", told which place it is in and never asked to name it",
      { x: P, y: H - 14, "font-size": 11, fill: C.muted });
  }

  /* ------------------------------------------------------------------ ladder */
  function ladder(sel, data) {
    var W = 800, H = 200, P = 70;
    var svg = svgIn(sel, W, H);

    sel.append("div")
      .attr("class", "flex flex-wrap items-center gap-3 mt-3 text-sm font-mono")
      .html('<button class="btn btn-xs" data-l="prev">\u2190 back</button>' +
            '<button class="btn btn-xs" data-l="next">next stage \u2192</button>' +
            '<span class="opacity-60" data-l="pos"></span>');

    var box = sel.append("div")
      .attr("class", "mt-3 rounded-box border border-base-300 bg-base-200/60 p-4 " +
                      "font-mono text-sm leading-relaxed");

    var stage = 0;
    function draw() {
      var s = data.ladder[stage];
      svg.selectAll("*").remove();
      sel.select('[data-l="pos"]').text("stage " + s.n + " of " + data.ladder.length);
      box.html(
        '<div class="text-base-content font-bold">' + s.n + '  ' + s.name + '</div>' +
        '<div class="opacity-60 mt-2 text-xs uppercase tracking-wider">from</div>' +
        '<div class="break-words">' + esc(s.in_) + '</div>' +
        '<div class="opacity-60 mt-3 text-xs uppercase tracking-wider">produces</div>' +
        '<div class="break-words">' + esc(s.out) + '</div>' +
        '<div class="opacity-70 mt-3 text-xs">' + esc(s.value) + '</div>');

      var step = (W - 2 * P) / (data.ladder.length - 1);
      svg.append("line").attr("x1", P).attr("x2", W - P)
        .attr("y1", 105).attr("y2", 105).attr("stroke", C.rule).attr("stroke-width", 2);
      data.ladder.forEach(function (l, i) {
        var g = svg.append("g")
          .attr("transform", "translate(" + (P + i * step) + ",105)");
        g.append("circle").attr("r", i === stage ? 10 : 7)
          .attr("fill", i <= stage ? (l.n >= 7 ? C.warm : C.signal) : "#ffffff")
          .attr("stroke", i === stage ? C.ink : C.rule).attr("stroke-width", 2);
        g.append("text").attr("y", 30).attr("text-anchor", "middle")
          .attr("font-size", 10.5)
          .attr("fill", i === stage ? C.ink : C.muted)
          .text(l.name.split(" ")[0]);
      });
    }
    function esc(s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
    sel.select('[data-l="prev"]').on("click", function () {
      stage = Math.max(0, stage - 1); draw(); });
    sel.select('[data-l="next"]').on("click", function () {
      stage = Math.min(data.ladder.length - 1, stage + 1); draw(); });
    draw();
  }

  /* -------------------------------------------------------------- pipeline */
  function pipeline(sel, data) {
    var p = data.whale_pipeline;
    var W = 860, H = 470;
    var svg = svgIn(sel, W, H);
    var cols = 6;
    var cw = (W - 80) / cols;
    var x = function (c) { return 40 + c * cw + cw / 2; };
    var rowY = { 0: 70, 2: 250, 3: 350 };
    var y = function (r) { return rowY[r]; };

    var nodeH = 58, nodeW = cw - 16;

    p.edges.forEach(function (e) {
      var a = p.stages.filter(function (s) { return s.id === e[0]; })[0];
      var b = p.stages.filter(function (s) { return s.id === e[1]; })[0];
      var x1 = x(a.col), y1 = y(a.row), x2 = x(b.col) + (b.row !== a.row ? -0 : 0);
      if (a.row === b.row) {
        svg.append("line").attr("x1", x1 + nodeW / 2).attr("x2", x(b.col) - nodeW / 2)
          .attr("y1", y1).attr("y2", y1)
          .attr("stroke", C.rule).attr("stroke-width", 2)
          .attr("marker-end", "url(#arw)");
      } else {
        svg.append("path")
          .attr("d", "M " + x1 + " " + (y1 + nodeH / 2) +
                    " C " + x1 + " " + (y1 + 60) + ", " + x(b.col) + " " + (y(b.row) - 60) +
                    ", " + x(b.col) + " " + (y(b.row) - nodeH / 2))
          .attr("fill", "none").attr("stroke", C.rule).attr("stroke-width", 2)
          .attr("marker-end", "url(#arw)");
      }
    });

    var defs = svg.append("defs");
    var mk = defs.append("marker").attr("id", "arw").attr("viewBox", "0 0 10 10")
      .attr("refX", 9).attr("refY", 5).attr("markerWidth", 6).attr("markerHeight", 6)
      .attr("orient", "auto-start-reverse");
    mk.append("path").attr("d", "M 0 0 L 10 5 L 0 10 z").attr("fill", C.muted);

    p.stages.forEach(function (s) {
      var g = svg.append("g")
        .attr("transform", "translate(" + (x(s.col) - nodeW / 2) + "," + (y(s.row) - nodeH / 2) + ")");
      g.append("rect").attr("width", nodeW).attr("height", nodeH).attr("rx", 6)
        .attr("fill", s.id === "addr" ? C.signalSoft : "#ffffff")
        .attr("stroke", s.id === "addr" ? C.signal : C.rule)
        .attr("stroke-width", s.id === "addr" ? 2 : 1);
      g.append("foreignObject").attr("width", nodeW - 12).attr("height", nodeH - 8)
        .attr("x", 6).attr("y", 4)
        .append("xhtml:div")
        .attr("style", "font-family:ui-monospace,Menlo,monospace;font-size:11px;line-height:1.25;color:" + C.ink)
        .html("<b>" + s.label + "</b><br><span style='color:" + C.muted + "'>" + s.note + "</span>");
    });

    p.gates.forEach(function (gt) {
      var g = svg.append("g")
        .attr("transform", "translate(" + (x(gt.col) - nodeW / 2) + "," + (y(gt.row) - 14) + ")");
      g.append("rect").attr("width", nodeW).attr("height", 28).attr("rx", 4)
        .attr("fill", C.warmSoft).attr("stroke", C.warm).attr("stroke-dasharray", "3 3");
      g.append("foreignObject").attr("width", nodeW - 12).attr("height", 24)
        .attr("x", 6).attr("y", 2)
        .append("xhtml:div")
        .attr("style", "font-family:ui-monospace,Menlo,monospace;font-size:10px;line-height:1.2;color:" + C.warm)
        .text(gt.label);
    });

    txt(svg, "top row: from a recording to a phrase address. lower rows: a neural response, and the mapping between them.",
      { x: 40, y: 24, "font-size": 12, fill: C.ink, "font-weight": "700" });
    txt(svg, "the dashed boxes are the controls, and they are the hard part",
      { x: 40, y: H - 50, "font-size": 11, fill: C.warm });
    txt(svg, "every choice above is made on training folds only, then frozen before the test",
      { x: 40, y: H - 28, "font-size": 11, fill: C.muted });
  }

  /* ---------------------------------------------------------------- mounts */
  var VIEWS = {
    pipeline: pipeline,
    manifold: manifold, ladder: ladder, bootstrap: bootstrap,
    matrix: matrix, seedKeys: seedKeys, sizeCompare: sizeCompare,
    rootBars: rootBars, controls: controls, precision: precision,
    capability: capability, layers: layers, turn: turn
  };

  function mount() {
    var jobs = Object.keys(VIEWS)
      .map(function (k) { return ["#viz-" + k, VIEWS[k]]; })
      .filter(function (j) { return document.querySelector(j[0]); });
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