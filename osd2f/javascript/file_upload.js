// This is the javascript to handle folder loading &
// client-side filtering
'use strict'
import 'blob-polyfill' // for safari File handling

import { Archive } from 'libarchive.js'
import { apply_adv_anonymization } from './server_interaction'
import { visualize } from './visualize'
import { getFilesFromDataTransferItems } from 'datatransfer-files-promise'
import { server } from './server_interaction'

export { visualize as vis } from './visualize'
export { server } from './server_interaction'

server.log('INFO', 'loaded js')

Archive.init({ workerUrl: '/static/js/libarchive/worker-bundle.js' })

server.log('INFO', 'initialized archive worker')

// 1. submit handlers
const folderScanner = function (webkitEntry, files) {
  if (webkitEntry.isDirectory) {
    let dir = webkitEntry.createReader()
    dir.readEntries(entries =>
      entries.forEach(entry => folderScanner(entry, files))
    )
  } else {
    files.push(webkitEntry)
  }
}

// 2. file-reader
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

    flat_obj[k] = val
  }

  return flat_obj
}

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

// 3. controller
export const fileLoadController = async function (sid, settings, files) {
  document.getElementById('processing').classList.remove('invisible')
  // we map filenames to the regex format filenames in
  // provided settings
  var setmatch
  setmatch = Object.fromEntries(
    files.map(file => {
      let nameRegex
      for (nameRegex of Object.keys(settings.files)) {
        if (RegExp(nameRegex).exec(file.name)) {
          return [file.name, nameRegex]
        }
      }
      return []
    })
  )
  // remove undefined keys, i.e. files that do not match any RegEx
  Object.keys(setmatch).map(k => {
    if (k === 'undefined') {
      delete setmatch[k]
    }
  })

  let acceptedFiles
  acceptedFiles = files.filter(f => setmatch[f.name] !== undefined)

  let data = []

  let bar = document.getElementById('progress-bar')
  bar.value = 0
  let f
  for (f of acceptedFiles) {
    let content
    // normal files
    if (f.text != null) {
      content = await f.text()
    } else {
      let extractedFile = await f.extract()
      content = await extractedFile.text()
    }
    let fileob
    fileob = new Object()
    fileob['filename'] = f.name
    fileob['submission_id'] = sid
    fileob['n_deleted'] = 0
    try {
      server.log('INFO', 'file parsing', window.sid, {
        file_match: setmatch[f.name]
      })
      fileob['entries'] = fileReader(
        settings['files'][setmatch[f.name]].accepted_fields,
        JSON.parse(content),
        null,
        settings['files'][setmatch[f.name]].in_key
      )
      server.log('INFO', 'file send to anonymization', sid, {
        file_match: setmatch[f.name]
      })
      fileob = await apply_adv_anonymization(fileob)
      server.log('INFO', 'file anonymized', sid, {
        file_match: setmatch[f.name]
      })
      data.push(fileob)
    } catch (e) {
      server.log('ERROR', 'file matched, but is not JSON', sid)
      console.log("Unable to parse file because it's not real JSON")
    }

    // update the loading
    let pos
    pos = (data.length / acceptedFiles.length) * 100

    if (pos !== bar.value) {
      bar.value = pos
    }
  }

  // filter failed files
  data = data.filter(x => x)

  // show users that processing has completed
  bar.value = 100
  document.getElementById('processing').classList.add('invisible')

  server.log('INFO', 'starting visualization', sid)
  visualize(data, content)
}

export async function fileSelectHandler(e) {
  server.log('INFO', 'file select detected', sid)
  var filesSelected = e.target.files
  if (filesSelected === undefined) {
    server.log('INFO', 'file select empty', sid)
    return // no files selected yet
  }

  // if there is one file, which is an archive
  if (RegExp('.*.zip$').exec(filesSelected[0].name) != null) {
    server.log('INFO', 'file select is archive', sid)

    let archiveContent = await Archive.open(filesSelected[0])
    let contentList = await archiveContent.getFilesArray()
    let fl = contentList.map(c => c.file)

    fileLoadController(sid, settings, fl)
  } else {
    server.log('INFO', 'file select is single file', sid)

    fileLoadController(sid, settings, Array(filesSelected[0]))
  }
}
document.getElementById('fileElem').onchange = fileSelectHandler

async function fileDropHandler(e) {
  server.log('INFO', 'file drop detected', sid)

  let filesSelected = await getFilesFromDataTransferItems(e.dataTransfer.items)

  // if there is one file, which is an archive
  if (
    filesSelected.length == 1 &&
    RegExp('.*.zip$').exec(filesSelected[0].name) != null
  ) {
    server.log('INFO', 'file drop is archive', sid)

    let archiveContent = await Archive.open(filesSelected[0])
    let contentList = await archiveContent.getFilesArray()
    let fl = contentList.map(c => c.file)

    fileLoadController(sid, settings, fl)
  } else {
    server.log('INFO', 'file drop is file(s)', sid)

    fileLoadController(sid, settings, filesSelected)
  }
}
document
  .getElementById('drop-area')
  .addEventListener('drop', fileDropHandler, false)
