# MacBook dGPU Disabler/Enabler
Some MacBook models from 2010 to 2013 may experience issues with the dedicated GPU, ranging from graphical errors to a completely black screen. The definitive solution would be to replace the graphics chip. However, there is another option, and here's how I present it: there are some GRUB commands that allow you to disable the dedicated GPU via software. This may not be the definitive solution, but it's a good temporary solution.

Some of the errors that may occur are the following:
![](https://github.com/niko-forte/macbook-dgpu/blob/main/image-000.png)

You can use this small Python code I created to disable the dedicated GPU. You can clone it with the command
<pre> git clone https://github.com/niko-forte/macbook-dgpu </pre>
And then run it on the terminal and run these commands.
<pre>cd macbook-dgpu
sudo python3 no_dGPU.py</pre>
All you have to do is follow the on-screen instructions.
![](https://github.com/niko-forte/macbook-dgpu/blob/main/image-002.png)
