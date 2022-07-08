const { fileReader } = require("../parsing/fileparser")

test("test array of objects file", () => {
    json_content = [
        {
            "key": "value"
        },
        {
            "key": "value2"
        }
    ]

    spec = {
        fields: ["key"]
    }

    parsed = fileReader(spec.fields, json_content)

    expect(parsed[0].key).toBe("value")
    expect(parsed[1].key).toBe("value2")

})

test("test array of objects nested in key", () => {
    json_content = {
        "main_key": [
            { "name": "obj1" },
            { "name": "obj2" }
        ]
    }


    spec = {
        in_key: "main_key",
        fields: ["name"]
    }

    parsed = fileReader(spec.fields, json_content, undefined, spec.in_key)

    expect(parsed[0].name).toBe("obj1")
    expect(parsed[1].name).toBe("obj2")

})

test("test object with array of values file", () => {
    json_content = {
        "main_key": [
            "value1",
            "value2",
            "value3"
        ]
    }

    spec = {
        in_key: "main_key"
    }

    parsed = fileReader([], json_content, undefined, spec.in_key)

    expect(parsed[0].index).toBe(0)
    expect(parsed[0].value).toBe("value1")

    expect(parsed[1].index).toBe(1)
    expect(parsed[1].value).toBe("value2")

    expect(parsed[2].index).toBe(2)
    expect(parsed[2].value).toBe("value3")

})

test("test file with '.' in main_key", () => {
    json_content = {
        "main.key": [
            { name: "obj1" },
            { name: "obj2" }
        ]
    }

    spec = {
        in_key: "main.key",
        fields: ["name"]
    }

    parsed = fileReader(spec.fields, json_content, undefined, spec.in_key)

    expect(parsed[0].name).toBe("obj1")
    expect(parsed[1].name).toBe("obj2")

})

test("test file with array of values obj", () => {
    json_content = [
        {
            "keywords": ["keyword A", "keyword B"]
        }
    ]

    spec = {
        fields: ["keywords"]
    }

    parsed = fileReader(spec.fields, json_content)

    expect(parsed[0].keywords.length).toBe(2)
    expect(parsed[0].keywords[0]).toBe("keyword A")
    expect(parsed[0].keywords[1]).toBe("keyword B")
})

test("test file with heavily nested values", () => {
    json_content = { "window.YTD.stuff": [{ "one": { "two": { "three": [{ "nested": "obj" }] } } }, { "one": { "two": { "three": [{ "nested": "obj_two" }] } } }] }

    spec = {
        in_key: "window.YTD.stuff",
        fields: ["one.two.three"]
    }

    parsed = fileReader(spec.fields, json_content, undefined, spec.in_key)

    expect(parsed[0]["one.two.three"][0].nested).toBe("obj")
    expect(Array.isArray(parsed)).toBe(true)
})

test("fields that result in object value", () => {
    json_content = { "window.YTD.stuff": [{ "one": { "two": { "three": [{ "nested": "obj" }] } } }, { "one": { "two": { "three": [{ "nested": "obj_two" }] } } }] }

    spec = {
        in_key: "window.YTD.stuff",
        fields: ["one.two"]
    }

    parsed = fileReader(spec.fields, json_content, undefined, spec.in_key)

    console.log(parsed)
    expect(Array.isArray(parsed[0]["one.two"].three)).toBe(true)
})