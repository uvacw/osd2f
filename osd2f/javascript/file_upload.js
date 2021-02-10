// This is the javascript to handle folder loading &
// client-side filtering
"use strict"
import {sleep} from "./utils.js"
export {sleep as sleep} from "./utils"


// 1. submit handlers
const folderScanner = function(webkitEntry, files){
    if (webkitEntry.isDirectory){
        let dir = webkitEntry.createReader();
        dir.readEntries( entries => 
            entries.forEach(
                entry =>  folderScanner(entry, files)
            )
        );
    } else {
        
        files.push(webkitEntry)
    }
};

// 2. file-reader
const objReader = function(spec, o, prev){
  
    let flat_obj = {}

    let options = spec.map(p=> p.split(".").shift(1))

    let k
    for (k of Object.keys(o)){
      if (options.filter(o=>o==k).length==0){
        continue
      }
      let newkey = [prev,k]
        .filter(e=>typeof e != "undefined")
        .join(".")
      
      let val = o[k]
      let sub_spec = spec
        .filter(s => s.startsWith(k))
        .map(s => s.substring(k.length+1, s.length))
      
      if (Array.isArray(val)){
        
        flat_obj[newkey] = val.map(
          c => objReader(sub_spec, c)
        )
        continue
      } 
      
      if (typeof val == "object" && val != null ) { 
        
        flat_obj = Object.assign(
          flat_obj, 
          objReader(sub_spec, val, k)
          )
        continue 
      }
      
      flat_obj[newkey] = val 
    }
    return flat_obj
  }

const fileReader = function(paths, objects, prepath, in_key){
    // in case the data is nested in an object
    // rather than an array
    if ( typeof in_key !== 'undefined' && in_key!==null){
        return fileReader(paths, objects[in_key], prepath)
    }

    // in case the contents is just one array of values,
    // instead of an array of objects
    if (Array.isArray(objects) && paths.length==0){
      return [{"entries":objects}]
    }

    // extract the whitelisted paths from all objects
    // in the array contained in the file
    return objects.map(obj => objReader(paths, obj))

}

// 3. controller
export const fileLoadController = async function(sid, settings, files, callback){
    document.getElementById("processing").classList.remove("invisible")
    // we map filenames to the regex format filenames in
    // provided settings
    var setmatch
    setmatch = Object.fromEntries(
      files.map(file => {
        let nameRegex
        for (nameRegex of Object.keys(settings.files)){
          if (RegExp(nameRegex).exec(file.name)){
            return [file.name, nameRegex]
          };
        }
        return [];
      })
    )
    // remove undefined keys, i.e. files that do not match any RegEx
    Object.keys(setmatch).map(k=> {if (k==="undefined") {delete setmatch[k]}})
    
    let acceptedFiles
    acceptedFiles = files.filter(f => setmatch[f.name]!==undefined)

    let data = [];

    acceptedFiles.map(
        async f => {
                let content
                // normal files
                if (f.text != null){
                  content = await f.text()
                } 
                // files from archive
                else {
                  let done = false
                  f.readData((r,e)=>{
                    let t
                    t = new TextDecoder()
                    content = t.decode(r)
                    console.log(e)
                    done = true
                  })
                  
                  let wait = 10000
                  while (!done && wait>0){
                    await sleep(100)
                    wait -= 100
                  }
                }

                let fileob
                fileob = new Object();
                fileob["filename"] = f.name;
                fileob["submission_id"] = sid;
                try {
                  fileob["entries"] = fileReader(
                    settings['files'][setmatch[f.name]].accepted_fields, 
                    JSON.parse(content),
                    null,
                    settings['files'][setmatch[f.name]].in_key
                    )
                  data.push(fileob);
                } catch (error) {
                  // log failed files, for instance OSX metadata
                  // files.
                  console.log("Invalid JSON file:",f.name)
                  console.log(error)
                  data.push(false)
                }
                }
            
        );
    let bar
    bar = document.getElementById("progress-bar");
    while (data.length < acceptedFiles.length){
      let pos
      pos = (data.length / acceptedFiles.length) *100

      if (pos!==bar.value){
        bar.value = pos 
      }
      await sleep(500);
    }

    // filter failed files
    data = data.filter(x=>x)
    
    bar.value = 100;

    // Finally, we submit the filtered submission data to
    // the server for more complex anonymization (WITHOUT STORING)
    fetch(
      "/anonymize", 
    {
      method: "POST",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    }
    ).then(response => {
      document.getElementById("processing").classList.add("invisible");
      return response.json()
    })
    .then(filtered => {callback(filtered)
    })
    .catch((error)=>{console.log("Error",error)})
}

