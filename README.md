# 使用方法:

源代码: 

[https://github.com/MrXnneHang/face-detect-system/tree/master](https://github.com/MrXnneHang/face-detect-system/tree/master)

## 环境准备：

* docker

* mysql
* python-env

**docker&mysql**

docker 和 mysql 可以参考我之前发的。

[Windows使用docker安装和使用MYSQL](http://xnnehang.top/blog/50)

注意你需要先像那个例子中，创建一个数据库叫faces，后面我们会在代码中连接它。

例子中将数据库映射到 D:\iso\mysql 中来持久化保存，**如果你没有D盘，请考虑更改到别处**。在"启动MYSQL容器"的板块中。

以及每次要运行代码，都需要保持数据库的打开(docker的后台运行)。

**python-env**

[requirements.txt](https://github.com/MrXnneHang/face-detect-system/blob/master/requirements.txt)

上面是requirements.如果要安装cpu版本，直接:

```cmd
pip install -r requirements.txt
```

如果要安装cuda版本，则先将requirements.txt中的 torch,torchvision注释。

这是更新后的 requirements.txt:

```cmd
# torch == 2.2.2
# torchvision == 0.17.2
facenet_pytorch == 2.6.0
pyaml
pyqt5
PyQt5-Frameless-Window
opencv-python
PyQt-Fluent-Widgets[full]
mysql-connector-python
```



然后参考:

[pip使用清华源来安装指定版本的 pytorch-cuda](http://xnnehang.top/blog/54)

单独安装完后再次:

```cmd
pip install -r requirements.txt
```



## 运行方法:



在你部署好的 python env 中，并且保证 docker 在后台运行了 Mysql ，那么就可以直接。
```cmd
python demo.py
```



## 效果:

主窗口:

![Snipaste_2024-07-11_20-15-23](https://image.baidu.com/search/down?url=https://img1.doubanio.com/view/photo/l/public/p2910501358.webp)

录入窗口:

![Snipaste_2024-07-11_20-16-06](https://image.baidu.com/search/down?url=https://img1.doubanio.com/view/photo/l/public/p2910501360.webp)

**注意**你每次删除和录入人员，都需要**点击更新模型才会生效**。

这里因为会涉及隐私，就没有打开摄像头。在录入的时候在点击确定前记得摆好pos。

你可以在 config.yml 中修改你想要的背景图片，和运行的 设备( cpu / cuda ) 。



留下这个，可能以后学弟会碰到。也希望学弟能在这个基础上更进一步。我刚学 pyqt 也只能说插点图片，设点 button ， 希望以后的人能在这个基础上玩点花的。我下次再要写 GUI 应用的时候也能在这个基础上玩点花的。但我一般 webui 写得多，主打的是方便修改。

我记得我在学 C++ 的时候那个人说教人用 Qt 的都是坑人的，真的要写 UI 要写自己的库。我在写的时候也有瞬间有个念头，快大三了我还在玩泥巴，真的有救吗。但后来想想，玩的开心就好，要想走全栈，什么都值得玩一遍。


## 原理：

使用的并非分类模型而是**特征提取模型**。

因为考虑到应用场景，每个人可能只会录入一张照片而非多张。以及使用的模型是 vggfacenet2， 整体的模型参数和 resnet18 差不多，但是在预训练好的情况下，性能和效果都相当不错。

**录入**:

* 录入照片，保存本地
* 计算脸部特征向量，存入数据库

**识别**:

* 加载数据库中所有用户的脸部特征向量 target
* 计算摄像头捕获到的人脸的特征向量 input
* 计算 input 和 target 之间的相似度
* 如果相似度和 userA  高于某个阈值，认为输入人脸是 userA 。
* 如果所有相似度都低于某个阈值，认为这个人不是 users 中的一员。

# 碰到的bug以及优化:

## 1.摄像头初始化耗时过长：

```python
self.camera = cv2.VideoCapture(0) 
```

这个摄像头的初始化大概需要两三秒，而不少 button 直接和摄像头打交道。我不能忍受点击一个 button 后要等待四五秒。所以就把摄像头在运行程序的时候初始化，然后把这个摄像头全局地传递使用，就不需要反复初始化。

## 2.加载模型的时间过长：

同理我也是开了一个线程在后台加载模型，当运行程序后时候后台直接加载，而并不是等到使用到模型了再等它加载四五秒。