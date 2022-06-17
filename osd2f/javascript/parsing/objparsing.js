// objReader recursively parses JSON objects to extract
// the whitelisted fields and returns a flattened representation.
const objReader = function (spec, o, prev) {
    let flat_obj = {}

    let options = spec.map(p => p.split('.').shift(1))

    // if the object is the endpoint of a spec, 
    if (Array.isArray(spec) && spec.length === 1 && spec[0] === "") {
        return o
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

            flat_obj[newkey] = val.map(c => objReader(sub_spec, c))
            continue
        }

        if (typeof val == 'object' && val != null) {
            flat_obj = Object.assign(flat_obj, objReader(sub_spec, val, k))

            continue
        }

        flat_obj[newkey] = val
    }

    return flat_obj
}

module.exports.objReader = objReader