// A DOM small enough to run the build board's script, plus a no-op setInterval
// so the page's stamp refresher does not keep the process alive.
//
// The board has no test suite, and a parse check does not catch the defects it
// actually ships. A comma dropped inside a nested array still parses, and a
// sentence that renders perfectly can still say something false. So the check
// is to execute the script and read what it produced.
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
  addEventListener: function(){} };
var setInterval = function(){ return 0; };
