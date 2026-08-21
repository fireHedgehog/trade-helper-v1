#!/usr/bin/env bash
set -euo pipefail

# Deterministic Playwright CLI smoke coverage for the zero-build frontend.
# Start the backend first; this script never starts refresh or strategy work.

SMOKE_BASE_URL="${SMOKE_BASE_URL:-http://127.0.0.1:8000}"
PWCLI_BIN="${PWCLI_BIN:-$HOME/.codex/skills/playwright/scripts/playwright_cli.sh}"
SMOKE_SESSION="trade-helper-smoke-$$"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx is required (install Node.js/npm)" >&2
  exit 1
fi
if [[ ! -f "$PWCLI_BIN" ]]; then
  echo "Playwright CLI wrapper not found: $PWCLI_BIN" >&2
  exit 1
fi

pw() {
  bash "$PWCLI_BIN" --session "$SMOKE_SESSION" "$@"
}

cleanup() {
  pw close >/dev/null 2>&1 || true
}
trap cleanup EXIT

snapshot() {
  pw snapshot >/dev/null
}

assert_js() {
  local expression="$1"
  local message="$2"
  if ! pw eval "(() => { if (!($expression)) throw new Error('browser smoke assertion failed'); return 'ok'; })()" >/dev/null; then
    echo "$message" >&2
    exit 1
  fi
}

run_js() {
  local expression="$1"
  local message="$2"
  local output
  if ! output="$(pw eval "$expression" 2>&1)"; then
    echo "$output" >&2
    echo "$message" >&2
    exit 1
  fi
}

pw open "$SMOKE_BASE_URL/#today" >/dev/null
sleep 2
snapshot
assert_js "document.querySelector('#today-status').textContent !== 'Reading saved research…'" "Today did not finish its read-only load"
assert_js "document.querySelector('#dimmer').hidden" "Navigation unexpectedly started a long-running action"
echo "smoke: Today read-only state"

# Pipeline fixtures prove review gating, persisted progress, and retry language
# without starting refresh or strategy work.
run_js "(() => { window.__smokeApi = window.api; window.api = async (path, options) => path === '/api/daily-pipeline/plan' ? ({expected_session:'2026-08-18',status:'refresh_required',refresh:{status:'ready',symbols:['SPY','QQQ'],count:2,delay_seconds:2,minimum_delay_seconds:2},strategy_jobs:[],summary:{ready:1,blocked_data:1,skipped_current:2,skipped_empty:3,excluded_symbols:['BAD'],excluded_count:1}}) : window.__smokeApi(path, options); document.querySelector('#today-plan-pipeline').click(); return 'pipeline fixture installed'; })()" "Could not install deterministic pipeline plan"
sleep 1
snapshot
assert_js "!document.querySelector('#today-run-pipeline').disabled" "Reviewed pipeline did not enable its explicit run action"
assert_js "document.querySelector('#today-pipeline-plan').textContent.includes('Portfolio comparison is excluded')" "Pipeline scope boundary is missing"
assert_js "document.querySelector('#today-pipeline-plan').textContent.includes('excludes 1 non-current symbols: BAD')" "Partial-coverage exclusion is not disclosed in preflight"
pw eval "window.renderPipelineStatus({state:'running',expected_session:'2026-08-18',refresh:{state:'running'},strategy_jobs:[{state:'complete',excluded_data:[{symbol:'BAD',reason:'not_current'}]},{state:'pending'}],message:'fixture running'})" >/dev/null
snapshot
assert_js "document.querySelector('#today-run-pipeline').disabled" "Pipeline action stayed enabled while running"
assert_js "document.querySelector('#today-pipeline-plan').textContent.includes('Excluded from daily discovery (1): BAD')" "Running pipeline hides its excluded coverage"
pw eval "window.renderPipelineStatus({state:'interrupted',expected_session:'2026-08-18',refresh:{state:'interrupted'},strategy_jobs:[{state:'interrupted'}],message:'server stopped before completion'})" >/dev/null
snapshot
assert_js "document.querySelector('#today-run-pipeline').textContent.includes('Retry')" "Interrupted pipeline did not expose retry-by-replanning"
echo "smoke: Pipeline reviewed, running, and interrupted states"

