find_package(pybind11)

pybind11_add_module(bracelet bracelet.cxx)
target_link_libraries(bracelet PRIVATE cbracelet)
install(TARGETS bracelet LIBRARY DESTINATION "jeweler")
