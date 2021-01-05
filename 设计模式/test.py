from 设计模式.singletest import test1
if __name__ == "__main__":
    x = test1.a
    y = test1.a
    print(id(x),id(y))

