"use strict"
// as per https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
export function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms))
  }

// Data could be too big for sessionStorage (>10mb)
// so instead, we park it into a private variable
// accessible via the Donation class 
var donation
export class Donation {

  SetData(data){
    donation = data;
  }
  GetRaw(){
    return JSON.stringify(donation)
  }
  GetObj(){
    return null
  }
}