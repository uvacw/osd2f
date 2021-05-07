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
