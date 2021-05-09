'use strict'

// for use áfter local filtering of fields
// allows for advanced server-side anonymization
export async function apply_adv_anonymization (fileobj) {
  fileobj = await fetch('/adv_anonymize_file', {
    method: 'POST',
    mode: 'same-origin',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(fileobj)
  })
    .then(response => {
      return response.json()
    })
    .catch(response => console.log(response.error))

  return fileobj.data
}

export const server = {
  log: function (level, position, sid, entry) {
    let params = {
      level: level,
      position: position,
      cb: Math.random() // to avoid caching
    }
    if (sid != undefined) {
      params['sid'] = sid
    } else {
      if (window.sid != undefined) {
        params['sid'] = window.sid
      }
    }
    if (entry != undefined) {
      params['entry'] = JSON.stringify(entry)
    }

    fetch('/log?' + new URLSearchParams(params), {
      method: 'GET',
      mode: 'same-origin',
      credentials: 'same-origin'
    })
      .then(r => {})
      .catch(e => {
        console.log('Unable to log', level, position, 'due to', e)
      })
  }
}
