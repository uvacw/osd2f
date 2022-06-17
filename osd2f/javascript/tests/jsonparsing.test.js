const { ParseJSON } = require("../parsing/jsonparsing")

test("test regular JSON obj", () => {
    text_content = '{"content": [1, 2, 3]}'
    content = ParseJSON(text_content)

    expect(content.content.length).toBe(3)
    expect(content.content[0]).toBe(1)

})

test("test regular JSON array", () => {
    text_content = '[1,2,3]'
    content = ParseJSON(text_content)

    expect(content.length).toBe(3)
    expect(content[0]).toBe(1)
})

test("bad (twitter) JSON", () => {
    text_content = 'content = [ { "key" : "value" } ]'
    content = ParseJSON(text_content)
    console.log(content)
    expect(content.content[0].key).toBe("value")
})