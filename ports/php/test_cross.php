<?php
require 'nova_super.php';
function main(){
  $a = [];
  $seed = 2026;
  $x = $seed % 2147483647;
  if($x <= 0) $x += 2147483646;
  for($i=0;$i<5000;$i++){
    $x = ($x * 48271) % 2147483647;
    $val = floor(($x-1)/(2147483647-1) * 10000000);
    $a[] = $val;
  }
  $exp = $a;
  sort($exp, SORT_NUMERIC);
  $res = nova_super($a);
  for($i=0;$i<count($res);$i++){
    if($res[$i] != $exp[$i]){ echo "bad\n"; return; }
  }
  echo "ok\n";
}
main();
