const fs = require('fs')

let calcEntropyForFile = (file) => {
    let freq = {}
    let freqCond = {}
    
    for (let i = 0; i < file.length; i++) {
        if (i === 0) {
            freqCond[file[i]] = {0: 1}
        } else {
            freqCond[file[i]] === undefined ? freqCond[file[i]] = {[file[i-1]]: 1} : freqCond[file[i]][file[i-1]] === undefined ? freqCond[file[i]][file[i-1]] = 1 : freqCond[file[i]][file[i-1]] += 1
        }
        freq[file[i]] === undefined ? freq[file[i]] = 1 : freq[file[i]] += 1
    }
    
    let entropy = Object.keys(freq).map(key => freq[key] * ((-1)*(Math.log2(freq[key]) - Math.log2(file.length)))).reduce((a, b) => a+b, 0)/file.length
    console.log('Entropy:', entropy) 
    
    let condEntropy = Object.keys(freq).map(x => {
        return Object.keys(freqCond).map(y => {
            let res = (freqCond[y][x] * ((-1)*(Math.log2(freqCond[y][x]) - Math.log2(freq[x]))))
            return Number.isNaN(res) ? 0 : res
        }).reduce((a, b) => a+b, 0)
    }).reduce((a, b) => a+b, 0)/file.length
    console.log('Conditional entropy:', condEntropy)
}

let tests = [fs.readFileSync('pan-tadeusz-czyli-ostatni-zajazd-na-litwie.txt'), fs.readFileSync('test1.bin'), fs.readFileSync('test2.bin'), fs.readFileSync('test3.bin')]
tests.forEach(test => calcEntropyForFile(test))