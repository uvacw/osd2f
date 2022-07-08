// This is the javascript to handle folder loading &
// client-side filtering
'use strict'
import 'blob-polyfill' // for safari File handling

import { Archive } from 'libarchive.js'
import { apply_adv_anonymization } from './server_interaction'
import { visualize } from './visualize'
import { getFilesFromDataTransferItems } from 'datatransfer-files-promise'
import { server } from './server_interaction'
import { fileReader } from './parsing/fileparser'
import { ParseJSON } from './parsing/jsonparsing'

export { visualize as vis } from './visualize'
export { server } from './server_interaction'

server.log('INFO', 'loaded js')

// loads the zipfile reading WASM libraries
Archive.init({ workerUrl: '/static/js/libarchive/worker-bundle.js' })

server.log('INFO', 'initialized archive worker')

// folderScanner handles folder uploads.
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

// reparseAsUTF8 stringifies an object, parses the string as UTF8
// and returns the JSON parsed result. This removes issues with
// UTF-8 donations, that JS assumes are UTF-16. 
const reparseAsUTF8 = function (object) {
  // drawn from https://stackoverflow.com/questions/52747566/what-encoding-facebook-uses-in-json-files-from-data-export
  function decode(s) {
    let d = new TextDecoder;
    let a = s.split('').map(r => r.charCodeAt());
    return d.decode(new Uint8Array(a));
  }

  let stringObj = JSON.stringify(object)


  let decodedString = decode(stringObj)

  // check whether translation did not introduce bad characters
  // that signal it was already UTF-16, in which case we return
  // the original, supposedly UTF16 object
  if (decodedString.search("�") > 0) {
    return object
  }

  // return the UTF8->UTF16 decoded object instead
  return JSON.parse(decodedString)
}

// countFileTypes takes a list of filenames and
// counts the lowercased extensions
function countFileTypes(arr) {
  let counts = new Object
  arr.
    map(e => e.split(".").pop().toLowerCase()).
    map(ext => counts[ext] = counts[ext] + 1 || 1)
  return counts
}

// fileLoadController checks whether files are in the whitelist, 
// and parses these files using the fileReader and the appropriate
// whitelist of fields for that particular file. 
export const fileLoadController = async function (sid, settings, files) {
  document.getElementById("empty_selection").classList.add("d-none")
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

  // log the count of selected files, the count of files
  // matching the whitelist and a frequency table of the
  // filetypes selected.
  server.log("INFO", "files selected", sid,
    {
      "selected": files.length,
      "matching_whitelist": acceptedFiles.length,
      "types": countFileTypes(files.map(f => f.name))
    })

  if (files.length > 0 && acceptedFiles.length == 0) {
    document.getElementById("empty_selection").classList.remove("d-none")
    server.log("ERROR", "empty selection", sid)
  }

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
        ParseJSON(content), // custom to support malformed
        null,
        settings['files'][setmatch[f.name]].in_key
      )
      server.log('INFO', 'reparsing file to UTF8')
      try {
        fileob = reparseAsUTF8(fileob)
      } catch {
        server.log("INFO", "file could not be reparsed, might be UTF16 already", window.sid)
      }

      server.log('INFO', 'file send to anonymization', sid, {
        file_match: setmatch[f.name]
      })
      fileob = await apply_adv_anonymization(fileob)
      server.log('INFO', 'file anonymized', sid, {
        file_match: setmatch[f.name]
      })
      data.push(fileob)
    } catch (e) {
      console.log(e)
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

// fileSelectHandler is used to detect files uploaded through
// the file select prompt.
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

// fileDropHandler is used to detect files uploaded using 
// the drag-and-drop interface.
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
