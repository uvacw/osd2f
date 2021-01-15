var data = {
    title : "hey title",
    timestamp: 12312321,
    flat_data : {flatnest1:"a", flatnest2:"b"},
      array_data : [
      {"nested_field1": "nested_value",
      "nested_field2": "nested_value2"}
    ]
  }
  
  var spec = ["title","flat_data.flatnest1", "array_data.nested_field1"]
  
  var datas = [data, data]
  
  
  const key_rest_split = function(path){
    sa = path.split(".")
    key = sa.shift(1)
      return key, sa.join('.')
  }
  
  const pathSelect = function(paths, obj, prepath){
    var flat_version = {}
    
    for (p of paths) {
      
      key, rest = key_rest_split(p)
      if ( rest.length==0 ){
       
        flat_version[[prepath,key].filter(i=>i!==undefined).join(".")] = obj[key]
      } else {
        console.log("key",key, typeof(obj[key]))
        children = obj[key]
        
        next_path = [prepath,key].filter(i=>i!==undefined).join(".")
        if (!Array.isArray(children)) {
            sub_flat_version = pathSelect(
              [rest], children, next_path
            )  
        } else {
          sub_flat_version = {}
          sub_flat_version[next_path] =children.map(child=>pathSelect([rest],child, key))
          console.log("nested:", sub_flat_version)
        }
        
        flat_version = Object.assign(flat_version, sub_flat_version)
      }
    }
    return flat_version
  }
  
  
  var d = pathSelect(spec,data)
  
  console.log(d)