if(${CMAKE_VERSION} VERSION_GREATER "3.3")
    cmake_policy(SET CMP0063 NEW)
endif()

include(GNUInstallDirs)

set(LIBRARY "libcmark-gfm")
set(HEADERS
  cmark-gfm.h
  cmark-gfm-extension_api.h
  parser.h
  buffer.h
  node.h
  iterator.h
  chunk.h
  references.h
  footnotes.h
  map.h
  utf8.h
  scanners.h
  inlines.h
  houdini.h
  cmark_ctype.h
  render.h
  registry.h
  syntax_extension.h
  plugin.h
  )
set(LIBRARY_SOURCES
  cmark.c
  node.c
  iterator.c
  blocks.c
  inlines.c
  scanners.c
  scanners.re
  utf8.c
  buffer.c
  references.c
  footnotes.c
  map.c
  render.c
  man.c
  xml.c
  html.c
  commonmark.c
  plaintext.c
  latex.c
  houdini_href_e.c
  houdini_html_e.c
  houdini_html_u.c
  cmark_ctype.c
  arena.c
  linked_list.c
  syntax_extension.c
  registry.c
  plugin.c
  ${HEADERS}
  )

include_directories(. ${CMAKE_CURRENT_BINARY_DIR})
include_directories(
  ${PROJECT_BINARY_DIR}/extensions
)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/cmark-gfm_version.h.in
  ${CMAKE_CURRENT_BINARY_DIR}/cmark-gfm_version.h)

include (GenerateExportHeader)

set(CMAKE_C_FLAGS_PROFILE "${CMAKE_C_FLAGS_RELEASE} -pg")
set(CMAKE_LINKER_PROFILE "${CMAKE_LINKER_FLAGS_RELEASE} -pg")

# -fvisibility=hidden
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN 1)


add_library(${LIBRARY} SHARED ${LIBRARY_SOURCES})
# Include minor version and patch level in soname for now.
set_target_properties(${LIBRARY} PROPERTIES
  OUTPUT_NAME "cmark-gfm"
  SOVERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}.gfm.${PROJECT_VERSION_GFM}
  VERSION ${PROJECT_VERSION})

set_property(TARGET ${LIBRARY}
  APPEND PROPERTY MACOSX_RPATH true)


generate_export_header(${LIBRARY}
  BASE_NAME ${PROJECT_NAME})

list(APPEND CMARK_INSTALL ${LIBRARY})


if(NOT MSVC OR CMAKE_HOST_SYSTEM_NAME STREQUAL Windows)
  set(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_NO_WARNINGS ON)
  include(InstallRequiredSystemLibraries)
endif()

set(libdir lib${LIB_SUFFIX})

install(TARGETS ${CMARK_INSTALL}
  EXPORT cmark-gfm
  LIBRARY DESTINATION ${libdir}
  )

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/libcmark-gfm.pc.in
  ${CMAKE_CURRENT_BINARY_DIR}/libcmark-gfm.pc @ONLY)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/libcmark-gfm.pc
  DESTINATION ${libdir}/pkgconfig)

install(FILES
  cmark-gfm.h
  cmark-gfm-extension_api.h
  ${CMAKE_CURRENT_BINARY_DIR}/cmark-gfm_export.h
  ${CMAKE_CURRENT_BINARY_DIR}/cmark-gfm_version.h
  DESTINATION include
  )

install(EXPORT cmark-gfm DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake)

# Feature tests
include(CheckIncludeFile)
include(CheckCSourceCompiles)
include(CheckCSourceRuns)
include(CheckSymbolExists)
CHECK_INCLUDE_FILE(stdbool.h HAVE_STDBOOL_H)
CHECK_C_SOURCE_COMPILES(
  "int main() { __builtin_expect(0,0); return 0; }"
  HAVE___BUILTIN_EXPECT)
CHECK_C_SOURCE_COMPILES("
  int f(void) __attribute__ (());
  int main() { return 0; }
" HAVE___ATTRIBUTE__)

CONFIGURE_FILE(
  ${CMAKE_CURRENT_SOURCE_DIR}/config.h.in
  ${CMAKE_CURRENT_BINARY_DIR}/config.h)




