// This is the javascript to handle folder loading &
// client-side filtering

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
const key_rest_split = function(p){
    let key
    sa = p.split(".")
    key = sa.shift(1)
    return [key, sa.join('.')]
  }

const objReader = function(spec, o, prev){
  
    let flat_obj = {}

    let options = spec.map(p=> p.split(".").shift(1))

    
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
    if ( typeof in_key !== 'undefined' ){
        return fileReader(paths, objects[in_key], prepath)
    }

    // in case the contents is just one array of values,
    // instead of an array of values
    if (Array.isArray(objects) && paths==""){
      return [{"entries":objects}]
    }

    // extract the whitelisted paths from all objects
    // in the array contained in the file
    return objects.map(obj => objReader(paths, obj))

}

// 3. controller
const fileLoadController = async function(settings, files){
    // we map filenames to the regex format filenames in
    // provided settings
    console.log("files:", files)
    setmatch = Object.fromEntries(
      files.map(file => {
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
    

    acceptedFiles = files.filter(f => setmatch[f.name]!==undefined)

    let output = [];

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
                    content = String.fromCharCode.apply(null, new Uint8Array(r))
                    console.log(e)
                    done = true
                  })
                  wait = 1000
                  while (!done || wait>0){
                    await sleep(100)
                    wait -= 100
                  }
                }
                fileob = new Object;
                fileob[f.name] = fileReader(
                  paths=settings['files'][setmatch[f.name]].fields, 
                  objects=JSON.parse(content),
                  prepath=null,
                  in_key = settings['files'][setmatch[f.name]].in_key
                  )
                output.push(fileob);
                }
            
        );
    bar = document.getElementById("progress-bar");
    while (output.length < acceptedFiles.length){
      pos = (output.length / acceptedFiles.length) *100

      if (pos!==bar.value){
        bar.value = pos 
      }
      await sleep(500);
    }
    bar.value = 100;
    
    console.log("output is: ",output)
}

// as per https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
function sleep(ms){
  return new Promise(resolve => setTimeout(resolve, ms))
}