pw resize 390 844 >/dev/null
snapshot
assert_js "getComputedStyle(document.querySelector('.today-actions')).gridTemplateColumns.split(' ').length === 1" "Today actions did not collapse to one narrow-screen column"
assert_js "getComputedStyle(document.querySelector('.section-heading')).flexDirection === 'column'" "Pipeline heading/actions did not stack on narrow screens"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Narrow layout causes page-level horizontal overflow"
echo "smoke: Today narrow layout"

pw eval "location.hash = '#explorer'" >/dev/null
sleep 1
snapshot
assert_js "document.querySelector('#status').textContent.includes('press Run Backtest')" "Symbol Research did not remain not-run"
assert_js "document.querySelector('#dimmer').hidden" "Symbol Research navigation triggered computation"
assert_js "getComputedStyle(document.querySelector('.content')).flexDirection === 'column'" "Symbol Research chart and dossier did not stack on narrow screens"
assert_js "Math.round(document.querySelector('.rail').getBoundingClientRect().width) <= window.innerWidth" "Symbol Research dossier exceeds the narrow viewport"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Symbol Research causes page-level narrow overflow"
echo "smoke: Symbol Research not-run state"

pw eval "location.hash = '#lab'" >/dev/null
sleep 2
snapshot
assert_js "document.querySelector('#lab-run-state').textContent === 'Not run'" "Strategy Lab did not open in not-run state"
pw eval "document.querySelector('#lab-clear').click()" >/dev/null
snapshot
pw eval "document.querySelector('#lab-compute').click()" >/dev/null
snapshot
assert_js "document.querySelector('#lab-run-state').textContent.includes('no symbols selected')" "Empty Strategy Lab selection was not rejected"
assert_js "document.querySelector('#scoreboard').textContent.includes('Select at least one symbol')" "Empty calculation did not explain the required action"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Strategy Lab causes page-level narrow overflow"
echo "smoke: Strategy Lab not-run and empty states"

# Macro response is injected to avoid a live Trading Economics request.
run_js "(() => { window.__smokeApi = window.api; window.api = async (path, options) => path === '/api/macro' ? ({contract:{status:'display_only',permitted_use:'fixture display only',upgrade_requires:'fixture upgrade gate'},cards:[{label:'US 2Y yield',symbol:'DGS2',close:4.2,change_pct:0.1,provider:'FRED',dataset_id:'fred-final-revised-display-v1',observation_date:'2026-08-01',revision_status:'final_revised_current_FRED',release_datetime:null}],events:[{key:'cpi',name:'CPI',category:'Inflation',next:null,last:{actual:2.7,previous:2.8,observation_date:'2026-07-01'},signal_eligible:false}]}) : window.__smokeApi(path, options); location.hash = '#macro'; return 'macro fixture installed'; })()" "Could not install the deterministic Macro fixture"
sleep 1
snapshot
assert_js "document.querySelector('#macro-contract').textContent.includes('Point-in-time vintages: unavailable')" "Macro availability boundary was not rendered"
assert_js "!document.querySelector('#macro-events').textContent.includes('good for equities')" "Macro rendered a prohibited equity-direction claim"
assert_js "document.querySelector('#macro-events').textContent.includes('not signal eligible')" "Macro eligibility warning is missing"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Macro causes page-level narrow overflow"
echo "smoke: Macro display-only state"

