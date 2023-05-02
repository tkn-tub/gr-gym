#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "gnuradio::gnuradio-gnugym" for configuration "Release"
set_property(TARGET gnuradio::gnuradio-gnugym APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(gnuradio::gnuradio-gnugym PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/x86_64-linux-gnu/libgnuradio-gnugym.so.v1.2-compat-xxx-xunknown"
  IMPORTED_SONAME_RELEASE "libgnuradio-gnugym.so.1.2.0git"
  )

list(APPEND _IMPORT_CHECK_TARGETS gnuradio::gnuradio-gnugym )
list(APPEND _IMPORT_CHECK_FILES_FOR_gnuradio::gnuradio-gnugym "${_IMPORT_PREFIX}/lib/x86_64-linux-gnu/libgnuradio-gnugym.so.v1.2-compat-xxx-xunknown" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
