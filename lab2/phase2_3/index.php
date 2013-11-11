<?php
function downloadFile ($url, $path) {
  echo "Downloading file $url to $path"
  $newfname = $path;
  $file = fopen ($url, "rb");
  if ($file) {
    $newf = fopen ($newfname, "wb");

    if ($newf)
    while(!feof($file)) {
      fwrite($newf, fread($file, 1024 * 8 ), 1024 * 8 );
    }
  }

  if ($file) {
    fclose($file);
  }

  if ($newf) {
    fclose($newf);
  }
}
downloadFile("/users/binh6480/Downloads","http://www.cs.utah.edu/~binh/archive/a.mo");
?>
