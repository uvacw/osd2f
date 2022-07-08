// objReader recursively parses JSON objects to extract
// the whitelisted fields and returns a flattened representation.
const objReader = function (spec, o, prev) {
    let flat_obj = {}

    let options = spec.map(p => p.split('.').shift(1))

    // if the object is the endpoint of a spec, 
    if (prev !== undefined && (spec.length === 0 || spec[0] === "")) {
        flat_obj[prev] = o
        return flat_obj
    }

    let k
    for (k of Object.keys(o)) {
        if (options.filter(o => o == k).length == 0) {
            continue
        }
        let newkey = [prev, k].filter(e => typeof e != 'undefined').join('.')

        let val = o[k]
        let sub_spec = spec
            .filter(s => s.startsWith(k + "."))
            .map(s => s.substring(k.length + 1, s.length))

        if (Array.isArray(val)) {
            if (sub_spec == "") {
                flat_obj[newkey] = val
                continue
            }

            var ac
            ac = val.map(c => objReader(sub_spec, c))

            // only append array values if they are not empty
            if (ac.length > 0) {
                flat_obj[newkey] = ac
            }
            continue
        }

        if (typeof val == 'object' && val != null) {
            flat_obj = Object.assign(flat_obj, objReader(sub_spec, val, newkey))

            continue
        }


        flat_obj[newkey] = val
    }


    return flat_obj
}

module.exports.objReader = objReader