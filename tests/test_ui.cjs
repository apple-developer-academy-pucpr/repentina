// Interaction regression checks using a small DOM adapter; no participant data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag='div') { this.tag=tag;this.children=[];this.events={};this.attributes={};this.value='';this.hidden=false;this.textContent=''; }
  append(child) { this.children.push(child); }
  replaceChildren() { this.children=[]; }
  setAttribute(key,value) { this.attributes[key]=value; }
  removeAttribute(key) { delete this.attributes[key]; }
  addEventListener(name,callback) { this.events[name]=callback; }
  focus() { this.events.focus?.(); }
  scrollIntoView() {}
  fire(name,key) { this.events[name]?.({key,preventDefault(){}}); }
}
const people=[
 {id:'1',name:'Ágata Exemplo',from:1,to:1},
 {id:'2',name:'Bruna Fictícia',from:1,to:2},
 {id:'3',name:'Caio Exemplo',from:2,to:1},
 {id:'4',name:'Daniel Fictício',from:2,to:2},
];
const template=fs.readFileSync(`${__dirname}/index.html`,'utf8');
assert.match(template,/<header>.*Apple Developer Academy.*class="event-name">Repentina<\/div><\/header>/);
assert.match(template,/<section class="hero" aria-labelledby="title">/);
assert.match(template,/\.badge\{[^}]*grid-column:3;[^}]*justify-self:end/);
assert.match(template,/header,main,footer\{width:calc\(100% - 64px\);max-width:1164px;margin-inline:auto/);
function setup(round=1){
 const nodes={};
 const document={getElementById(id){return nodes[id]??=new Element()},createElement(tag){return new Element(tag)}};
 const participants=people.map(p=>({...p,from:round?p.from:p.to}));
 const script=template.split('<script>')[1].split('</script>')[0].replace('/*__ROUND_DATA__*/null',JSON.stringify({round,teams:[1,2],participants}));
 vm.runInNewContext(script,{document});return nodes;
}
function text(node){return [node.textContent,...node.children.map(text)].join(' ')}
const n=setup();
assert.equal(n.round.textContent,'1ª Troca');
assert.equal(n.round.hidden,false);
assert.equal(n.teams.children.length,2);
const first=n.teams.children[0];
assert.match(text(first),/Quem sai.*Bruna Fictícia.*Quem entra.*Caio Exemplo.*Quem fica.*Ágata Exemplo/);
assert.doesNotMatch(text(first),/Daniel Fictício/);
n.search.value='agata';n.search.fire('input');
assert.equal(n.names.children.length,1);
assert.equal(n.names.children[0].textContent,'Ágata Exemplo');
assert.equal(n.search.attributes['aria-expanded'],'true');
assert.match(n.personal.textContent,/permanece no time 1/);
assert.match(text(n.teams),/Ágata Exemplo/);
n.search.fire('keydown','ArrowDown');
assert.equal(n.search.attributes['aria-activedescendant'],'suggestion-0');
n.search.fire('keydown','Enter');
assert.equal(n.search.value,'Ágata Exemplo');assert.equal(n.names.hidden,true);
n.search.value='exemplo';n.search.fire('input');
assert.equal(n.names.children.length,2);
n.search.fire('keydown','ArrowUp');assert.equal(n.search.attributes['aria-activedescendant'],'suggestion-1');
n.search.fire('keydown','Escape');assert.equal(n.names.hidden,true);
n.search.fire('focus');n.names.children[1].fire('click');
assert.equal(n.search.value,'Caio Exemplo');assert.equal(n.names.hidden,true);
assert.match(n.personal.textContent,/saia do time 2 e vá para o time 1/);
n.search.value='inexistente';n.search.fire('input');
assert.equal(n.names.hidden,true);assert.equal(n.empty.hidden,false);assert.equal(n.teams.children.length,0);
n.clear.fire('click');assert.equal(n.teams.children.length,2);assert.equal(n.names.hidden,true);
n.search.value='exemplo';n.search.fire('input');n.search.fire('keydown','Tab');assert.equal(n.names.hidden,true);
n.search.fire('focus');n.search.fire('blur');assert.equal(n.names.hidden,true);
const initial=setup(0);
assert.equal(initial.round.hidden,true);assert.equal(initial.round.textContent,'');
assert.equal(initial.title.textContent,'Encontre sua equipe');
assert.match(text(initial.teams),/Equipe/);
assert.doesNotMatch(text(initial.teams),/inicial|Quem fica|Quem sai|troca/i);
assert.doesNotMatch(initial.intro.textContent,/inicial|troca|rodada/i);
initial.search.value='agata';initial.search.fire('input');
assert.match(initial.personal.textContent,/sua equipe é a 1/);
for(const number of [1,2,3,4])assert.equal(setup(number).round.textContent,`${number}ª Troca`);
console.log('PASS: remaining members, accent search, keyboard and pointer selection, dismissal, empty results, reset, initial round');
module.exports={Element};
