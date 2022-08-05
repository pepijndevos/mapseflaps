# mapseflaps
A GPS mapping application for the SHA2017 badge, and possibly other platfroms

Requires https://github.com/badgeteam/ESP32-platform-firmware/pull/246 on the SHA badge to be able to draw PNGs without using a 32kb buffer.

Tiles:

* generated with https://github.com/openmaptiles/openmaptiles
* served with https://github.com/pepijndevos/microtileserver-gl
* styled with https://github.com/openmaptiles/maptiler-toner-gl-style

In order to make tileserver-gl render the toner style, you need to edit `style.json` to insert a valid API key for `glyphs` and use
```json
  "sources": {
    "openmaptiles": {
      "type": "vector",
      "url": "mbtiles://{v3}"
    }
  },
```

By running `node . --verbose` you can see the default config file. Save it  as `config.json` and change it to point to the toner style.