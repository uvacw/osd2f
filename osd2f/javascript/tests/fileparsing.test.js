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