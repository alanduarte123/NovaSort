<?php
require 'nova_super.php';
$d = json_decode(file_get_contents('/tmp/cross.json'), true);
$a = $d['a']; $exp = $d['exp'];
$res = nova_super($a);
$ok = true;
for($i=0;$i<count($res);$i++){
  if($res[$i] != $exp[$i]){ $ok=false; echo "bad $i\n"; break; }
}
if($ok) echo "ok\n";
