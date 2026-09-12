// Independent implementation: reads original JSON numeric lexemes as strings;
// decimal.js (80 digits), independently recomputes both allocations and totals.
import fs from "node:fs";
import assert from "node:assert/strict";
import Decimal from "decimal.js";
Decimal.set({ precision: 80, rounding: Decimal.ROUND_HALF_UP });
const source = fs.readFileSync("data/marketing_daily.json", "utf8");
const rows = JSON.parse(
  source.replace(/(:\s*)(-?\d+(?:\.\d+)?)(\s*[,}])/g, '$1"$2"$3'),
);
const report = JSON.parse(
  fs.readFileSync("public/results/report.json", "utf8"),
);
const names = report.channels.map((c) => c.channel);
const means = Object.fromEntries(
  names.map((c) => {
    const rs = rows.filter((r) => r.channel === c);
    assert.equal(rs.length, 1095);
    return [
      c,
      rs.reduce((a, r) => a.add(r.roas), new Decimal(0)).div(rs.length),
    ];
  }),
);
const budget = new Decimal(500000000),
  caps = { Email: new Decimal(150000000), SMS: new Decimal(120000000) };
const weights = Decimal.sum(...Object.values(means));
const raw = Object.fromEntries(
  names.map((c) => [c, budget.mul(means[c]).div(weights)]),
);
// Official baseline binds no caps. Check this fact independently before using its closed form.
for (const c of ["Email", "SMS"]) assert(raw[c].lte(caps[c]));
const proportional = Object.fromEntries(names.map((c) => [c, raw[c].floor()]));
let residual = budget
  .sub(Decimal.sum(...Object.values(proportional)))
  .toNumber();
for (const c of [...names].sort(
  (a, b) =>
    raw[b].sub(proportional[b]).cmp(raw[a].sub(proportional[a])) ||
    a.localeCompare(b),
)) {
  if (residual-- <= 0) break;
  proportional[c] = proportional[c].add(1);
}
const linear = Object.fromEntries(names.map((c) => [c, new Decimal(0)]));
let left = budget;
for (const c of [...names].sort(
  (a, b) => means[b].cmp(means[a]) || a.localeCompare(b),
)) {
  linear[c] = Decimal.min(left, caps[c] ?? budget);
  left = left.sub(linear[c]);
}
const results = {};
for (const [mode, allocation] of Object.entries({ proportional, linear })) {
  assert(Decimal.sum(...Object.values(allocation)).eq(budget));
  for (const c of names) {
    assert.equal(
      allocation[c].div(100).toFixed(2),
      report.scenarios[mode].allocation[c],
    );
    assert.equal(
      means[c].toFixed(12),
      report.channels.find((x) => x.channel === c).meanRoas,
    );
  }
  const total = Decimal.sum(
    ...names.map((c) => allocation[c].div(100).mul(means[c])),
  ).toFixed(2);
  assert.equal(total, report.scenarios[mode].total);
  results[mode] = total;
}
results.fractionalPaiseProportional = Decimal.sum(
  ...names.map((c) => raw[c].div(100).mul(means[c])),
).toFixed(2);
fs.mkdirSync("artifacts", { recursive: true });
fs.writeFileSync(
  "artifacts/independent-reconciliation.json",
  JSON.stringify(
    {
      passed: true,
      implementation: "Node.js decimal.js, 80-digit precision",
      rows: rows.length,
      ...results,
    },
    null,
    2,
  ),
);
console.log("Independent decimal reconciliation passed:", results);
