"use strict"
import {Donation} from "./utils"

// for use áfter local filtering of fields
// allows for advanced server-side anonymization
export async function apply_adv_anonymization(fileobj){
    fileobj = await fetch(
        "/adv_anonymize_file", 
      {
        method: "POST",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(fileobj)
      }
      ).then(response => {
        return response.json()
      }).catch(response => console.log(response.error ))
      
    
    return fileobj.data
}


function donate(){
  document.getElementById("donatespinner").classList.remove("invisible")
  // disabled button for further donations
  document.getElementById("donatebutton").classList.add("disabled");
  document.getElementById("donatebutton").setAttribute("disabled", true)

  fetch(
  "/upload", 
{
  method: "POST",
  mode: "same-origin",
  credentials: "same-origin",
  headers: {
    "Content-Type": "application/json"
  },
  body: Donation.prototype.GetRaw()
}
).then(() => {
  // remove processing queue
  document.getElementById("donatespinner").classList.add("invisible");
  document.getElementById("thankyou").classList.remove("invisible");
  noDonationYet = false;
})
.catch((error)=>{console.log("Error",error)})
}

document.getElementById("donatebutton").addEventListener("click",donate)
