add_library(cbracelet STATIC bracelet.c)
set_target_properties(cbracelet PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)
