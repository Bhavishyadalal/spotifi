[app]
title = Spotifi
package.name = spotifi
package.domain = org.spotifi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

requirements = python3,kivy,pyjnius,android

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

android.arch = arm64-v8a

android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