# Render each supported Data Management state without provider calls or writes.
run_js "(() => { window.__dataFixture = (state) => ({checked_at:new Date().toISOString(),source:'fixture',adjustment:'fixture',expected_latest_session:'2026-08-18',freshness_policy:'fixture',refresh_policy:{period:'max',delay_seconds:2,retry_backoff_seconds:30,note:'fixture'},summary:{symbols:0,fresh:0,aging:0,stale:0,invalid:0,fred_managed:0},datasets:[],symbols:[],refresh:{state,job_id:'fixture-job',started_at:'2026-08-19T00:00:00Z',finished_at:state === 'running' ? null : '2026-08-19T00:01:00Z',completed:state === 'complete' ? 1 : 0,failed:state === 'complete_with_errors' ? 1 : 0,total:1,current_symbol:state === 'running' ? 'SPY' : null,items:[]}}); window.api = async (path, options) => path.startsWith('/api/data/status') ? window.__dataFixture('running') : window.__smokeApi(path, options); location.hash = '#data'; return 'data fixture installed'; })()" "Could not install deterministic Data Management states"
sleep 1
snapshot
assert_js "document.querySelector('#data-status').textContent.includes('0/1')" "Running data progress was not rendered"
assert_js "document.querySelector('#data-refresh-stale').disabled" "Refresh controls stayed enabled during a running job"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Data Management causes page-level narrow overflow"
pw eval "(() => { clearTimeout(dataPollTimer); window.renderDataStatus(window.__dataFixture('interrupted')); return 'interrupted rendered'; })()" >/dev/null
snapshot
assert_js "document.querySelector('#data-job-note').textContent.includes('server stopped before completion')" "Interrupted recovery guidance is missing"
pw eval "window.renderDataStatus(window.__dataFixture('complete_with_errors'))" >/dev/null
snapshot
assert_js "document.querySelector('#data-job-note').textContent.includes('1 failed')" "Partial-failure count was not rendered"
echo "smoke: Data running, interrupted, and partial-failure states"

# Strategy Library (Strategy Management) response is fixture-injected -- read-only, no live data needed.
run_js "(() => { window.api = async (path, options) => path === '/api/strategy-library' ? ({entries:[{id:'fixture-a',name:'Fixture Tier A Strategy',tier:'A',origin:'preset',origin_label:'Classic preset',type:'Time-Series',category:'time-series trend',decision:'rejected',summary:'Fixture Tier A summary.',github_url:'https://github.com/fireHedgehog/trade-helper-v1/blob/main/docs/research-results/fixture-a.md'},{id:'fixture-b',name:'Fixture Tier B Study',tier:'B',origin:null,origin_label:null,type:'Time-Series',category:'1 §0',decision:'not_material_or_not_consistent',summary:'Fixture Tier B summary.',github_url:'https://github.com/fireHedgehog/trade-helper-v1/blob/main/docs/research-results/fixture-b.md'}]}) : window.__smokeApi(path, options); location.hash = '#records'; return 'strategy library fixture installed'; })()" "Could not install the deterministic Strategy Library fixture"
sleep 1
snapshot
assert_js "document.querySelector('#records-count').textContent.includes('2 total')" "Strategy Management did not render its entry count"
assert_js "document.querySelector('#records-rows').textContent.includes('Fixture Tier A Strategy')" "Strategy Management did not render the fixture Tier A entry"
assert_js "document.querySelector('#records-rows').textContent.includes('Fixture Tier B Study')" "Strategy Management did not render the fixture Tier B entry"
assert_js "document.querySelector('#records-rows a').href.includes('github.com')" "Strategy Management source link is not a GitHub URL"
assert_js "document.documentElement.scrollWidth <= window.innerWidth" "Strategy Management causes page-level narrow overflow"
echo "smoke: Strategy Management read-only record"

# Inject one transport failure and prove it becomes an explicit failure, not a loader.
run_js "(() => { window.api = async () => { throw new Error('smoke transport failure'); }; window.loadData(); return 'failure injected'; })()" "Could not inject the transport failure"
sleep 1
snapshot
assert_js "document.querySelector('#data-status').textContent.includes('status failed')" "Transport failure did not become a visible failed state"
assert_js "document.querySelector('#data-job-note').textContent.includes('Freshness is unknown')" "Failure did not invalidate freshness"
assert_js "document.querySelector('#dimmer').hidden" "Failure left the global loader active"
echo "smoke: transport failure state"
pw resize 1280 900 >/dev/null

console_output="$(pw console error || true)"
if ! grep -q "Errors: 0" <<<"$console_output"; then
  echo "$console_output" >&2
  echo "Browser console contains errors." >&2
  exit 1
fi
echo "Browser smoke passed: read-only navigation, not-run, empty, running, interrupted, partial-failure, and failed states."
