add_library(cbracelet STATIC bracelet.cxx)
set_target_properties(cbracelet PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)
