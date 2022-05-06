const { objReader } = require("./objparsing")

// fileReader selects the starting point for recursive parsing
// for each object in the file and returns the resulting objects.
const fileReader = function (paths, objects, prepath, in_key) {
    // in case the data is nested in an object
    // rather than an array
    if (typeof in_key !== 'undefined' && in_key !== null) {
        // If this is a nested key (using '.' notation, e.g. "level1key.level2key")
        if (in_key.search("\\.") > 0) {
            let key_array = in_key.split(".")
            in_key = key_array.shift(1)
            let next_key = key_array.join(".")

            // if there is already a prepath
            if (typeof prepath !== undefined || prepath !== null) {
                return fileReader(paths, objects[in_key], prepath + "." + in_key, next_key)
            }
            return fileReader(paths, objects[in_key], in_key, next_key)
        }
        return fileReader(paths, objects[in_key], prepath)
    }

    if (Array.isArray(objects)) {
        // in case the contents is just one array of values,
        // instead of an array of objects
        if (paths.length == 0) {
            let entries = []
            let i = 0
            while (i < objects.length) {
                entries.push({
                    index: i,
                    value: objects[i]
                })
                i++
            }
            return entries
        } else {
            // extract the whitelisted paths from all objects
            // in the array contained in the file
            return objects.map(obj => objReader(paths, obj))
        }
    }

    // If the objects is actually one object (not an array)
    return [objReader(paths, objects)]
}

module.exports.fileReader = fileReader