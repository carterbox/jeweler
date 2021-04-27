#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <stdexcept> // std::invalid_argument
#include <vector>

#include "bracelet.hxx"

using namespace pybind11::literals;

// Because both stl.h and stl_bind.h are included, explicitly list opaque types
PYBIND11_MAKE_OPAQUE(std::vector<std::vector<int>>);

PYBIND11_MODULE(bracelet, m) {
  // Creating an opaque type prevents copies from vector to Python List
  pybind11::bind_vector<std::vector<std::vector<int>>>(m, "VectorInt2D");
  m.doc() = "Provides functions to generate combinatoric bracelets.";
  m.def(
      "bracelet_fc",
      [](int n, int k, const std::vector<int> &counts) {
        int *num = new int[n + 1];
        int total = 0;
        for (int i = 0; i < k; i++) {
          if (counts[i] <= 0) {
            delete num;
            throw std::invalid_argument(
                "All counts must be greater than zero.");
          }
          total += counts[i];
          num[i + 1] = counts[i];
        }
        if (total != n) {
          delete num;
          throw std::invalid_argument("The sum of counts must be n.");
        }
        auto bracelets = BraceletFC(n, k, num);
        delete num;
        return bracelets;
      },
      R"(Return all bracelets of fixed content using method by Karim et al.

    Parameters
    ----------
    n : int
        The length of the bracelet.
    k : int
        The number of unique colors in the bracelet.
    counts : [int]
        The number of each unique color.

    Returns
    -------
    bracelets : [[int]]
      A list of the bracelets.

    References
    ----------
    Karim, S., J. Sawada, Z. Alamgir, and S. M. Husnine. 2013. “Generating
    Bracelets with Fixed Content.” Theoretical Computer Science 475: 103–12.
    https://doi.org/10.1016/j.tcs.2012.11.024.
)",
      "n"_a, "k"_a, "counts"_a);
}
