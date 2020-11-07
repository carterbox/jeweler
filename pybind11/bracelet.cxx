#include <algorithm>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

#include "bracelet.h"

PYBIND11_MODULE(bracelet, m) {
  m.doc() = "Generates combinatoric bracelets of fixed content using the "
            "algorithm from Karim et al. (2012).\nKarim, S., "
            "J. Sawada, Z. Alamgir, and S. M. Husnine. 2013. “Generating "
            "Bracelets with Fixed Content.” Theoretical Computer Science 475: "
            "103–12. https://doi.org/10.1016/j.tcs.2012.11.024.";

  m.def(
      "bracelet_fc",
      [](int n, int k, const std::vector<int> &counts) {
        int num[64];
        std::copy(counts.begin(), counts.end(), num + 1);
        BraceletFC(n, k, num);
      },
      "Print all bracelets of fixed content.");
}
