objparsing = require("../parsing/objparsing")


test("Parsing simple data", () => {
    simple_data = {
        "key": 1,
        "nested":
        {
            "key": 2
        },
        "nested_obj": {
            "sub1": 1,
            "sub2_ignored": 2
        },
        "nested_array": [
            {
                "array_obj": 3,
                "array_obj_ignored": 3
            }
        ]
    }

    simple_spec = {
        fields: [
            "key",
            "nested.key",
            "nested_obj.sub1",
            "nested_array.array_obj",
            "nonexisting_field"
        ]
    }

    // do the parsing
    r = objparsing.objReader(simple_spec.fields, simple_data)

    // check whether specified and existing fields are recoverd
    expect(r.key).toBe(1)
    expect(r["nested.key"]).toBe(2)
    expect(r["nested_obj.sub1"]).toBe(1)
    expect(r.nested_array[0].array_obj).toBe(3)

    // check whether specified but missing fields are ignored
    expect(r.nonexisting_field).toBe(undefined)

    // check whether ignored files are indeed ignored
    expect(r["nested_obj.sub2_ignored"]).toBe(undefined)
    expect(r.nested_array[0].array_obj_ignored).toBe(undefined)

})

test("Empty nested array which is a parent key should not show up as it's own witelisted field", () => {
    data = {
        key: []
    }

    spec = {
        fields: ["key.subfield"]
    }

    r = objparsing.objReader(spec.fields, data)

    expect(r.key).toBe(undefined)

})