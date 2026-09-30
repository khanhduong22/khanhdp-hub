/**
 * Copyright 2018 Google Inc. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// If the loader is already loaded, just stop.
if (!self.define) {
  let registry = {};

  // Used for `eval` and `importScripts` where we can't get script URL by other means.
  // In both cases, it's safe to use a global var because those functions are synchronous.
  let nextDefineUri;

  const singleRequire = (uri, parentUri) => {
    uri = new URL(uri + ".js", parentUri).href;
    return registry[uri] || (
      
        new Promise(resolve => {
          if ("document" in self) {
            const script = document.createElement("script");
            script.src = uri;
            script.onload = resolve;
            document.head.appendChild(script);
          } else {
            nextDefineUri = uri;
            importScripts(uri);
            resolve();
          }
        })
      
      .then(() => {
        let promise = registry[uri];
        if (!promise) {
          throw new Error(`Module ${uri} didn’t register its module`);
        }
        return promise;
      })
    );
  };

  self.define = (depsNames, factory) => {
    const uri = nextDefineUri || ("document" in self ? document.currentScript.src : "") || location.href;
    if (registry[uri]) {
      // Module is already loading or loaded.
      return;
    }
    let exports = {};
    const require = depUri => singleRequire(depUri, uri);
    const specialDeps = {
      module: { uri },
      exports,
      require
    };
    registry[uri] = Promise.all(depsNames.map(
      depName => specialDeps[depName] || require(depName)
    )).then(deps => {
      factory(...deps);
      return exports;
    });
  };
}
define(['./workbox-7e5eb42b'], (function (workbox) { 'use strict';

  self.skipWaiting();
  workbox.clientsClaim();
  /**
   * The precacheAndRoute() method efficiently caches and responds to
   * requests for URLs in the manifest.
   * See https://goo.gl/S9QRab
   */
  workbox.precacheAndRoute([{
    "url": "registerSW.js",
    "revision": "402b66900e731ca748771b6fc5e7a068"
  }, {
    "url": "manifest.json",
    "revision": "ad3778a194e48b171f28317343083b5d"
  }, {
    "url": "index.html",
    "revision": "fe053244bb8b8caba637ed5fbf4df76e"
  }, {
    "url": "icons/icon.svg",
    "revision": "5b8b096b2096256148b31ec4de5ea2fc"
  }, {
    "url": "assets/vendor-react-B9rM_PBI.js",
    "revision": null
  }, {
    "url": "assets/vendor-DRcGonlY.js",
    "revision": null
  }, {
    "url": "assets/index-D8BF8zP-.css",
    "revision": null
  }, {
    "url": "assets/index-BVpQ2PwS.js",
    "revision": null
  }, {
    "url": "assets/icons-B5TW5SaK.js",
    "revision": null
  }, {
    "url": "assets/StoresPage-1x1l3M0_.js",
    "revision": null
  }, {
    "url": "assets/OrderTrackingPage-C_QTI6Ds.js",
    "revision": null
  }, {
    "url": "assets/LocationPickerModal-DUQ3qWlq.js",
    "revision": null
  }, {
    "url": "assets/KitchenPage-C_uoiL8x.js",
    "revision": null
  }, {
    "url": "assets/K80ReceiptModal-YDW7yCEW.js",
    "revision": null
  }, {
    "url": "assets/HomePage-DZcE42tv.js",
    "revision": null
  }, {
    "url": "assets/CheckoutPage-CACHOVH1.js",
    "revision": null
  }, {
    "url": "assets/AccountPage-DvxbQw44.js",
    "revision": null
  }, {
    "url": "icons/icon.svg",
    "revision": "5b8b096b2096256148b31ec4de5ea2fc"
  }, {
    "url": "manifest.webmanifest",
    "revision": "eac423917a2c18e1424146eb0fac847e"
  }], {});
  workbox.cleanupOutdatedCaches();
  workbox.registerRoute(new workbox.NavigationRoute(workbox.createHandlerBoundToURL("index.html")));

}));
