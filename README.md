# Python-Django-商城

## 页面
1. 商品相关
    1. 首页
    2. 列表页
    3. 详情页
2. 购物车相关
    1. 购物车页
3. 订单相关
    1. 提交订单页
    2. 订单评论页
4. 用户相关
    1. 注册页
    2. 登录页
    3. 用户中心-信息页
    4. 用户中心-订单页
    5. 用户中心-地址页


## 技术栈
1. python
2. django
3. mysql
4. redis
5. celery
6. nginx
7. gunicorn
8. supervisord
9. 发邮件
10. 支付宝支付


## 部署
1. 配置文件更新
    ```
    cp shop/settings.py.bak shop/settings.py
    vim shop/settings.py
    <!-- 补充相应mysql/redis/邮箱/支付宝信息 -->
    ```
2. 运行环境安装
    ```
    python3.9 -m venv venv
    source venv/bin/activate
    pip3.9 install -r requirements.txt
    ```
3. 依赖安装
    ```sh
    <!-- mysql -->
    mysql -hxxx.xxx.xxx.xxx -uroot -p
    create database db_shop

    <!-- redis -->
    wget http://download.redis.io/releases/redis-7.2-rc2.tar.gz
    tar -zxvf redis-7.2-rc2.tar.gz
    cd redis-7.2-rc2
    make
    cd src
    make install

    <!-- nginx -->
    yum -y install nginx
    ```
4. 启动项目
    ```
    supervisord -c /root/shop/dependent/supervisor.conf
    ```

# REFERENCE
[天天生鲜Django项目](https://www.bilibili.com/video/BV1vt41147K8?p=1&vd_source=1a98bca050ed6f7b5382a8bcbafd0b04)