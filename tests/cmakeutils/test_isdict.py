from cmakeutils.typecheck import isdict

def test_isdict():
    results = []

    v1 = 0
    v2 = {}
    v3 = {'str': None}
    v4 = {None: 'str'}
    v5 = {'a': 1}
    v6 = {'a': 1, 'b': 'c'}

    results = [
        not isdict(v1, str, int),
        isdict(v2, str, int),
        isdict(v3, str, int),
        not isdict(v4, str, int),
        isdict(v5, str, int),
        not isdict(v6, str, int)
    ]

    result = list(set(results))[0]

    assert result
