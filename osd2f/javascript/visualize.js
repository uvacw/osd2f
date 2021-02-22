"use strict"

// Placeholder visualization
export function visualize(d){
    d.forEach(appendFile);
  }

function appendFile(fileobj){
    document.getElementById("files")
    .innerHTML += `<p>${fileobj.filename} : <b> ${fileobj.entries.length} </b> datapoints</p>`
  }