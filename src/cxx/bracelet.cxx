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

// An ordered set of integers from largest to smallest
class LinkedList {

  int k;

  struct cell {
    int next, prev;
  };

  cell *avail;

public:
  int head; // the current highest number in the set

  // Create a set of integers for k-ary strings
  LinkedList(const int k) : k(k) {
    avail = new cell[k + 2];
    // Initialize the set as [0, 1, ... k, k + 1]
    for (int j = k + 1; j >= 0; j--) {
      avail[j].next = j - 1;
      avail[j].prev = j + 1;
    }
    head = k;
  }
  ~LinkedList() { delete[] avail; }
  // Remove color i from the list
  void remove(int i) {
    if (i == head)
      head = avail[i].next;
    int p = avail[i].prev;
    int n = avail[i].next;
    avail[p].next = n;
    avail[n].prev = p;
  }
  // Add the color i back to the list
  void add(int i) {
    int p = avail[i].prev;
    int n = avail[i].next;
    avail[n].prev = i;
    avail[p].next = i;
    if (avail[i].prev == k + 1)
      head = i;
  }
  // Get the next largest color in the set after i
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

// A compact representation of a k-ary string using a sequence of Blocks
class RunLength {

  // A k-ary string of a single color
  struct Block {
    int s; // the color of this string
    int v; // the length of this string
  };

public:
  Block *B;
  int nb = 0; // number of blocks

  // Initialize a RunLength of maximum length n
  RunLength(int n) {
    B = new Block[n + 1];
    B[0].s = 0;
  }
  ~RunLength() { delete[] B; }

  // Append a character of color v to the string
  void update(int v) {
    if (B[nb].s == v)
      ++B[nb].v;
    else {
      nb++;
      B[nb].v = 1;
      B[nb].s = v;
    }
  }
  // Remove the end character from the string
  void restore() {
    if (B[nb].v == 1)
      nb--;
    else
      --B[nb].v;
  }
  /*---------------------------------------------------------------------*/
  // return -1 if reverse smaller, 0 if equal, and 1 if reverse is larger
  /*---------------------------------------------------------------------*/
  int check_reversal() {
    int j = 1;
    while (B[j].v == B[nb - j + 1].v && B[j].s == B[nb - j + 1].s &&
           j <= nb / 2)
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
};

/*-----------------------------------------------------------*/
// necklace is lexigraphic minimal rotation of equivalence class
// prenecklace any prefix of a necklace
// Lyndon word an aperiodic necklace

void Gen(int t, // t = len(a[]) + 1
         int p, // length of longest Lyndon prefix of a[]
         int r, // length of longest mirror (reversal) prefix of a[]
         int z,
         int b, // The next color to append to a[]
         int RS,
         const int n, // length of fixed-content; Lyndon word when p == n
         const int k, // number of possible colors
         int *num, std::vector<std::vector<int>> &wrist, LinkedList &list,
         RunLength &run_length) {
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
    if (num[k] > 0 && t != r + 1 && run_length.B[b + 1].s == k &&
        run_length.B[b + 1].v > num[k])
      RS = TRUE;
    if (num[k] > 0 && t != r + 1 &&
        (run_length.B[b + 1].s != k || run_length.B[b + 1].v < num[k]))
      RS = FALSE;
    if (RS == FALSE)
      Print(p, n, wrist);
  }
  // Recursively extend the prenecklace - unless only 0s remain to be appended
  else if (num[1] != n - t + 1) {
    j = list.head;

    while (j >= a[t - p]) {
      run[z] = t - z;
      run_length.update(j);

      num[j]--;
      if (num[j] == 0)
        list.remove(j);

      a[t] = j;

      z2 = z;

      if (j != k)
        z2 = t + 1;

      if (j != a[t - p]) {
        p2 = t;
      } else {
        p2 = p;
      }

      switch (run_length.check_reversal()) {
      case 0:
        Gen(t + 1, p2, t, z2, run_length.nb, FALSE, n, k, num, wrist, list,
            run_length);
        break;
      case 1:
        Gen(t + 1, p2, r, z2, b, RS, n, k, num, wrist, list, run_length);
        break;
      }

      if (num[j] == 0)
        list.add(j);
      num[j]++;

      run_length.restore();

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
  LinkedList list = LinkedList(k);
  for (int j = 1; j <= n; j++) {
    a[j] = k; // Initialize a with k for optimization.
    run[j] = 0;
  }
  // Initialize with a1 = 1; all bracelets must start with 1
  a[1] = 1;
  num[1]--;
  if (num[1] == 0)
    list.remove(1);
  RunLength run_length = RunLength(n);
  run_length.update(1);

  std::vector<std::vector<int>> wrist;
  Gen(2, 1, 1, 2, 1, FALSE, n, k, num, wrist, list, run_length);
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
