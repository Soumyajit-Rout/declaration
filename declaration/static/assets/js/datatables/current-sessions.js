/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else {
		var a = factory();
		for(var i in a) (typeof exports === 'object' ? exports : root)[i] = a[i];
	}
})(self, function() {
return /******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./src/app/datatables/current-sessions.js":
/*!************************************************!*\
  !*** ./src/app/datatables/current-sessions.js ***!
  \************************************************/
/***/ (function() {

eval("function _typeof(o) { \"@babel/helpers - typeof\"; return _typeof = \"function\" == typeof Symbol && \"symbol\" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && \"function\" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? \"symbol\" : typeof o; }, _typeof(o); }\nfunction _classCallCheck(a, n) { if (!(a instanceof n)) throw new TypeError(\"Cannot call a class as a function\"); }\nfunction _defineProperties(e, r) { for (var t = 0; t < r.length; t++) { var o = r[t]; o.enumerable = o.enumerable || !1, o.configurable = !0, \"value\" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o); } }\nfunction _createClass(e, r, t) { return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, \"prototype\", { writable: !1 }), e; }\nfunction _toPropertyKey(t) { var i = _toPrimitive(t, \"string\"); return \"symbol\" == _typeof(i) ? i : i + \"\"; }\nfunction _toPrimitive(t, r) { if (\"object\" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || \"default\"); if (\"object\" != _typeof(i)) return i; throw new TypeError(\"@@toPrimitive must return a primitive value.\"); } return (\"string\" === r ? String : Number)(t); }\nvar DataTableManager = /*#__PURE__*/function () {\n  function DataTableManager(tableElement, apiUrl) {\n    _classCallCheck(this, DataTableManager);\n    this.tableElement = tableElement;\n    this.apiUrl = apiUrl;\n    this.dataTableOptions = this.createDataTableOptions();\n    this.dataTable = new KTDataTable(tableElement, this.dataTableOptions);\n    this.filterMap = this.createFilterMap();\n  }\n  return _createClass(DataTableManager, [{\n    key: \"createDataTableOptions\",\n    value:\n    /**\n     * Creates the options for the DataTable.\n     *\n     * @return {Object} The options for the DataTable.\n     */\n    function createDataTableOptions() {\n      return {\n        apiEndpoint: this.apiUrl,\n        pageSize: 10,\n        columns: {\n          select: {\n            render: function render(item, data, context) {\n              var checkbox = document.createElement('input');\n              checkbox.className = 'checkbox checkbox-sm';\n              checkbox.type = 'checkbox';\n              checkbox.value = data.id.toString();\n              checkbox.setAttribute('data-datatable-row-check', 'true');\n              return checkbox.outerHTML.trim();\n            }\n          },\n          user: {\n            title: 'Person',\n            render: function render(item) {\n              var prefix = DataTableManager.isLocalhost() ? 'metronic-tailwind-html' : 'metronic/tailwind';\n              return \"\\n              <div class=\\\"flex items-center gap-2.5\\\">\\n                <div class=\\\"shrink-0\\\">\\n                  <img class=\\\"h-9 rounded-full\\\" src=\\\"/static/\".concat(prefix, \"/dist/assets/media/avatars/\").concat(item.avatar, \"\\\">\\n                </div>\\n                <a class=\\\"leading-none font-semibold text-gray-900 hover:text-primary\\\" href=\\\"#\\\">\\n                  \").concat(item.name, \"\\n                </a>\\n              </div>\\n            \");\n            }\n          },\n          browser: {\n            title: 'Browser',\n            render: function render(item) {\n              return \"\\n              <div class=\\\"flex items-center gap-2\\\">\\n                <i class=\\\"ki-outline ki-chrome text-gray-700 text-lg\\\"></i>\\n                <span class=\\\"text-gray-700\\\">\".concat(item.name, \"</span>\\n              </div>\\n            \");\n            }\n          },\n          ipAddress: {\n            title: 'IP Address'\n          },\n          location: {\n            title: 'Location',\n            render: function render(item) {\n              var prefix = DataTableManager.isLocalhost() ? 'metronic-tailwind-html' : 'metronic/tailwind';\n              return \"\\n              <div class=\\\"flex items-center gap-1.5\\\">\\n                <img alt=\\\"flag\\\" class=\\\"h-4 rounded-full\\\" src=\\\"/static/\".concat(prefix, \"/dist/assets/media/flags/\").concat(item.flag, \"\\\">\\n                <span class=\\\"leading-none text-gray-700\\\">\").concat(item.name, \"</span>\\n              </div>\\n            \");\n            }\n          },\n          action: {\n            title: '',\n            render: function render(item) {\n              return \"\\n              <button class=\\\"btn btn-icon btn-light btn-clear btn-sm\\\">\\n                <i class=\\\"ki-outline ki-dots-vertical\\\"></i>\\n              </button>\\n            \";\n            },\n            createdCell: function createdCell(cell, cellData, rowData) {\n              cell.querySelector('.btn').addEventListener('click', function () {\n                alert(\"Clicked on action button for row \".concat(rowData.user.name));\n              });\n            }\n          }\n        }\n      };\n    }\n\n    /**\n     * Creates a map of filter elements based on the data-datatable-filter-column attribute.\n     *\n     * @return {Map<string, HTMLSelectElement>} A map of filter elements, where the key is the value of the data-datatable-filter-column attribute and the value is the corresponding HTMLSelectElement.\n     */\n  }, {\n    key: \"createFilterMap\",\n    value: function createFilterMap() {\n      var filterElements = document.querySelectorAll('select[data-datatable-filter-column]');\n      return new Map(Array.from(filterElements).map(function (el) {\n        return [el.getAttribute('data-datatable-filter-column'), el];\n      }));\n    }\n\n    /**\n     * Initialize the filters based on the state and map the filter elements to their corresponding datatable columns.\n     */\n  }, {\n    key: \"initializeFilters\",\n    value: function initializeFilters() {\n      var _this = this;\n      this.dataTable.getState().filters.forEach(function (_ref) {\n        var column = _ref.column,\n          value = _ref.value;\n        if (_this.filterMap.has(column)) {\n          var filterEl = _this.filterMap.get(column);\n          if (filterEl !== null) {\n            filterEl.value = value || '';\n          }\n        }\n      });\n      this.filterMap.forEach(function (el, column) {\n        el.addEventListener('change', function () {\n          _this.dataTable.setFilter({\n            column: column,\n            type: 'text',\n            value: el.value || ''\n          }).redraw();\n        });\n      });\n    }\n\n    /**\n     * A debounced function that delays invoking the input function until after wait milliseconds have elapsed since the last time the debounced function is invoked.\n     *\n     * @param {Function} func - The function to debounce.\n     * @param {number} wait - The number of milliseconds to delay.\n     * @return {Function} The debounced function.\n     */\n  }, {\n    key: \"debounce\",\n    value: function debounce(func, wait) {\n      var timeout;\n      return function () {\n        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {\n          args[_key] = arguments[_key];\n        }\n        var context = this;\n        clearTimeout(timeout);\n        timeout = setTimeout(function () {\n          return func.apply(context, args);\n        }, wait);\n      };\n    }\n\n    /**\n     * Initializes the search functionality for the current table.\n     * It sets up a debounced search event listener on the search element\n     * to perform a search on the datatable whenever the user types in the search input.\n     *\n     * @return {void}\n     */\n  }, {\n    key: \"initSearch\",\n    value: function initSearch() {\n      var _this2 = this;\n      var searchElement = document.querySelector('[data-datatable-search=\"true\"]');\n      if (this.dataTable && searchElement) {\n        var debouncedSearch = this.debounce(function () {\n          _this2.dataTable.search(searchElement.value);\n        }, 300);\n        searchElement.addEventListener('keyup', debouncedSearch);\n      }\n    }\n\n    /**\n     * Creates a new instance of DataTableManager with the specified tableElement and apiUrl.\n     * Initializes filters and search functionality for the instance.\n     *\n     * @param {void}\n     * @return {void}\n     */\n  }], [{\n    key: \"isLocalhost\",\n    value: function isLocalhost() {\n      return /^(localhost|127.0.0.1)$/.test(window.location.hostname);\n    }\n  }, {\n    key: \"createInstance\",\n    value: function createInstance() {\n      var apiUrl = DataTableManager.isLocalhost() ? 'http://127.0.0.1:8001/metronic-tailwind-html/demo1/account/security/current-sessions/_data.html' : 'https://keenthemes.com/metronic/tailwind/demo1/account/security/current-sessions/_data.html';\n      var tableElement = document.querySelector('#current_sessions_table');\n      var dataTableManager = new DataTableManager(tableElement, apiUrl);\n      dataTableManager.initializeFilters();\n      dataTableManager.initSearch();\n    }\n  }]);\n}();\nKTDom.ready(function () {\n  DataTableManager.createInstance();\n});\n\n//# sourceURL=webpack://metronic-tailwind-html/./src/app/datatables/current-sessions.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./src/app/datatables/current-sessions.js"]();
/******/ 	
/******/ 	return __webpack_exports__;
/******/ })()
;
});