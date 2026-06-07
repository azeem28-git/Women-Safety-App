# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to those specified
# in the Android SDK tools ProGuard files.

# Keep WebView from being stripped.
-keep class android.webkit.** { *; }
