import app

def test_things():
    app.do_things('nothing')

def test_main():
    status = app.main()
    assert status == 'Everything is alright'
