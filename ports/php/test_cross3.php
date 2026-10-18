<?php
require 'nova_super.php';
$a = [];
$seed = 2026;
$x = $seed % 2147483647;
if ($x <= 0) $x += 2147483646;
for ($i = 0; $i < 5000; $i++) {
  $x = ($x * 48271) % 2147483647;
  $r = ($x - 1.0) / (2147483647.0 - 1.0);
  $val = intval(round($r * 10000000.0));
  $a[] = $val;
}
$exp = $a;
sort($exp, SORT_NUMERIC);
$res = nova_super($a);
$ok = true;
for($i=0;$i<count($res);$i++){
  if($res[$i] != $exp[$i]){ $ok=false; echo "bad $i\n"; break; }
}
if($ok) echo "ok\n";
