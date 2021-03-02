// This is the javascript to handle folder loading &
// client-side filtering
'use strict'
import { Archive } from 'libarchive.js'
import { apply_adv_anonymization } from './server_interaction'
import { readDb, readJson } from './read_file'
import { visualize } from './visualize'
import { getFilesFromDataTransferItems } from 'datatransfer-files-promise'

export { visualize as vis } from './visualize'

Archive.init({ workerUrl: '/static/js/libarchive/worker-bundle.js' })

// (NOTE to Bob: Is this actually still used?)
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
  
  for (const f of acceptedFiles) {
    const setting = settings["files"][setmatch[f.name]];
    
    // parse data according to file_type in YAML (default is JSON)
    let entries;
    if (setting.file_type === "db") {
      entries = await readDb(f, setting)
        .then((entries) => entries)
        .catch((e) => console.log("Could not parse DB: " + e.message));
    } else {
      // default is JSON
      entries = await readJson(f, setting)
        .then((entries) => entries)
        .catch((e) => console.log("Could not parse JSON: " + e.message));
    }

    if (entries) {
      let fileob = new Object();
      fileob["filename"] = f.name;
      fileob["submission_id"] = sid;
      fileob["entries"] = entries;
      fileob["n_deleted"] = 0;
      fileob = await apply_adv_anonymization(fileob);
      data.push(fileob);
    }

    console.log(data);
    // update the loading
    let pos;
    pos = (data.length / acceptedFiles.length) * 100;

    if (pos !== bar.value) {
      bar.value = pos;
    }
  }

  // filter failed files
  data = data.filter(x => x)

  // show users that processing has completed
  bar.value = 100
  document.getElementById('processing').classList.add('invisible')

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
