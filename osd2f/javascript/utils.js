"use strict"
// as per https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
export function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms))
  }

export class Donation {

  getKey(){
    return "donations"
  }

  SetData(data){
    window.sessionStorage.setItem(this.getKey(), JSON.stringify(data))
  }
  GetRaw(){
    return window.sessionStorage.getItem(this.getKey())
  }
  GetObj(){
    let serialized = window.sessionStorage.getItem(this.getKey())
    if (serialized===null){
      return null
    }
    return JSON.parse(serialized)
  }
}