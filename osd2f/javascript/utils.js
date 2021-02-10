"use strict"
// as per https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
export function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms))
  }