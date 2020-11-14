#include <algorithm>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

#include "bracelet.hxx"

using namespace pybind11::literals;

PYBIND11_MODULE(bracelet, m) {
  m.doc() = "Provides functions to generate combinatoric bracelets.";

  m.def(
      "bracelet_fc",
      [](int n, int k, const std::vector<int> &counts) {
        int *num = new int[n + 1];
        int total = 0;
        for (int i = 0; i < k; i++) {
          if (counts[i] <= 0) {
            throw std::invalid_argument(
                "All counts must be greater than zero.");
          }
          total += counts[i];
          num[i + 1] = counts[i];
        }
        if (total != n) {
          throw std::invalid_argument("The sum of counts must be n.");
        }
        auto bracelets = BraceletFC(n, k, num);
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
