from mnist.worker import prediction

def test_prediction():
    r = prediction(file_path='a/b/c/d.png', num=1)
    assert r in range(10)


