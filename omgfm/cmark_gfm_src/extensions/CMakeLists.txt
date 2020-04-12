cmake_minimum_required(VERSION 2.8)
set(LIBRARY "libcmark-gfm-extensions")
set(LIBRARY_SOURCES
    core-extensions.c
    table.c
    strikethrough.c
    autolink.c
    tagfilter.c
    ext_scanners.c
    ext_scanners.re
    ext_scanners.h
    tasklist.c
   )

include_directories(
  ${PROJECT_SOURCE_DIR}/src
  ${PROJECT_BINARY_DIR}/src
)

include (GenerateExportHeader)

include_directories(. ${CMAKE_CURRENT_BINARY_DIR})

set(CMAKE_C_FLAGS_PROFILE "${CMAKE_C_FLAGS_RELEASE} -pg")
set(CMAKE_LINKER_PROFILE "${CMAKE_LINKER_FLAGS_RELEASE} -pg")
add_compiler_export_flags()

add_library(${LIBRARY} SHARED ${LIBRARY_SOURCES})

set_target_properties(${LIBRARY} PROPERTIES
  OUTPUT_NAME "cmark-gfm-extensions"
  SOVERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}.gfm.${PROJECT_VERSION_GFM}
  VERSION ${PROJECT_VERSION})

set_property(TARGET ${LIBRARY}
  APPEND PROPERTY MACOSX_RPATH true)

generate_export_header(${LIBRARY}
  BASE_NAME cmark-gfm-extensions)

list(APPEND CMARK_INSTALL ${LIBRARY})
target_link_libraries(${LIBRARY} libcmark-gfm)


set(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_NO_WARNINGS ON)

include (InstallRequiredSystemLibraries)
install(TARGETS ${CMARK_INSTALL}
  EXPORT cmark-gfm-extensions
  LIBRARY DESTINATION lib${LIB_SUFFIX}
  )

install(FILES
  cmark-gfm-core-extensions.h
  ${CMAKE_CURRENT_BINARY_DIR}/cmark-gfm-extensions_export.h
  DESTINATION include
  )

install(EXPORT cmark-gfm-extensions DESTINATION lib${LIB_SUFFIX}/cmake-gfm-extensions)


