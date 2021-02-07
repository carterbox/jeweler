// This module is a modified version of the code in the appendix of:
// Karim, S., J. Sawada, Z. Alamgir, and S. M. Husnine. 2013. “Generating
// Bracelets with Fixed Content.” Theoretical Computer Science 475: 103–12.
// https://doi.org/10.1016/j.tcs.2012.11.024.

#include <stdio.h>
#include <vector>

#include "bracelet.hxx"

#define TRUE 1
#define FALSE 0
#define NECK 1
#define LYN 0

#define MAX_LENGTH 64

int a[MAX_LENGTH], run[MAX_LENGTH];

/*-----------------------------------------------------------*/

typedef struct cell {
  int next, prev;
} cell;

class List {
cell avail[MAX_LENGTH];

public:
int head;

  List(int k) {
    for (int j = k + 1; j >= 0; j--) {
      avail[j].next = j - 1;
      avail[j].prev = j + 1;
    }
    head = k;
  }

  void remove(int i) {
  int p, n;

  if (i == head)
    head = avail[i].next;
  p = avail[i].prev;
  n = avail[i].next;
  avail[p].next = n;
  avail[n].prev = p;
}

  void add(int i, const int k) {
  int p, n;

  p = avail[i].prev;
  n = avail[i].next;
  avail[n].prev = i;
  avail[p].next = i;
  if (avail[i].prev == k + 1)
    head = i;
}

  int next(int i) { return avail[i].next; }
};

/*-----------------------------------------------------------*/

void Print(int p, const int n, std::vector<std::vector<int>> &wrist) {
  int j;
  if (NECK && n % p != 0)
    return;
  if (LYN && n != p)
    return;
  std::vector<int> bracelet(n);
  for (j = 1; j <= n; j++) {
    bracelet[j - 1] = a[j] - 1;
  }
  wrist.push_back(bracelet);
}

/*-----------------------------------------------------------*/

typedef struct element {
  int s, v;
} element;
element B[MAX_LENGTH]; // run length encoding data structure
int nb = 0;            // number of blocks

void UpdateRunLength(int v) {
  if (B[nb].s == v)
    B[nb].v = B[nb].v + 1;
  else {
    nb++;
    B[nb].v = 1;
    B[nb].s = v;
  }
}

void RestoreRunLength() {
  if (B[nb].v == 1)
    nb--;
  else
    B[nb].v = B[nb].v - 1;
}

/*---------------------------------------------------------------------*/
// return -1 if reverse smaller, 0 if equal, and 1 if reverse is larger
/*---------------------------------------------------------------------*/

int CheckRev() {
  int j;
  j = 1;
  while (B[j].v == B[nb - j + 1].v && B[j].s == B[nb - j + 1].s && j <= nb / 2)
    j++;
  if (j > nb / 2)
    return 0;
  if (B[j].s < B[nb - j + 1].s)
    return 1;
  if (B[j].s > B[nb - j + 1].s)
    return -1;
  if (B[j].v < B[nb - j + 1].v && B[j + 1].s < B[nb - j + 1].s)
    return 1;
  if (B[j].v > B[nb - j + 1].v && B[j].s < B[nb - j].s)
    return 1;
  return -1;
}

/*-----------------------------------------------------------*/
// necklace is lexigraphic minimal rotation of equivalence class
// prenecklace any prefix of a necklace
// Lyndon word an aperiodic necklace

void Gen(int t, // t = len(a[]) + 1
         int p, // length of longest Lyndon prefix of a[]
         int r, int z,
         int b, // add this color to the end of a[]
         int RS,
         const int n, // length of fixed-content; Lyndon word when p == n
         const int k, // number of possible colors
         int *num, std::vector<std::vector<int>> &wrist, List &list) {
  int j, z2, p2, c;
  // Incremental comparison of a[r+1...n] with its reversal
  if (t - 1 > (n - r) / 2 + r) {
    if (a[t - 1] > a[n - t + 2 + r])
      RS = FALSE;
    else if (a[t - 1] < a[n - t + 2 + r])
      RS = TRUE;
  }
  // Termination condition - only characters k remain to be appended
  if (num[k] == n - t + 1) {
    if (num[k] > run[t - p])
      p = n;
    if (num[k] > 0 && t != r + 1 && B[b + 1].s == k && B[b + 1].v > num[k])
      RS = TRUE;
    if (num[k] > 0 && t != r + 1 && (B[b + 1].s != k || B[b + 1].v < num[k]))
      RS = FALSE;
    if (RS == FALSE)
      Print(p, n, wrist);
  }
  // Recursively extend the prenecklace - unless only 0s remain to be appended
  else if (num[1] != n - t + 1) {
    j = list.head;
    while (j >= a[t - p]) {
      run[z] = t - z;
      UpdateRunLength(j);
      num[j]--;
      if (num[j] == 0)
        list.remove(j);
      a[t] = j;
      z2 = z;
      if (j != k)
        z2 = t + 1;
      p2 = p;
      if (j != a[t - p])
        p2 = t;
      c = CheckRev();
      if (c == 0)
        Gen(t + 1, p2, t, z2, nb, FALSE, n, k, num, wrist, list);
      if (c == 1)
        Gen(t + 1, p2, r, z2, b, RS, n, k, num, wrist, list);
      if (num[j] == 0)
        list.add(j, k);
      num[j]++;
      RestoreRunLength();
      j = list.next(j);
    }
    a[t] = k;
  }
}

/*-----------------------------------------------------------*/

std::vector<std::vector<int>>
BraceletFC(const int n, // the length of the bracelet
           const int k, // the number of unique colors
           int *num     // the number of each color; start filling at 1
) {
  int j;
  List list = List(k);
  for (j = 1; j <= n; j++) {
    a[j] = k;
    run[j] = 0;
  }
  a[1] = 1;
  num[1]--;
  if (num[1] == 0)
    list.remove(1);
  B[0].s = 0;
  UpdateRunLength(1);
  std::vector<std::vector<int>> wrist;
  Gen(2, 1, 1, 2, 1, FALSE, n, k, num, wrist, list);
  wrist.shrink_to_fit();
  return wrist;
}

int main() {
  int n, k;
  int num[MAX_LENGTH];
  printf("Enter n (bracelet length) k (number of colors): ");
  if (scanf("%d %d", &n, &k) != 2)
    return 1;
  for (int j = 1; j <= k; j++) {
    printf(" enter # of %d’s: ", j - 1);
    if (scanf("%d", &num[j]) != 1)
      return 1;
  }
  auto wrist = BraceletFC(n, k, num);
  for (int i = 0; i < wrist.size(); i++) {
    for (int j = 0; j < n; j++) {
      printf("%d ", wrist[i][j]);
    }
    printf("\n");
  }
  printf("Total = %zu\n", wrist.size());
}
