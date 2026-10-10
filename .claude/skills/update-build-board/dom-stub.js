// A DOM small enough to run the build board's script, plus a no-op setInterval
// so the page's stamp refresher does not keep the process alive.
//
// A parse check does not catch the defects the board actually ships. A comma
// dropped inside a nested array still parses, and a sentence that renders
// perfectly can still say something false. So the check is to execute the
// script and read what it produced. Two things run it on this stub: the
// skill's harness, against the data about to be written, and
// tests/test_build_board.py, which holds what the page draws with no data, an
// empty database, a partial one and a fixture board.
//
// This is plain ES5 and assumes nothing about its host, so any JavaScript engine
// runs it. Where none is installed, `osascript -l JavaScript` is JavaScriptCore
// and is already present on macOS. Every element the script asks for is created on demand and
// kept in `store`, so a harness appended after the script can read
// `store.<id>.innerHTML` for any id the page renders into.
var store = {};
function mkEl(id) {
  return { id: id, innerHTML: "", textContent: "",
    classList: { add: function(){}, remove: function(){}, toggle: function(){} },
    querySelectorAll: function(){ return []; },
    onclick: null, onkeydown: null };
}
var document = {
  getElementById: function(id){ if(!store[id]) store[id]=mkEl(id); return store[id]; },
  addEventListener: function(){},
  // The board redraws on every database write, and each redraw after the first
  // removes the Escape listener the previous one added. A stub without this
  // throws on the second render, which a page that drew only once never reached.
  removeEventListener: function(){} };
var setInterval = function(){ return 0; };
