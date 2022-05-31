
def GetMemebers(
        cls: type,
        attrs: set[str]
        ) -> None:
    for attr in dir(cls):
        attrs.add(attr)
    for base in cls.__bases__:
        GetMemebers(base, attrs)



if __name__ == '__main__':
    module = input('Enter the module of the type: ')
    clsName = input('Enter the class (type) name: ')
    cls = exec(compile(
        f'import {module};{module}.{clsName}',
        '<string>',
        'single'))

    attrs: set[str] = set()
    GetMemebers(cls, attrs)

    attrs = list(attrs)
    attrs.sort()

    print('All attributes:')
    for attr in attrs:
        print(attr)
