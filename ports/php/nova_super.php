<?php

function argsort_stable($b){
  $n = count($b);
  $idx = array();
  for ($i = 0; $i < $n; $i++) {
    $idx[] = $i;
  }
  usort($idx, function($i, $j) use ($b) {
    if ($b[$i] != $b[$j]) {
      return $b[$i] <=> $b[$j];
    }
    return $i <=> $j;
  });
  return $idx;
}

function nova_super($a){
  $n = count($a);
  if ($n <= 1) {
    return array_values($a);
  }
  if ($n < 32) {
    $arr = array_values($a);
    $m = count($arr);
    for ($i = 1; $i < $m; $i++) {
      $v = $arr[$i];
      $j = $i - 1;
      while ($j >= 0 && $arr[$j] > $v) {
        $arr[$j + 1] = $arr[$j];
        $j--;
      }
      $arr[$j + 1] = $v;
    }
    return $arr;
  }
  $arr = array_values($a);
  $minv = $arr[0];
  $maxv = $arr[0];
  for ($i = 1; $i < $n; $i++) {
    if ($arr[$i] < $minv) $minv = $arr[$i];
    if ($arr[$i] > $maxv) $maxv = $arr[$i];
  }
  $r = $maxv - $minv + 1;
  $limitCount = max(65536, $n);
  if ($r >= 1 && $r <= $limitCount) {
    $cnt = array_fill(0, $r, 0);
    for ($i = 0; $i < $n; $i++) {
      $k = $arr[$i] - $minv;
      $cnt[$k]++;
    }
    $out = array();
    for ($i = 0; $i < $r; $i++) {
      $val = $minv + $i;
      $c = $cnt[$i];
      for ($j = 0; $j < $c; $j++) {
        $out[] = $val;
      }
    }
    return $out;
  }
  $voff = array();
  for ($i = 0; $i < $n; $i++) {
    $voff[] = $arr[$i] - $minv;
  }
  // low
  $d0 = array();
  for ($i = 0; $i < $n; $i++) {
    $d0[] = $voff[$i] & 0xFFFF;
  }
  $idx0 = argsort_stable($d0);
  $v1 = array();
  for ($i = 0; $i < $n; $i++) {
    $v1[] = $voff[$idx0[$i]];
  }
  // high
  $d1 = array();
  for ($i = 0; $i < $n; $i++) {
    $d1[] = ($v1[$i] >> 16) & 0xFFFF;
  }
  $idx1 = argsort_stable($d1);
  $out1 = array();
  for ($i = 0; $i < $n; $i++) {
    $out1[] = $v1[$idx1[$i]] + $minv;
  }
  return $out1;
}
