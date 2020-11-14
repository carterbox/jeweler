#pragma once

#include <vector>

std::vector<std::vector<int>>
BraceletFC(const int n, // the length of the bracelet
           const int k, // the number of unique colors
           int *num     // the number of each color; start filling at 1
);
