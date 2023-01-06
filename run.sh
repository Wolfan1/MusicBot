echo "Running discord music bot."
ret=1

while [ $ret -ge 1 ]
do
  python3 bot.py
  ret=$?
done
