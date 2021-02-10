/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
window.file_upload =
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./osd2f/javascript/file_upload.js":
/*!*****************************************!*\
  !*** ./osd2f/javascript/file_upload.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"sleep\": () => (/* reexport safe */ _utils_js__WEBPACK_IMPORTED_MODULE_0__.sleep),\n/* harmony export */   \"fileLoadController\": () => (/* binding */ fileLoadController)\n/* harmony export */ });\n/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./utils */ \"./osd2f/javascript/utils.js\");\n// This is the javascript to handle folder loading &\n// client-side filtering\n\n;\n\n\n\n// 1. submit handlers\nconst folderScanner = function(webkitEntry, files){\n    if (webkitEntry.isDirectory){\n        let dir = webkitEntry.createReader();\n        dir.readEntries( entries => \n            entries.forEach(\n                entry =>  folderScanner(entry, files)\n            )\n        );\n    } else {\n        \n        files.push(webkitEntry)\n    }\n};\n\n// 2. file-reader\nconst objReader = function(spec, o, prev){\n  \n    let flat_obj = {}\n\n    let options = spec.map(p=> p.split(\".\").shift(1))\n\n    let k\n    for (k of Object.keys(o)){\n      if (options.filter(o=>o==k).length==0){\n        continue\n      }\n      let newkey = [prev,k]\n        .filter(e=>typeof e != \"undefined\")\n        .join(\".\")\n      \n      let val = o[k]\n      let sub_spec = spec\n        .filter(s => s.startsWith(k))\n        .map(s => s.substring(k.length+1, s.length))\n      \n      if (Array.isArray(val)){\n        \n        flat_obj[newkey] = val.map(\n          c => objReader(sub_spec, c)\n        )\n        continue\n      } \n      \n      if (typeof val == \"object\" && val != null ) { \n        \n        flat_obj = Object.assign(\n          flat_obj, \n          objReader(sub_spec, val, k)\n          )\n        continue \n      }\n      \n      flat_obj[newkey] = val \n    }\n    return flat_obj\n  }\n\nconst fileReader = function(paths, objects, prepath, in_key){\n    // in case the data is nested in an object\n    // rather than an array\n    if ( typeof in_key !== 'undefined' && in_key!==null){\n        return fileReader(paths, objects[in_key], prepath)\n    }\n\n    // in case the contents is just one array of values,\n    // instead of an array of objects\n    if (Array.isArray(objects) && paths.length==0){\n      return [{\"entries\":objects}]\n    }\n\n    // extract the whitelisted paths from all objects\n    // in the array contained in the file\n    return objects.map(obj => objReader(paths, obj))\n\n}\n\n// 3. controller\nconst fileLoadController = async function(sid, settings, files, callback){\n    document.getElementById(\"processing\").classList.remove(\"invisible\")\n    // we map filenames to the regex format filenames in\n    // provided settings\n    var setmatch\n    setmatch = Object.fromEntries(\n      files.map(file => {\n        let nameRegex\n        for (nameRegex of Object.keys(settings.files)){\n          if (RegExp(nameRegex).exec(file.name)){\n            return [file.name, nameRegex]\n          };\n        }\n        return [];\n      })\n    )\n    // remove undefined keys, i.e. files that do not match any RegEx\n    Object.keys(setmatch).map(k=> {if (k===\"undefined\") {delete setmatch[k]}})\n    \n    let acceptedFiles\n    acceptedFiles = files.filter(f => setmatch[f.name]!==undefined)\n\n    let data = [];\n\n    acceptedFiles.map(\n        async f => {\n                let content\n                // normal files\n                if (f.text != null){\n                  content = await f.text()\n                } \n                // files from archive\n                else {\n                  let done = false\n                  f.readData((r,e)=>{\n                    let t\n                    t = new TextDecoder()\n                    content = t.decode(r)\n                    console.log(e)\n                    done = true\n                  })\n                  \n                  let wait = 10000\n                  while (!done && wait>0){\n                    await (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.sleep)(100)\n                    wait -= 100\n                  }\n                }\n\n                let fileob\n                fileob = new Object();\n                fileob[\"filename\"] = f.name;\n                fileob[\"submission_id\"] = sid;\n                try {\n                  fileob[\"entries\"] = fileReader(\n                    settings['files'][setmatch[f.name]].accepted_fields, \n                    JSON.parse(content),\n                    null,\n                    settings['files'][setmatch[f.name]].in_key\n                    )\n                  data.push(fileob);\n                } catch (error) {\n                  // log failed files, for instance OSX metadata\n                  // files.\n                  console.log(\"Invalid JSON file:\",f.name)\n                  console.log(error)\n                  data.push(false)\n                }\n                }\n            \n        );\n    let bar\n    bar = document.getElementById(\"progress-bar\");\n    while (data.length < acceptedFiles.length){\n      let pos\n      pos = (data.length / acceptedFiles.length) *100\n\n      if (pos!==bar.value){\n        bar.value = pos \n      }\n      await (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.sleep)(500);\n    }\n\n    // filter failed files\n    data = data.filter(x=>x)\n    \n    bar.value = 100;\n\n    // Finally, we submit the filtered submission data to\n    // the server for more complex anonymization (WITHOUT STORING)\n    fetch(\n      \"/anonymize\", \n    {\n      method: \"POST\",\n      mode: \"same-origin\",\n      credentials: \"same-origin\",\n      headers: {\n        \"Content-Type\": \"application/json\"\n      },\n      body: JSON.stringify(data)\n    }\n    ).then(response => {\n      document.getElementById(\"processing\").classList.add(\"invisible\");\n      return response.json()\n    })\n    .then(filtered => {callback(filtered)\n    })\n    .catch((error)=>{console.log(\"Error\",error)})\n}\n\n\n\n//# sourceURL=webpack://file_upload/./osd2f/javascript/file_upload.js?");

/***/ }),

/***/ "./osd2f/javascript/utils.js":
/*!***********************************!*\
  !*** ./osd2f/javascript/utils.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"sleep\": () => (/* binding */ sleep)\n/* harmony export */ });\n\n// as per https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep\nfunction sleep(ms){\n    return new Promise(resolve => setTimeout(resolve, ms))\n  }\n\n//# sourceURL=webpack://file_upload/./osd2f/javascript/utils.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		if(__webpack_module_cache__[moduleId]) {
/******/ 			return __webpack_module_cache__[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	// module exports must be returned from runtime so entry inlining is disabled
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__("./osd2f/javascript/file_upload.js");
/******/ })()
;