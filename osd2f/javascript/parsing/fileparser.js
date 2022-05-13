const { objReader } = require("./objparsing")
var jp = require("jsonpath")

// fileReader selects the starting point for recursive parsing
// for each object in the file and returns the resulting objects.
const fileReader = function (paths, objects, prepath, in_key) {
    // in case the data is nested in an object
    // rather than an array
    if (typeof in_key !== 'undefined' && in_key !== null) {

        var jsonPathSpec = '$["' + in_key + '"].*'
        var nested_objects = jp.query(objects, jsonPathSpec)

        return fileReader(paths, nested_objects, in_key, undefined)

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