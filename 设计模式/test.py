from 设计模式.singletest import test1
def a():
    return 1,2
if __name__ == "__main__":
    x = test1.a
    y = test1.a
    print(id(x),id(y))
    a,b = a()
    print(a,b)

