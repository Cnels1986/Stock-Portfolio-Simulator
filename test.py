from app import app
import unittest

def login(client, username, password):
    return client.post('/login', data=dict(username=username,password=password), follow_redirects=True)
def logout(client):
    return client.get('/logout', follow_redirects=True)

# def test_login_logout(client):



class FlaskTestCase(unittest.TestCase):
    def test_login_route(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    def test_register_route(self):
        tester = app.test_client(self)
        response = tester.get('/register', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    # def test_logout_route(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/logout', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)
    # def test_admin_route(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/admin', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)
    # def test_sell_route(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/sell', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)
    # def test_buy_route(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/buy', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)
    # def test_confirm_route(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/confirm ', content_type='html/text')
    #     self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
