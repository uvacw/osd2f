'use strict'

import initSqlJs from 'sql.js'


export async function readJson(f, setting) {
    let content;
    // normal files
    if (f.text != null) {
      content = await f.text();
    } else {
      let extractedFile = await f.extract();
      content = await extractedFile.text();
    }
  
    return fileReader(
      setting.accepted_fields,
      JSON.parse(content),
      null,
      setting.in_key
    );
  }


export async function readDb(f, setting) {
    const config = { locateFile: (filename) => `static/js/${filename}` };
  
    let sqlQuery = "";
    for (const accepted_field of setting.accepted_fields) {
      if (sqlQuery === "") sqlQuery += "SELECT " + accepted_field;
      else sqlQuery += ", " + accepted_field;
    }
    sqlQuery += " from " + setting.in_key + ";";
  
    const SQL = await initSqlJs(config);
  
    let jsondata = new Promise((resolve, reject) => {
      let r = new FileReader();
      r.onload = function () {
        const Uints = new Uint8Array(r.result);
        const db = new SQL.Database(Uints);
        try {
          const dbq = db.prepare(sqlQuery);
          const jsondata = [];
          while (dbq.step()) jsondata.push(dbq.getAsObject());
          resolve(jsondata);
        } catch (e) {
          reject(e);
        }
      };
      r.readAsArrayBuffer(f);
    });
  
    return jsondata;
  }


  // used in readJson
  const fileReader = function (paths, objects, prepath, in_key) {
    // in case the data is nested in an object
    // rather than an array
    if (typeof in_key !== 'undefined' && in_key !== null) {
      return fileReader(paths, objects[in_key], prepath)
    }
  
    // in case the contents is just one array of values,
    // instead of an array of objects
    if (Array.isArray(objects) && paths.length == 0) {
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
    }
  
    // extract the whitelisted paths from all objects
    // in the array contained in the file
    return objects.map(obj => objReader(paths, obj))
  }

  // used in readJson -> fileReader
  const objReader = function (spec, o, prev) {
    let flat_obj = {}
  
    let options = spec.map(p => p.split('.').shift(1))
  
    let k
    for (k of Object.keys(o)) {
      if (options.filter(o => o == k).length == 0) {
        continue
      }
      let newkey = [prev, k].filter(e => typeof e != 'undefined').join('.')
  
      let val = o[k]
      let sub_spec = spec
        .filter(s => s.startsWith(k))
        .map(s => s.substring(k.length + 1, s.length))
  
      if (Array.isArray(val)) {
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
  
  