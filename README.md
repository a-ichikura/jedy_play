# Jedyでペイントを行う[WIP]
## 実行方法
M5 stick plus cとserial通信を開始
```
rosrun rosserial_python serial_node.py _port:=/dev/ttyUSB0 _baud:=115200
```
Pythonコードで実行
```
cd scripts
python main.py
## low, middle, high のいずれかを打ち込むと動作するはず
```

##動き方
### LOW
1.スタート\n
2.LEDが白く光る\n 
3.音がなる (Help!)\n
4.LEDがほしい絵の具の色に光る（ランダム、赤、青、緑）\n
5.ロボットの手をとって絵の具をつける\n
6.ボタンを押す\n
7.音がなる（Ready!)\n
8.ロボットの手をとって絵を描く(10秒間)\n
9.音がなる(Joy!)\n
10.終了（LED消灯)\n

### Middle
1.スタート
2.LEDが白く光る 
3.音がなる (Help!)
4.LEDがほしい絵の具の色に光る（ランダム、赤、青、緑）
5.ロボットの手をとって絵の具をつける
6.ボタンを押す
7.音がなる（Ready!)
8.ロボットがひとりでに描き出す
9.音がなる(Joy!)
10.終了（LED消灯）

### High
1.スタート
2.LEDが白く光る 
3.音がなる (Help!)
4.LEDがほしい絵の具の色に光る（ランダム、赤、青、緑）
5.ロボットが絵の具に手を伸ばす
7.音がなる（Ready!)
8.ロボットがひとりでに描き出す
9.音がなる(Joy!)
10.終了（LED消灯）
