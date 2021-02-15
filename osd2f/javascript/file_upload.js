// This is the javascript to handle folder loading &
// client-side filtering
'use strict'
import { Archive } from 'libarchive.js'
import { apply_adv_anonymization } from './server_interaction'
import { visualize } from './visualize'
import { Donation } from './utils'
import { getFilesFromDataTransferItems } from 'datatransfer-files-promise'

Archive.init({ workerUrl: '/static/js/libarchive/worker-bundle.js' })

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

const fileReader = function (paths, objects, prepath, in_key) {
  // in case the data is nested in an object
  // rather than an array
  if (typeof in_key !== 'undefined' && in_key !== null) {
    return fileReader(paths, objects[in_key], prepath)
  }

  // in case the contents is just one array of values,
  // instead of an array of objects
  if (Array.isArray(objects) && paths.length == 0) {
    return [{ entries: objects }]
  }

  // extract the whitelisted paths from all objects
  // in the array contained in the file
  return objects.map(obj => objReader(paths, obj))
}

// 3. controller
export const fileLoadController = async function (
  sid,
  settings,
  files,
  callback
) {
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
    try {
      fileob['entries'] = fileReader(
        settings['files'][setmatch[f.name]].accepted_fields,
        JSON.parse(content),
        null,
        settings['files'][setmatch[f.name]].in_key
      )
      fileob = await apply_adv_anonymization(fileob)
      data.push(fileob)
    } catch (e) {
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

  Donation.prototype.SetData(data)

  // show users that processing has completed
  bar.value = 100
  document.getElementById('processing').classList.add('invisible')
  document.getElementById('donatebutton').classList.remove('disabled')
  try {
    document
      .getElementById('donatebutton')
      .attributes.removeNamedItem('disabled')
  } catch {}

  visualize(data)
}

export async function fileSelectHandler (e) {
  var filesSelected = e.target.files
  if (filesSelected === undefined) {
    console.log('no files', e)
    return // no files selected yet
  }

  // if there is one file, which is an archive
  if (RegExp('.*.zip$').exec(filesSelected[0].name) != null) {
    let archiveContent = await Archive.open(filesSelected[0])
    let contentList = await archiveContent.getFilesArray()
    let fl = contentList.map(c => c.file)

    fileLoadController(sid, settings, fl)
  } else {
    fileLoadController(sid, settings, Array(filesSelected[0]))
  }
}
document.getElementById('fileElem').onchange = fileSelectHandler

async function fileDropHandler (e) {
  let filesSelected = await getFilesFromDataTransferItems(e.dataTransfer.items)

  // if there is one file, which is an archive
  if (
    filesSelected.length == 1 &&
    RegExp('.*.zip$').exec(filesSelected[0].name) != null
  ) {
    let archiveContent = await Archive.open(filesSelected[0])
    let contentList = await archiveContent.getFilesArray()
    let fl = contentList.map(c => c.file)

    fileLoadController(sid, settings, fl)
  } else {
    fileLoadController(sid, settings, filesSelected)
  }
}
document
  .getElementById('drop-area')
  .addEventListener('drop', fileDropHandler, false)
