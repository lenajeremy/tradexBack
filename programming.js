function vowelsAndConsonants(s) {
  let vowels = ['a', 'e', 'i', 'o', 'u']
  for (let alphabet of s){
      vowels.indexOf(alphabet) != -1 ? console.log(alphabet) : '';
  }
  for(let alphabel of s){
      vowels.indexOf(alphabel) === -1 ? console.log(alphabel) : '';
  }
}

console.log(vowelsAndConsonants('abcdefghijklmnopqrstuvwxyz'));