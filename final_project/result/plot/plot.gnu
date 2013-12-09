
reset
set title "Round-trip time measurement for gaming services \n (smaller is better)"
set key inside top right box
set xlabel ""
set ylabel "RTT (ms)"
set yrange [0:260]
set output "game-server-rtt.eps"
#set y2tics nomirror tc lt 6

set terminal eps

set xrange [-0.25:10.00]
set xtic rotate by -45
set boxwidth 0.25
plot 'game-value-client' using ($0-.05):3:5:xtic(1) with boxerrorbars title "UE - server RTT",\
     'game-value-pgw' using ($0+0.25):3:5 with boxerrorbars title "PGW - server RTT"



reset
set title "Round-trip time measurement for streaming services \n (smaller is better)"
set key inside top right box
set xlabel ""
set ylabel "RTT (ms)"
set yrange [0:90]
set output "streaming-server-rtt.eps"
#set y2tics nomirror tc lt 6

set terminal eps

set xrange [-0.1:6]
set xtic rotate by -45
set boxwidth 0.25
plot 'stream-value-client' using ($0-.05):3:5:xtic(1) with boxerrorbars title "UE - server RTT",\
     'stream-value-pgw' using ($0+0.25):3:5 with boxerrorbars title "PGW - server RTT"
