import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_add_entry(self):
        rv = self.app.post('/add', data=dict(
            title='Test Entry',
            text='Test Content',
            category='Test Category'
        ), follow_redirects=True)
        assert b'Test Entry' in rv.data
        assert b'Test Content' in rv.data
        assert b'Test Category' in rv.data

    def test_edit_entry(self):
        self.app.post('/add', data=dict(
            title='Test Title',
            text='Test Text',
            category='Test Category'
        ), follow_redirects=True)
        rv = self.app.post('/edit/1', data=dict(
            title='Updated Title',
            text='Updated Text',
            category='Updated Category'
        ), follow_redirects=True)
        assert b'Updated Title' in rv.data
        assert b'Updated Text' in rv.data
        assert b'Updated Category' in rv.data

    def test_delete_entry(self):
        self.app.post('/add', data=dict(
            title='To be deleted',
            text='Delete this entry',
            category='Delete Category'
        ), follow_redirects=True)
        rv = self.app.post('/delete/1', follow_redirects=True)
        assert b'To be deleted' not in rv.data

if __name__ == '__main__':
    unittest.main()