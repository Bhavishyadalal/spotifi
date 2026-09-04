[app]
title = Spotifi
package.name = spotifi
package.domain = org.spotifi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

# Fixed: pyjnius -> jnius, added android explicitly
requirements = python3,kivy==2.3.0,jnius,android

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 26

# Fixed: 25b -> 25c (25b has known arm64 build issues)
android.ndk = 25c

android.sdk = 33
android.accept_sdk_license = True

android.arch = arm64-v8a

android.enable_androidx = True

# Speed up builds — only build for one arch
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
