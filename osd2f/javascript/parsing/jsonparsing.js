
// ParseJSON is a helper that is lenient for badly
// formatted json
const ParseJSON = function (text_content) {
    try {
        return JSON.parse(text_content)
    }
    catch {
        return parseTwitterJSON(text_content)
    }

}


// parseTwitterJSON parses malformed JSON delivered by Twitter
const parseTwitterJSON = function (text_content) {

    // assume it's the first, global, key that is malformed
    chunks = text_content.split("=")
    main_key = chunks.shift()
    body = chunks.join('=')

    // build it as proper JSON
    fixed_content = '{ "' + main_key.trim() + '" :' + body + '}'

    return JSON.parse(fixed_content)
}

module.exports.ParseJSON = ParseJSON