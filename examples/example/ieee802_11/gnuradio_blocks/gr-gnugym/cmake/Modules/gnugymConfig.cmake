INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_GNUGYM gnugym)

FIND_PATH(
    GNUGYM_INCLUDE_DIRS
    NAMES gnugym/api.h
    HINTS $ENV{GNUGYM_DIR}/include
        ${PC_GNUGYM_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GNUGYM_LIBRARIES
    NAMES gnuradio-gnugym
    HINTS $ENV{GNUGYM_DIR}/lib
        ${PC_GNUGYM_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GNUGYM DEFAULT_MSG GNUGYM_LIBRARIES GNUGYM_INCLUDE_DIRS)
MARK_AS_ADVANCED(GNUGYM_LIBRARIES GNUGYM_INCLUDE_DIRS)

