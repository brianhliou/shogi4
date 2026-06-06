#!/usr/bin/env python3
"""Parse recorded game-*.txt replays into a self-contained HTML board viewer.

Reads the ply-by-ply replays (board grids + moves + evals already rendered by
watch_game/batch_games) and emits viewer/index.html with the games embedded, plus
a small JS stepper (board, eval normalized to White, hands, prev/next/autoplay).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "viewer")
FILES = [f"game-{i}.txt" for i in range(1, 9)] + ["game-strong.txt"]

HDR = re.compile(r"^--- ply\s+(\d+)\s+(White|Black)\s+(\S+)\s+eval\s+(\S+)\s+\(d(\d+)\)(?:\s+\[([^\]]*)\])?")


def parse(path):
    name = os.path.basename(path).replace(".txt", "")
    plies, result = [], "?"
    pend = None            # header dict awaiting its board, or None for the start board
    rows, h1, h2, in_board = [], "-", "-", False
    with open(path) as f:
        for line in f:
            s = line.rstrip("\n")
            m = HDR.match(s)
            if m:
                pend = {"ply": int(m[1]), "mover": m[2], "move": m[3],
                        "eval": m[4], "depth": int(m[5]), "tag": m[6] or ""}
                continue
            if "WINS" in s or "draw" in s.lower() and "===" in s:
                result = s.replace("=", "").strip()
            if "black hand:" in s:
                rows, in_board = [], True
                h2 = s.split("black hand:")[1].strip()
                continue
            if in_board and re.match(r"\s*[1-4]\s", s):
                rows.append(s.split()[1:5])
                continue
            if "white hand:" in s:
                h1 = s.split("white hand:")[1].strip()
                cells = [c for row in rows for c in row]   # rank4..rank1, a..d
                node = {"cells": cells, "h1": h1, "h2": h2}
                if pend is None and not plies:
                    node.update({"ply": 0, "mover": "", "move": "", "eval": "", "depth": 0, "tag": ""})
                else:
                    node.update(pend)
                    node["dst"] = dst_of(pend["move"])
                plies.append(node)
                pend, in_board = None, False
    return {"name": name, "result": result, "plies": plies}


def dst_of(mv):
    if "@" in mv:
        return mv.split("@")[1]
    mv = mv.rstrip("+")
    return mv[2:4]


def main():
    games = [parse(os.path.join(HERE, fn)) for fn in FILES if os.path.exists(os.path.join(HERE, fn))]
    os.makedirs(OUT, exist_ok=True)
    html = TEMPLATE.replace("/*DATA*/", json.dumps(games))
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(html)
    print(f"wrote {OUT}/index.html with {len(games)} games "
          f"({sum(len(g['plies']) for g in games)} positions)")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shogi4 — engine game viewer</title>
<style>
  :root { --w:#1769aa; --b:#b23b3b; --promo:#caa000; --hi:#ffe79e; --line:#caa46a; }
  * { box-sizing:border-box; }
  body { font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif; margin:0; background:#f6f1e7; color:#2b2620; }
  .wrap { max-width:760px; margin:24px auto; padding:0 16px; }
  h1 { font-size:19px; margin:0 0 2px; } .sub { color:#7a7164; margin:0 0 16px; font-size:13px; }
  .row { display:flex; gap:20px; flex-wrap:wrap; align-items:flex-start; }
  select,button { font:inherit; padding:5px 9px; border:1px solid #c9bfa9; border-radius:7px; background:#fff; cursor:pointer; }
  button:hover { background:#f0ead9; } button:disabled { opacity:.4; cursor:default; }
  .board { display:grid; grid-template-columns:repeat(4,62px); grid-template-rows:repeat(4,62px);
           border:2px solid #6b5836; background:#e8d6ab; }
  .sq { border:1px solid var(--line); display:flex; flex-direction:column; align-items:center; justify-content:center;
        position:relative; }
  .sq.hi { background:var(--hi); }
  .pc { font-weight:700; font-size:20px; line-height:1; }
  .pc.w { color:var(--w); } .pc.b { color:var(--b); }
  .pc.promo { color:var(--promo); }
  .pc small { display:block; font-size:8px; font-weight:600; opacity:.65; margin-top:2px; }
  .coord { position:absolute; font-size:8px; color:#9a8c70; top:1px; left:2px; }
  .panel { min-width:230px; flex:1; }
  .eval { font-size:26px; font-weight:700; margin:2px 0 6px; }
  .meta { color:#6b6356; font-size:13px; margin-bottom:10px; }
  .controls { display:flex; gap:6px; margin:12px 0; }
  .controls input[type=range] { flex:1; }
  .hand { font-size:13px; color:#5a5346; } .hand b { color:#2b2620; }
  .tag { display:inline-block; font-size:11px; padding:1px 6px; border-radius:4px; background:#e4dcc8; margin-left:6px; }
  .res { margin-top:10px; font-weight:600; }
</style></head>
<body><div class="wrap">
  <h1>Shogi4 — engine self-play viewer</h1>
  <p class="sub">Patched Fairy-Stockfish, friendly-jump variant. White = first player (sente). Eval shown White-relative.</p>
  <div class="row">
    <div>
      <div style="margin-bottom:8px"><select id="game"></select></div>
      <div class="hand" id="bhand"></div>
      <div class="board" id="board"></div>
      <div class="hand" id="whand" style="margin-top:6px"></div>
    </div>
    <div class="panel">
      <div class="eval" id="eval">—</div>
      <div class="meta" id="meta"></div>
      <div class="controls">
        <button id="first">⏮</button><button id="prev">◀</button>
        <button id="play">▶ play</button>
        <button id="next">▶</button><button id="last">⏭</button>
      </div>
      <input type="range" id="slider" min="0" value="0" style="width:100%">
      <div class="res" id="result"></div>
    </div>
  </div>
</div>
<script>
const GAMES = /*DATA*/;
const NAMES = {K:'King',P:'Carp',T:'Tapir',R:'Raccoon',F:'Fox',O:'Koi',B:'Baku',N:'Tanuki',G:'Kitsune'};
const PROMO = new Set(['O','B','N','G']);
let gi=0, pi=0, timer=null;

const $ = id => document.getElementById(id);
const gsel=$('game');
GAMES.forEach((g,i)=>{ const o=document.createElement('option'); o.value=i;
  o.textContent=`${g.name}  —  ${g.result}  (${g.plies.length-1} plies)`; gsel.appendChild(o); });

function sqIndex(dst){ if(!dst) return -1; const c=dst.charCodeAt(0)-97, r=+dst[1]; return (4-r)*4 + c; }

function render(){
  const g=GAMES[gi], p=g.plies[pi];
  const hiDst = pi>0 ? sqIndex(p.dst) : -1;
  const b=$('board'); b.innerHTML='';
  for(let i=0;i<16;i++){
    const ch=p.cells[i], d=document.createElement('div'); d.className='sq'+(i===hiDst?' hi':'');
    const file='abcd'[i%4], rank=4-Math.floor(i/4);
    if(i%4===0||Math.floor(i/4)===3){ const co=document.createElement('span'); co.className='coord';
      co.textContent=(Math.floor(i/4)===3?file:'')+(i%4===0?rank:''); d.appendChild(co); }
    if(ch!=='.'){
      const up=ch.toUpperCase(), pc=document.createElement('span');
      pc.className='pc '+(ch===up?'w':'b')+(PROMO.has(up)?' promo':'');
      pc.innerHTML=up+'<small>'+NAMES[up]+(PROMO.has(up)?'+':'')+'</small>';
      d.appendChild(pc);
    }
    b.appendChild(d);
  }
  $('bhand').innerHTML='black hand: <b>'+(p.h2||'-')+'</b>';
  $('whand').innerHTML='white hand: <b>'+(p.h1||'-')+'</b>';
  $('eval').textContent = pi===0 ? 'start' : whiteEval(p);
  $('meta').innerHTML = pi===0 ? 'starting position'
    : `ply ${p.ply} · ${p.mover} · <b>${p.move}</b> · depth ${p.depth}`+(p.tag?`<span class="tag">${p.tag}</span>`:'');
  $('result').textContent = pi===g.plies.length-1 ? g.result : '';
  const sl=$('slider'); sl.max=g.plies.length-1; sl.value=pi;
  $('prev').disabled=$('first').disabled=(pi===0);
  $('next').disabled=$('last').disabled=(pi===g.plies.length-1);
}
function whiteEval(p){
  if(p.eval[0]==='(') return 'opening';
  const sign = p.mover==='White'?1:-1;
  if(p.eval[0]==='#'){ const n=parseInt(p.eval.slice(1))*sign;
    return n>0?`White mates #${n}`:`Black mates #${-n}`; }
  const cp=(parseFloat(p.eval)*sign);
  return (cp>=0?'+':'')+cp.toFixed(2);
}
function go(n){ const g=GAMES[gi]; pi=Math.max(0,Math.min(g.plies.length-1,n)); render(); }
function stop(){ if(timer){clearInterval(timer);timer=null;$('play').textContent='▶ play';} }
$('next').onclick=()=>go(pi+1); $('prev').onclick=()=>go(pi-1);
$('first').onclick=()=>go(0); $('last').onclick=()=>go(GAMES[gi].plies.length-1);
$('slider').oninput=e=>{stop();go(+e.target.value);};
$('game').onchange=e=>{stop();gi=+e.target.value;pi=0;render();};
$('play').onclick=()=>{ if(timer){stop();return;}
  $('play').textContent='⏸ pause';
  timer=setInterval(()=>{ if(pi>=GAMES[gi].plies.length-1){stop();return;} go(pi+1); },700); };
document.onkeydown=e=>{ if(e.key==='ArrowRight')go(pi+1); if(e.key==='ArrowLeft')go(pi-1); };
render();
</script>
</body></html>
"""

if __name__ == "__main__":
    main()
