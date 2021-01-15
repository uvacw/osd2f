var mobj = {
    title : "complex object",
    notitle: "hoting",
    data : [
      {"a_field": "for you", "another_field":"also great"},
      {"a_field": "not for you", "third_field":"huh"}
    ],
    ndata : {
      direct : "direct value",
      subs : 
          [{"a_field":"in sub array", "third_field":"a charm"}]
    }
  }
  
  spec = [
    "title",
    "ndata.direct",
    "ndata.subs.a_field",
    "data.a_field"
  ]
  
  var key_rest_split = function(p){
      let key
      sa = p.split(".")
      key = sa.shift(1)
      return [key, sa.join('.')]
    }
  
  var flat = function(spec, o, prev){
  
    let flat_obj = {}
    
    let options = spec.map(p=> p.split(".").shift(1))
    
    for (k of Object.keys(o)){
      if (options.filter(o=>o==k).length==0){
        console.log(k)
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
        console.log("is array: ", k )
        flat_obj[newkey] = val.map(
          c => flat(sub_spec, c)
        )
        continue
      } 
      
      if (typeof val == "object" && val != null ) { 
        
        flat_obj = Object.assign(
          flat_obj, 
          flat(sub_spec, val, k)
          )
        continue 
      }
      
      console.log("value", val)
      flat_obj[newkey] = val 
    }
    return flat_obj
  }
  
  flat(spec, mobj)
  